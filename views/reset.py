from flask import Blueprint, Response
from flask.views import MethodView
from .schemas.post_schemas import ResetPostsResponseSchema
from models import Post
from .util import class_route
from db import db

blp = Blueprint("Reset Database", __name__)


@class_route(blp, "/posts/reset")
class PostReset(MethodView):
    init_every_request = False

    def post(self):
        db.session.query(Post).delete()
        db.session.commit()
        response_data = {"msg": "Todos los datos fueron eliminados"}
        return Response(ResetPostsResponseSchema().dumps(response_data), status=200, mimetype='application/json')