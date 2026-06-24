from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    productos = db.relationship('Producto', backref='usuario', lazy=True)
    
    def serialize(self):
        return{
            "id":self.id,
            "nombre":self.nombre,
            "email":self.email
        }

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    def to_dict(self):
        return{
            "id":self.id,
            "nombre":self.nombre,
            "precio":self.precio,
            "descripcion":self.descripcion,
            "usuario_id":self.usuario_id
        }
    

@app.route('/')
def home():
    return "Hola, esto funciona"

@app.route('/usuario/register', methods=['POST'])
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
    
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuario = Usuario.query.all()
    resultado = [p.serialize() for p in usuario]
    return jsonify(resultado), 200
    
@app.route('/registro', methods=['POST'])
def registro():
    
    datos = request.json
    
    if not datos:
        return jsonify({"error": "No se enviaron datos en formato JSON"}), 400
    
    if "nombre" not in datos:
        return jsonify({"error": "Falta el campo 'nombre'"}), 400
    
    if "edad" not in datos:
        return jsonify({"error": "Falta el campo 'edad'"}), 400
    nombre = datos["nombre"]
    edad = datos["edad"]
    
    return f"Usuario {nombre} de {edad} anhos registrado"

@app.route('/productos', methods=['POST'])
def crear_producto():
    
    datos = request.json
    
    if not datos:
        return jsonify({"error": "No se enviaron datos en formato JSON"}), 400
    
    if "nombre" not in datos or "precio" not in datos or "usuario_id" not in datos:
        return jsonify({"error": "Falta el campos obligatorios"}), 400
    
    usuario = Usuario.query.get(datos["usuario_id"])
    if not usuario:
        return jsonify({"error": "Ese usuario no existe"}), 404
    
    nuevo = Producto(nombre=datos["nombre"], precio=datos["precio"], usuario_id=usuario.id)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()),201

@app.route('/usuarios/<int:id>/productos', methods=['GET'])
def productos_de_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": "Usuario no existe"}), 404

    productos = [p.to_dict() for p in usuario.productos]
    return jsonify(productos), 200

@app.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    resultado = [p.to_dict() for p in productos]
    return jsonify(resultado), 200

@app.route('/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    producto = Producto.query.get(id)
    
    if not producto:
        return jsonify({"error": "Este producto no existe"}), 404
    
    return jsonify(producto.to_dict()), 200

@app.route('/productos/<int:id>', methods=['PUT'])
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
    
@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    
    producto = Producto.query.get(id)
    if producto is None:
        return jsonify({"error": f"el id con el numero {id} no existe"}), 404
    
    nombre = producto.nombre
    
    db.session.delete(producto)
    db.session.commit()
    
    return jsonify({"mensaje": f"El producto {nombre} fue eliminado"}), 200
    
@app.errorhandler(404)
def no_encontrado(error):
    return jsonify({"error": "Esa ruta no existe"}), 404

if __name__ == '__main__':
    app.run(debug=True)