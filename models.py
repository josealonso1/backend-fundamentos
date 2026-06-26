from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    productos = db.relationship('Producto', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def serialize(self):
        return{
            "id":self.id,
            "nombre":self.nombre,
            "email":self.email
        }
        
    def set_password(self, password_hash: str):
        self.password = generate_password_hash(password_hash)
        
    def check_password(self, password_hash: str) -> bool:
        return check_password_hash(self.password, password_hash)

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
    