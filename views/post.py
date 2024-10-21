import os
import requests
import uuid
from datetime import datetime, timezone
from dateutil import parser
from marshmallow import ValidationError
from db import db
from flask import Blueprint, request, Response, jsonify, g, abort
from flask.views import MethodView
from .util import class_route, create_error_response
from .schemas.post_schemas import CreatePostSchema, ErrorResponseSchema, ResetPostsResponseSchema
from models import Post
import re

blp = Blueprint("Post", __name__)

USERS_PATH = os.getenv('USERS_PATH')
url_users = f'{USERS_PATH}/users/me'


# url_users = 'http://localhost:8010/users/me'


def is_valid_uuid(uuid_to_test):
    """
    Comprueba si uuid_to_test es un UUID válido en formato de cadena.
    """
    regex = r'[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}'
    match = re.match(regex, uuid_to_test)
    return bool(match)


@blp.before_request
def verify_token():
    token = request.headers.get('Authorization')

    if not token:
        error = {"msg": "Token is required"}
        return Response(ErrorResponseSchema().dumps(error), status=403)

    headers = {'Authorization': token}
    response = requests.get(url_users, headers=headers)

    if response.status_code == 401:
        # Token is invalid or expired
        error = {"msg": "Invalid or expired token"}
        return Response(ErrorResponseSchema().dumps(error), status=401)
    elif response.status_code != 200:
        # Error while verifying token
        error = {"msg": response.text}
        return Response(ErrorResponseSchema().dumps(error), status=response.status_code)

    # Token is valid, save user id
    user_data = response.json()
    g.user_id = user_data['id']


@class_route(blp, "/posts", methods=['POST', 'GET'])
class PostsView(MethodView):

    def post(self):
        try:
            # Extraer datos del request
            route_id = request.json.get('routeId')
            expire_at = request.json.get('expireAt')
            created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

            # Organizar expireAt
            expire_at = parser.parse(expire_at)
            expire_at = expire_at.replace(tzinfo=timezone.utc)
            expire_at = expire_at.replace(microsecond=0).isoformat()

            # Validar el esquema de entrada
            data = CreatePostSchema().load({
                'routeId': route_id,
                'userId': g.user_id,  # Se obtiene del token 'Authorization
                'expireAt': expire_at,
                'createdAt': created_at
            })

            # Verificar que la fecha de expiración sea mayor a la fecha de creación
            if data['expireAt'] <= data['createdAt']:
                error = {"msg": "La fecha expiración no es válida"}
                return jsonify(error), 412

            # Crear el post
            new_post = Post(
                id=str(uuid.uuid4()),
                routeId=data['routeId'],
                userId=data['userId'],
                expireAt=data['expireAt'],
                createdAt=data['createdAt']
            )
            db.session.add(new_post)
            db.session.commit()

            # Respuesta exitosa
            response_data = {
                "id": new_post.id,
                "userId": new_post.userId,
                "createdAt": new_post.createdAt.isoformat(),
            }
            return jsonify(response_data), 201

        except ValidationError as e:
            # Datos inválidos (400)
            error = {"msg": f"Datos invalidos, error(es): {e.messages}", "errors:": e.messages}
            return Response(ErrorResponseSchema().dumps(error), status=400)

        except Exception as e:
            # Error interno (500)
            error_response = create_error_response(e)
            return jsonify(error_response), 500

    def get(self):
        # Validar que no se pasen parametros inesperados
        valid_params = ['expire', 'route', 'owner']
        if any(param not in valid_params for param in request.args):
            error = {"msg": "Solicitud contiene parámetros inesperados."}
            return Response(ErrorResponseSchema().dumps(error), status=400)

        # Extraer parámetros de la consulta
        expire_filter = request.args.get('expire', type=str)
        route_id = request.args.get('route', type=str)
        owner = request.args.get('owner', type=str)

        # Validar que el routeId sea un UUID válido
        if route_id and not is_valid_uuid(route_id):
            error = {"msg": "Valor inválido para el parámetro \'route\'."}
            return Response(ErrorResponseSchema().dumps(error), status=400)

        # Validar que el expire sea 'true' o 'false'
        if expire_filter and expire_filter.lower() not in ['true', 'false']:
            error = {"msg": "Valor inválido para el parámetro \'expire\'."}
            return Response(ErrorResponseSchema().dumps(error), status=400)

        # Iniciar la consulta
        query = Post.query

        # Filtrar por roiuteId si se proporciona
        if route_id:
            query = query.filter_by(routeId=route_id)

        # Filtrar por userId si se proporciona
        if owner:
            if owner == 'me':
                owner = g.user_id
            query = query.filter_by(userId=owner)

        # Filtrar por estado de expericacion si se proporciona
        if expire_filter is not None:
            if expire_filter.lower() == 'true':
                query = query.filter(Post.expireAt < datetime.now(timezone.utc))
            elif expire_filter.lower() == 'false':
                query = query.filter(Post.expireAt >= datetime.now(timezone.utc))

        # Ejecutar la consulta y obtener los resultados
        posts = query.all()

        # Formatear y devolver los resultados
        results = [{
            "id": post.id,
            "routeId": post.routeId,
            "userId": post.userId,
            "expireAt": post.expireAt.isoformat(),
            "createdAt": post.createdAt.isoformat()
        } for post in posts]

        return jsonify(results), 200


@class_route(blp, "/posts/<string:id>", methods=['GET', 'DELETE'])
class PostView(MethodView):

    def get(self, id): # Error con el 404
        # Validar que el id sea un UUID válido
        if not is_valid_uuid(id):
            error = {"msg": "Valor inválido para el parámetro \'id\'."}
            return Response(ErrorResponseSchema().dumps(error), status=400)

        # Buscar el post
        post = Post.query.get_or_404(id, description="Publicación no encontrada.")

        # Si la publicación existe, retornarla
        result = {
            "id": post.id,
            "routeId": post.routeId,
            "userId": post.userId,
            "expireAt": post.expireAt.isoformat(),
            "createdAt": post.createdAt.isoformat()
        }
        return jsonify(result), 200

    def delete(self, id):
        # Validar que el id sea un UUID válido
        if not is_valid_uuid(id):
            error = {"msg": "Valor inválido para el parámetro \'id\'."}
            return Response(ErrorResponseSchema().dumps(error), status=400)

        # Buscar el post
        post = Post.query.get_or_404(id, description="Publicación no encontrada.")

        # Eliminar la publicación
        db.session.delete(post)
        db.session.commit()

        # Respuesta exitosa
        response = {"msg": "la publicación fue eliminada"}
        return jsonify(response), 200

