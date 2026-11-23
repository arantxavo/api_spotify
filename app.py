from flask import Flask, request

app = Flask(__name__)

# Consulta raíz
@app.route("/")
def hello():
    return "Bienvenid@ al gestor de preferencias musicales"

USUARIOS = []
CLIENT_ID = ef6807ab3e644ad1bd096b0b6105eade
CLIENT_SECRET = a04c4a1c39b44d8ea776a0cab19d2d0a


# Leer usuarios
@app.route("/usuarios")
def leer_usuarios():
    global USUARIOS
    return {"usuarios": USUARIOS}


# Dar de alta nuevo usuario
@app.route("/alta_usuario", methods=["POST"])
def alta_usuario():
    global USUARIOS

    usuario_nuevo = request.get_json()
    nuevo_id = max((usuario["id"] for usuario in USUARIOS), default = 0) + 1 # Coge el ID mayor y suma 1 (IA)
    nuevo_usuario = {
        "id": nuevo_id, 
        "nickname": usuario_nuevo["nickname"],
        "nombre": usuario_nuevo["nombre"],
    }
    
    if not usuario_nuevo["nombre"]:
        return {
                "error": "El nombre no puede estar vacío",
            }, 400
    if not usuario_nuevo["nickname"]:
        return {
                "error": "El nickname no puede estar vacío",
            }, 400

    for usuario in USUARIOS:
        if nuevo_usuario["nickname"] == usuario["nickname"]:
            return {
                "message": "Ese usuario ya existe",
            }, 400

    USUARIOS.append(nuevo_usuario)

    return {
        "message": "Usuario añadido con éxito",
    }, 201


# Eliminar un usuario
@app.route("/eliminar", methods=["DELETE"])
def eliminar_usuario():
    global USUARIOS
    nickname = request.args.get("nickname")

    for usuario in USUARIOS:
        if usuario["nickname"] == nickname:
            USUARIOS.remove(usuario)
            return {
                "message": f"Usuario {usuario["nickname"]} eliminado con éxito"
            }, 200

    return {"message": "Usuario no encontrado"}, 404


# Actualizar un usuario
@app.route("/actualizar/<nickname>", methods=["PUT"])
def actualizar_usuario(nickname):
    global USUARIOS
    nombre = request.args.get("nombre")

    for usuario in USUARIOS:
        if usuario["nickname"] == nickname:
            usuario["nombre"] = nombre
            return { 
                "message": f"Usuario {usuario["nickname"]} actualizado con éxito"
            }, 200

    return {"message": "Usuario no encontrado"}, 404 


# Guardar preferencias musicales
@app.route("/gustos_musicales/<nickname>", methods=["PATCH"])
def guardar_gustos_musicales(nickname):
    global USUARIOS

    gustos_musicales = request.get_json()

    for usuario in USUARIOS:
        if usuario["nickname"] == nickname:
            usuario["gustos_musicales"] = {
                "artistas": [],
                "generos": []
            }

            usuario["gustos_musicales"]["artistas"].extend(gustos_musicales["artistas"])
            usuario["gustos_musicales"]["generos"].extend(gustos_musicales["generos"])
            
            return { 
                "message": f"Preferencias musicales del usuario {usuario["nickname"]} guardadas con éxito"
            }, 200

    return {"message": "Usuario no encontrado"}, 404     


# SPOTIFY
# Función para obtener el token, pasandole el id y la passw y formatearlo
def obtener_token():
    url = "https://accounts.spotify.com/api/token"

    response = request.posts(
        url,
        data ={"grant_type": "client_credentials"},
        auth = {CLIENT_ID, CLIENT_SECRET}
    )


    if response.status_code != 200:
        return {
            "message": "Error al obtener el token."
        }, 404

    return {
       "Authorization": f"Bearer {response.json()["access_token"]}"
    }



# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
