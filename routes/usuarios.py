from flask import Blueprint, request, jsonify
from models import Usuario, Producto
from extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


api_users = Blueprint('usuarios', __name__)

@api_users.route('/usuarios/register', methods=['POST'])
def crear_usuario():
    
    datos = request.json
    
    if not datos:
        return jsonify({"error": "No se enviaron datos en formato JSON"}), 400

    if "nombre" not in datos or "email" not in datos or "password" not in datos:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    nombre_limpio = datos["nombre"].strip()
    email_limpio = datos["email"].strip()
    password_limpio = datos["password"].strip()
    
    if not nombre_limpio or len(nombre_limpio) > 50:
        return jsonify({"error": "El campo nombre debe estar relleno"}), 400
    
    if not email_limpio or len(email_limpio) > 100:
        return jsonify({"error": "El campo email debe estar relleno"}), 400
    
    if not password_limpio or len(password_limpio) > 200:
        return jsonify({"error": "El campo password debe estar relleno"}), 400
    
    nuevo_usuario = Usuario(nombre=nombre_limpio, email=email_limpio)
    nuevo_usuario.set_password(password_limpio) 
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    return jsonify({"mensaje": "Nuevo usuario creado",
                    "Usuario":nuevo_usuario.serialize()}), 201
    
@api_users.route('/usuarios/login', methods=['POST'])
def login_usuario():
    datos = request.json
    
    if not datos or "email" not in datos or "password" not in datos:
        return jsonify({"error": "faltan credenciales"}), 400
    
    usuario = Usuario.query.filter_by(email=datos["email"]).first()
    
    if not usuario or not usuario.check_password(datos["password"]):
        return jsonify({"error": "Email o constraseña incorrectos"}), 401
    
    token = create_access_token(identity=str(usuario.id))
    
    return jsonify({"access_token": token}), 200
    
    
@api_users.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuario = Usuario.query.all()
    resultado = [p.serialize() for p in usuario]
    return jsonify(resultado), 200

@api_users.route('/usuarios/productos', methods=['GET'])
@jwt_required()
def productos_de_usuario():
    usuario_actual_id = int(get_jwt_identity())
    
    usuario = Usuario.query.get(usuario_actual_id)
    
    if usuario.id != usuario_actual_id:
        return jsonify({"error": "No tienes permiso para editar otros productos"}), 403

    productos = [p.to_dict() for p in usuario.productos]
    return jsonify(productos), 200

@api_users.route('/usuarios/productos', methods=['POST'])
@jwt_required()
def crear_producto():
    
    usuario_actual_id = int(get_jwt_identity())
    usuario = Usuario.query.get(usuario_actual_id)

    if not usuario:
        return jsonify({"error": "Usuario no existe"}), 404
    
    datos = request.json
    
    if not datos:
        return jsonify({"error": "No se enviaron datos en formato JSON"}), 400
    
    if "nombre" not in datos or "precio" not in datos:
        return jsonify({"error": "Falta el campos obligatorios"}), 400
    
    nombre_limpio = datos["nombre"].strip()
    if not nombre_limpio or len(nombre_limpio) > 100:
        return jsonify({"error": "El nombre no puede estar vacio o contar con mas de 100 caracteres"}), 400
    
    if "precio" in datos:
        if not isinstance(datos["precio"],(int, float)):
            return jsonify({"error": "El precio debe ser un numero"}), 400
        
    nuevo = Producto(nombre=datos["nombre"], precio=datos["precio"], usuario_id=usuario.id)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()),201

@api_users.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required()
def editar_usuario(id):
    
    usuario_actual_id = get_jwt_identity()
    if str(id) != usuario_actual_id:
        return jsonify({"error": "No tienes permiso para editar otros usuarios"}), 403
    
    usuario = Usuario.query.get(id)
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Es obligatorio mandar en datos formato JSON"}), 400
    
    if "nombre" in data:
        nombre_limpio = data["nombre"].strip()
        if not nombre_limpio or len(nombre_limpio) > 50:
            return jsonify({"error": "El nombre no puede estar vacio o tener mas de 50 caracteres"}), 400
        usuario.nombre = nombre_limpio
    
    if "email" in data:
        email_limpio = data["email"].strip()
        if not email_limpio or len(email_limpio) > 100:
            return jsonify({"error": "El email no puede estar vacio o tener mas de 100 caracteres"}), 400
        usuario.email = email_limpio
        
    if "password" in data:
        password_limpio = data["password"].strip()
        if not password_limpio or len(password_limpio) > 200:
            return jsonify({"error": "El password no puede estar vacio o teer mas de 100 caracteres"}), 400
        usuario.set_password(password_limpio)
    db.session.commit()
    
    return jsonify({"mensaje": "Tu usuario fue actualizado",
                    "usuario":usuario.serialize()}), 200
    
@api_users.route('/usuarios/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(id):
    
    usuario_actual_id = get_jwt_identity()
    
    if str(id) != usuario_actual_id:
        return jsonify({"error": "No tienes permiso para eliminar otros usuarios"}), 403
    
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": f"Este id {id} no tiene ningun usuario registrado"}), 404
    
    nombre = usuario.nombre
    db.session.delete(usuario)
    db.session.commit()
    
    return jsonify({"mensaje": f"Usuario {nombre} eliminado con existo"}), 200