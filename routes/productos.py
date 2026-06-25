from flask import Blueprint, request, jsonify
from models import Producto , Usuario
from extensions import db

api_productos = Blueprint('productos', __name__)

@api_productos.route('/productos', methods=['POST'])
def crear_producto():
    
    datos = request.json
    
    if not datos:
        return jsonify({"error": "No se enviaron datos en formato JSON"}), 400
    
    if "nombre" not in datos or "precio" not in datos or "usuario_id" not in datos:
        return jsonify({"error": "Falta el campos obligatorios"}), 400
    
    nombre_limpio = datos["nombre"].strip()
    if not nombre_limpio or len(nombre_limpio) > 100:
        return jsonify({"error": "El nombre no puede estar vacio o contar con mas de 100 caracteres"}), 400
    
    usuario = Usuario.query.get(datos["usuario_id"])
    if not usuario:
        return jsonify({"error": "Ese usuario no existe"}), 404
    
    nuevo = Producto(nombre=datos["nombre"], precio=datos["precio"], usuario_id=usuario.id)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()),201

@api_productos.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    resultado = [p.to_dict() for p in productos]
    return jsonify(resultado), 200

@api_productos.route('/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    producto = Producto.query.get(id)
    
    if not producto:
        return jsonify({"error": "Este producto no existe"}), 404
    
    return jsonify(producto.to_dict()), 200

@api_productos.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    
    producto = Producto.query.get(id)
    
    if not producto:
        return jsonify({"error": f"el id con el numero {id} no existe"}), 404
    
    data = request.json
    
    if not data:
        return jsonify({"error": "No se enviaron datos en formato JSON"}), 400
    
    if "nombre" in data:
        nombre_limpio = data["nombre"].strip()
        if not nombre_limpio or len(nombre_limpio) > 40:
            return jsonify({"mensaje":"El nombre no puede estar vacio o contener mas de 40 caracteres"}), 400
        producto.nombre=nombre_limpio
    
    if "precio" in data:
        if not isinstance(data["precio"],(int, float)):
            return jsonify({"error": "El precio debe ser un numero"}), 400
        producto.precio = data["precio"]
        
    db.session.commit()

    return jsonify({"mensaje":"Tu Producto fue actualizado",
                    "producto": producto.to_dict()}), 200
    
@api_productos.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    
    producto = Producto.query.get(id)
    if producto is None:
        return jsonify({"error": f"el id con el numero {id} no existe"}), 404
    
    nombre = producto.nombre
    
    db.session.delete(producto)
    db.session.commit()
    
    return jsonify({"mensaje": f"El producto {nombre} fue eliminado"}), 200