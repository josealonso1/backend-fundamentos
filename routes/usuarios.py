from flask import Blueprint, request, jsonify
from models import Usuario, Producto
from extensions import db

api_users = Blueprint('usuarios', __name__)

@api_users.route('/usuarios/register', methods=['POST'])
def crear_usuario():
    datos = request.json
    
    if not datos:
        return jsonify({"error": "No se enviaron datos en formato JSON"}), 400

    if "nombre" not in datos or "email" not in datos:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    nombre_limpio = datos["nombre"].strip()
    email_limpio = datos["email"].strip()
    
    if not nombre_limpio or len(nombre_limpio) > 50:
        return jsonify({"error": "El campo nombre debe estar relleno"}), 400
    
    if not email_limpio or len(email_limpio) > 100:
        return jsonify({"error": "El campo email debe estar relleno"}), 400
    
    nuevo_usuario = Usuario(nombre=nombre_limpio, email=email_limpio)
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    return jsonify({"mensaje": "Nuevo usuario creado",
                    "Usuario":nuevo_usuario.serialize()}), 201
    
@api_users.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuario = Usuario.query.all()
    resultado = [p.serialize() for p in usuario]
    return jsonify(resultado), 200

@api_users.route('/usuarios/<int:id>/productos', methods=['GET'])
def productos_de_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": "Usuario no existe"}), 404

    productos = [p.to_dict() for p in usuario.productos]
    return jsonify(productos), 200

@api_users.route('/usuarios/<int:id>', methods=['PUT'])
def editar_usuario(id):
    
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return jsonify({"error": f"No se existe este id {id}"}), 404
    
    data = request.json
    
    if not data:
        return jsonify({"error": "Es obligatorio mandar en datos formato JSON"}), 400
    
    #if "nombre" not in data or "email" not in data:
    #    return jsonify({"error": "Faltan campos obligatorios"}), 400
    
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
        
    db.session.commit()
    
    return jsonify({"mensaje": "Tu usuario fue actualizado",
                    "usuario":usuario.serialize()}), 200
    
@api_users.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return jsonify({"error": f"Este id {id} no tiene ningun usuario registrado"}), 404
    
    #if usuario.productos:
    #    return jsonify({"error": "No se puede eliminar: el usuario tiene productos asociados"}), 400
    
    nombre = usuario.nombre
    
    db.session.delete(usuario)
    db.session.commit()
    
    return jsonify({"mensaje": f"Usuario {nombre} eliminado con existo"}), 200