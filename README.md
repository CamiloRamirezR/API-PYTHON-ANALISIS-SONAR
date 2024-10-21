# Gestión de Publicaciones
El servicio de gestión de publicaciones permite crear, buscar, eliminar y consultar publicaciones.

## Índice
1. [Estructura](#estructura)
2. [Ejecución](#ejecución)
3. [Uso](#uso)
4. [Pruebas](#pruebas)
5. [Autor](#autor)

## Estructura
```
├── models # Contiene los modelos de datos de la aplicación. Estos modelos representan las entidades de la base de datos y su estructura.
│
├── tests # Aquí se encuentran las pruebas unitarias de la aplicación.
│
├── views # Contiene los blueprints, que son colecciones de rutas relacionadas en la aplicación.
│   |── schemas # Contiene los esquemas para validar y serializar datos.
│   └── util.py # Archivo que contiene funciones auxiliares utilizadas en las vistas de la aplicación.
│
├── app.py # Archivo principal de la aplicación.
|
├── db.py # Archivo que contiene el objeto DB de SQLAlchemy para ejecutar queries.
|
├── .coveragerc # Archivo que contiene la configuración de coverage.py, la herramienta para la medición de la cobertura de código
|
├── Dockerfile # Archivo que contiene instrucciones para construir la imagen de Docker.
|
├── requirements.txt # Archivo que especifica las dependencias de Python necesarias para ejecutar la aplicación.
|
└── README.md # usted está aquí
```

## Ejecución
### Prerequisitos
1. La aplicación para la _Gestión de usuarios_ debe estar en funcionamiento, ya que la aplicación actual se comunica con ella para verificar el token del usuario.
2. Debe estar corriendo una base de datos Postgres.

**Nota**: Se puede ejecutar una base de datos de Postgres con Docker ejecutando:
```bash
docker run --name postgres-user -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=post -p 5432:5432 -d postgres:15
```

### Ejecutar con Docker
1. Instalar [Docker](https://docs.docker.com/get-docker/) si aun no has instalado
2. Ubicarse en la carpeta raíz de la aplicación
3. Construir el contenedor:
```bash
docker build -t misw4301-post:entrega1 .
```
4. Correr la aplicación con:
```bash
docker run --rm -it -e USERS_PATH=<USERS_PATH> -e DB_USER=<DB_USER> -e DB_PASSWORD=<DB_PASSWORD> -e DB_HOST=<DB_HOST> -e DB_PORT=<DB_PORT> -e DB_NAME=<DB_NAME> -p 8011:8000 misw4301-post:entrega1
```
Asegurarse de reemplazar:
- `<USERS_PATH>` con la URL donde se está ejecutando la aplicación de _Gestión de usuarios_.
- `<DB_USER>` con el usuario de la base de datos de Postgres.
- `<DB_PASSWORD>` con la contraseña de la base de datos de Postgres.
- `<DB_HOST>` con el host de la base de datos de Postgres.
- `<DB_PORT>` con el puerto de la base de datos de Postgres.
- `<DB_NAME>` con el nombre de la base de datos de Postgres.

**Se puede acceder a la aplicación en:** http://127.0.0.1:8011/

### Ejecutar local sin Docker
1. Instalar Python 3.9+ si aun no has instalado
2. Ubicarse en la carpeta raíz de la aplicación y crear un entorno virtual de python.
```bash
python -m venv venv
```
3. Activar el entorno virtual.
```bash
# Ejemplo en Windows
.\venv\Scripts\activate
```
```bash
# Ejemplo en Unix/MacOS
source venv/bin/activate
```
4. Instalar las dependencias.
```bash
pip install -r requirements.txt
```
4. Configurar los siguientes variables de entorno:
- `USERS_PATH` con la URL donde se está ejecutando la aplicación de _Gestión de usuarios_.
- `DB_USER` con el usuario de la base de datos de Postgres.
- `DB_PASSWORD` con la contraseña del usuario de la base de datos de Postgres.
- `DB_HOST` con el host de la base de datos de Postgres.
- `DB_PORT` con el puerto de la base de datos de Postgres.
- `DB_NAME` con el nombre de la base de datos de Postgres.

En entornos Windows, utiliza el comando set para definir las variables del entorno con el valor correspondiente:
-   `set USERS_PATH=<USERS_PATH>`
-   `set DB_USER=<DB_USER>`
-   `set DB_PASSWORD=<DB_PASSWORD>`
-   `set DB_HOST=<DB_HOST>`
-   `set DB_PORT=<DB_PORT>`
-   `set DB_NAME=<DB_NAME>`

Mientras que en entornos Unix/MacOS, utiliza el comando export para establecer las variable del entorno con el valor correspondiente:
-   `export USERS_PATH=<USERS_PATH>`
-   `export DB_USER=<DB_USER>`
-   `export DB_PASSWORD=<DB_PASSWORD>`
-   `export DB_HOST=<DB_HOST>`
-   `export DB_PORT=<DB_PORT>`
-   `export DB_NAME=<DB_NAME>`

Se debe asegurar estos cambios antes de ejecutar la aplicación para garantizar una correcta conexión con la base de datos de Postgres.

5. Correr la aplicación con:
```bash
flask run -p 8011
```

**Se puede acceder a la aplicación en:** http://127.0.0.1:8011/

**Nota**: En un entorno de desarrollo la aplicación también puede correr con una base de datos SQLite sin necesidad de tener una base de datos Postgres corriendo. **Este modo no está soportado oficialmente**.
```bash
flask --app "app:create_app('sqlite:///db.sqlite')" run -p 8011
```

## Uso
Para obtener instrucciones detalladas sobre cómo utilizar el proyecto y consumir la API es recomendable visitar el siguiente [enlace](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/proyecto-202411/wiki/Gesti%C3%B3n-de-Publicaciones). Allí encontrará una guía completa que muestra detalles de como realizar las siguientes acciones:

- Creación de publicación
- Ver y filtrar publicaciones
- Consultar una publicación
- Eliminar publicación
- Consulta de salud del servicio
- Restablecer base de datos

Puede consumir estos endpoints usando Postman, por ejemplo:

![image](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202411-proyecto-grupo19/assets/1379478/7fec7024-266a-4680-926b-8a54044a88a5)

Donde `{{POSTS_PATH}}` es el host donde está corriendo la aplicación (ej: 127.0.0.1:8011).

Es crucial tener presente que, para cualquier solicitud, exceptuando las de /reset y /ping, resulta imprescindible incluir el token de usuario. Por ende, la aplicación de _Gestión de usuarios_ debe estar operativa, dado que la aplicación actual depende de ella para autenticar el token del usuario.

![image](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202411-proyecto-grupo19/assets/1379478/078f6a2c-2f0e-4dc6-b90a-9423df10c3f0)

## Pruebas
Para ejecutar las pruebas, primero asegúrese de haber completado los pasos del 1 al 3 de la sección [Ejecutar local sin Docker](#ejecutar-local-sin-docker), luego proceda a ejecutar los siguientes comandos:
```bash
coverage run
coverage report
```

Se puede crear un reporte de cobertura en HTML con
```bash
coverage html
```
El reporte está en la carpeta `htmlcov`.

## Autor
**Nombre:** Camilo Ramírez Restrepo  
**Correo:** c.ramirezr2@uniandes.edu.co  
**GitHub:** [CamiloRamirezR](https://github.com/CamiloRamirezR)
