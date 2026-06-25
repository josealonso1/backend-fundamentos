from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extensions import db
from models import Usuario, Producto

from routes.usuarios import api_users
from routes.productos import api_productos


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(api_users)
app.register_blueprint(api_productos)

@app.route('/')
def home():
    return "Hola, esto funciona"

    
@app.errorhandler(404)
def no_encontrado(error):
    return jsonify({"error": "Esa ruta no existe"}), 404

if __name__ == '__main__':
    app.run(debug=True)