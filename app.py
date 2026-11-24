from flask import Flask, request
import requests
import os 
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Consulta raíz
@app.route("/")
def hello():
    return "Bienvenid@ al gestor de preferencias musicales"

USUARIOS = []
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


# Endpoint para leer usuarios
@app.route("/usuarios")
def leer_usuarios():

    return {"usuarios": USUARIOS}


# Enpoint para dar de alta nuevo usuario
@app.route("/alta_usuario", methods=["POST"])
def alta_usuario():

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


# Endpoint para eliminar un usuario
@app.route("/eliminar", methods=["DELETE"])
def eliminar_usuario():

    nickname = request.args.get("nickname")

    for usuario in USUARIOS:
        if usuario["nickname"] == nickname:
            USUARIOS.remove(usuario)
            return {
                "message": f"Usuario {usuario["nickname"]} eliminado con éxito"
            }, 200

    return {"message": "Usuario no encontrado"}, 404


# Endpoint para actualizar un usuario
@app.route("/actualizar/<nickname>", methods=["PUT"])
def actualizar_usuario(nickname):

    nombre = request.args.get("nombre")

    for usuario in USUARIOS:
        if usuario["nickname"] == nickname:
            usuario["nombre"] = nombre
            return { 
                "message": f"Usuario {usuario["nickname"]} actualizado con éxito"
            }, 200

    return {"message": "Usuario no encontrado"}, 404 


# Endpoint para guardar o actualizar preferencias musicales
@app.route("/gustos_musicales/<nickname>", methods=["PATCH"])
def guardar_gustos_musicales(nickname):

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



# Función para obtener el token, pasandole el id y la passw y formatearlo
def obtener_token():
    url = "https://accounts.spotify.com/api/token"

    response = requests.post(
        url,
        data ={"grant_type": "client_credentials"},
        auth = (CLIENT_ID, CLIENT_SECRET)
    )

    if response.status_code != 200:
        return {
            "message": "Error al obtener el token."
        }, 404

    return response.json()["access_token"]



# Función para obtener los id's de los artistas del usuario
def obtener_idartista(token, artista):

    response = requests.get(
        "https://api.spotify.com/v1/search",
        params={
            "q": artista,
            "type": "artist",
            "limit": 1
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    return response.json()["artists"]["items"][0]["id"]
    

# Endpoint que obtiene información sobre los artistas de un usuario
@app.route("/obtener_info_artistas/<nickname>")
def obtener_info_artistas(nickname):

    discografia = []

    token = obtener_token()

    for usuario in USUARIOS:
        if usuario["nickname"] == nickname:
            if "gustos_musicales" not in usuario:
                return {"message": f"El usuario {nickname} no tiene preferencias musicales guardadas"}, 404 
            for artista in usuario["gustos_musicales"]["artistas"]:
                id_artista = obtener_idartista(token, artista)
                albumes = []
                response = requests.get(
                    f"https://api.spotify.com/v1/artists/{id_artista}/albums",
                    params={
                        "include_groups": "album",
                        "market": "ES",
                    },
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )       

                if response.status_code == 429:
                    return {
                        "message": "Has enviado muchas peticiones. Espera un rato para volver a intentarlo."
                    }, 429
                
                for item in response.json()["items"]:
                    nuevo_album = {
                        "título": item["name"], 
                        "fecha_lanzamiento": item["release_date"],
                        "nº canciones": item["total_tracks"]
                    }
                    albumes.append(nuevo_album)

                discografia.append(
                    {
                        "artista" : artista,
                        "albumes": albumes
                    }
                )
                          
            return discografia, 200

        return {
            "message": "No existe ese usuario."
        }, 404
    

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
