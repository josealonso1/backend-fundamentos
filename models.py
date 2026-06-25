from extensions import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    productos = db.relationship('Producto', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
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
    