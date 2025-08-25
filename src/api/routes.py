"""
Este módulo se encarga de inicializar el servidor API, cargar la Base de Datos y añadir los Endopoints
"""
import datetime
from decimal import Decimal
import os
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Space, Booking, Payment
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


# Registrar el blueprint
api = Blueprint('api', __name__)
# app.register_blueprint(api, url_prefix='/api')  ---> ESTÁ EN "app.py"


##################################################
### CORS implementación
CORS(api) # Permite peticiones CORS hacia esta API
##################################################

# Configurar JWT ??? ---> está configurado en "app.py"


#############################################
## Endpoint de ejemplo
@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "msg": "¡Hola! Soy un mensaje del backend. Revisa la pestaña de red en Google Inspector y verás la solicitud GET"
    }
    return jsonify(response_body), 200
#############################################




#########################################################################################
#########################################################################################
#############                        WEPLACEIT                              #############
#############                      Rental Platform                          #############
#############                         REST API                              #############
#############                        Endpoints                              #############
#########################################################################################
#########################################################################################




############################################
#######     SIGN-UP (registrarse)    #######
############################################
""" JSON de registro de usuario:
{ 
    "first_name": "first_name_example",
    "last_name":  "last_name_example",
    "username":   "username_example",
    "email":      "example@email.com", 
    "password":   "example_password"
}
"""
@api.route('/signup', methods=['POST'])
def signup():

    try:
        # Se reciben los datos
        data = request.get_json()
        
        first_name = data.get("first_name")
        last_name  = data.get("last_name")
        username   = data.get("username")
        email      = data.get("email")
        password   = data.get("password")


        # Manejo de falta de datos
        if not first_name or not last_name or not username or not email or not password:
            return jsonify({ "error": "Todos los campos son obligatorios." }), 400
        
        # LÓGICA SIMILAR PARA VALIDAR CAMPOS
        # required_fields = ['email', 'username', 'first_name', 'last_name', 'password']
        # for field in required_fields:
        #     if not data.get(field):
        #         return jsonify({'error': f'"{field}" es requerido para el registro'}), 400
        
        # Revisar si el correo ya existe
        if User.query.filter_by(email=email).first():
            return jsonify({ "error": "Este correo electrónico ya está registrado." }), 400
        
        # Revisar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Este nombre de usuario ya está registrado.'}), 400


        # Se encripta la contraseña
        hashed_password = generate_password_hash(password)


        # Se crea el nuevo usuario en la base de datos
        new_user = User( email=email,
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        password=hashed_password,
                        is_active=True)

        db.session.add(new_user)
        db.session.commit()


        return jsonify({
            "msg": "Usuario creado correctamente",
            "Nuevo usuario": new_user.serialize() 
        }), 201
    
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


############################################
#######    LOG-IN (iniciar sesión)   #######
############################################
""" JSON request body para Log-in:
{
    "email":    "email@ejemplo.com",
    "password": "tu_contraseña"
}
"""
@api.route('/login', methods=['POST'])
def handle_login():

    try:
        # Se reciben los datos (correo y contraseña)
        data = request.get_json()
        email    = data.get("email")
        password = data.get("password")
        

        # Se revisa si ambos campos existen
        if not email or not password:
            return jsonify({"error": "Email y contraseña son necesarios"}), 400
        

        # Se busca el usuario en base de datos filtrando solo por el mail (único)
        user = User.query.filter_by(email=email).first()


        # Se verifica si el usuario y/o la contraseña existen
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if not check_password_hash(user.password, password):
            return jsonify({"msg": "Contraseña incorrecta"}), 401


        # Verifica si el usuario está desactivado
        if not user.is_active:
            return jsonify({"error": "Usuario ha sido desactivado"}), 401


        # Genera un token de acceso (con expiración)
        access_token = create_access_token(
            identity=str(user.id),  # Identidad del usuario (puedes usar el ID o el email)
            expires_delta=datetime.timedelta(hours=24)  # Expiración del token
        )

        return jsonify({
            "msg": "Inicio de sesión exitoso.",
            "access_token": access_token,
            "user": user.serialize()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


####################################################################################


############################################
#######     PRIVATE SITE TESTING     #######
############################################
""" 
Cómo añadir el Access_Token en el header en Postman:
    - Ir a la pestaña "Authorization"
    - Elegir "Bearer Toker" en el dropdown
    - Pegar el token SIN COMILLAS
"""
@api.route('/testing-private', methods=['GET'])
@jwt_required() # Uso del JWT
def private_route():

    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({ "msg": "Usuario no encontrado." }), 404
    
    return jsonify({
        "msg": f"Welcome {user.email}!",
        "user": user.serialize()
    }), 200


####################################################################################


############################################
#######     User - Perfil Privado    #######
#######       GET datos usuario      #######
############################################

@api.route('/profile', methods=['GET'])
@jwt_required()
def get_user_private_profile():
    
    try:

        # Obtener el ID del usuario autenticado
        current_user_id = get_jwt_identity()

        # Buscar el usuario en la base de datos
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "Usuario no encontrado."}), 404


        # Se incluye información adicional para el perfil de usuario privado
        profile_data = current_user.serialize()

        profile_data.update({
            'owned_spaces_count': len(current_user.owned_spaces),
            'bookings_count':     len(current_user.bookings),
            'owned_spaces':       [space.serialize()   for space   in current_user.owned_spaces],
            'bookings':           [booking.serialize() for booking in current_user.bookings]
        })
        
        
        return jsonify({
            "message":     "Datos de usuario encontrados",
            "current_user": profile_data
        }), 200


    except Exception as e:
        return jsonify({'error': str(e)}), 500



############################################
#######     User - Perfil Privado    #######
#######    Modificar datos usuario   #######
############################################
"""
JSON request body para actualizar perfil:
{
    "first_name": "nuevo_nombre",      // opcional
    "last_name":  "nuevo_apellido",    // opcional
    "username":   "nuevo_username",    // opcional
    "email":      "nuevo@email.com",   // opcional

    "current_password":  "vieja_contraseña",   // opcional
    "password":         "nueva_contraseña"   // opcional
}
"""
@api.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_private_profile():


    # Obtener el ID del usuario autenticado desde el token
    user_id = get_jwt_identity()

    # Buscar el usuario en la base de datos
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    

    # Obtener los datos del request
    data = request.get_json()


    try:  

        if "first_name" in data:
            user.first_name = data["first_name"]
        
        if "last_name" in data:
            user.last_name = data["last_name"]
        
        if "username" in data:
            # Verificar que el username no esté en uso
            existing_user = User.query.filter(User.username == data["username"], User.id != user.id).first()
            if existing_user:
                return jsonify({"msg": "Este nombre de usuario ya está en uso."}), 400
            user.username = data["username"]
        
        if "email" in data:
            # Verificar que el email no esté en uso
            existing_user = User.query.filter(User.email == data["email"], User.id != user.id).first()
            if existing_user:
                return jsonify({"msg": "Este correo electrónico ya está registrado."}), 400
            user.email = data["email"]


        # Manejo de cambio de contraseña
        if 'password' in data:
            if 'current_password' not in data:
                return jsonify({'error': 'Se necesita la contraseña actual para cambiar a nueva contraseña.'}), 400
            
            if not check_password_hash(user.password, data['current_password']):
                return jsonify({'error': 'La contraseña actual es incorrecta.'}), 400
            
            user.password = generate_password_hash(data['password'])
        
        
        # Guardar cambios en la BBDD
        db.session.commit()


        return jsonify({
            'message': 'Profile actualizado exitosamente.',
            'user': user.serialize()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar perfil.", 'error': str(e)}), 500
    

############################################
#######   GET ALL SPACES (PUBLIC)    #######
############################################
"""
Obtiene la lista de todos los espacios disponibles
Endpoint público - no requiere autenticación
"""
@api.route('/spaces', methods=['GET'])
def get_all_spaces():

    try:
        # Obtenemos todos los espacios de la base de datos
        spaces = Space.query.all()


        # Serializar todos los espacios
        spaces_data = [space.serialize() for space in spaces]

        return jsonify({
            "msg":    "Espacios obtenidos exitosamente.",
            "total":  len(spaces_data),
            "spaces": spaces_data
        }), 200

    except Exception as e:
        return jsonify({"message": "Error al obtener espacios.", "error": str(e)}), 500