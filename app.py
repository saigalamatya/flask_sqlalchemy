from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)

# @app.route('/', methods=['GET'])
# def get():
#   return jsonify({ 'msg': 'Hello World!' })

basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init marshmallow
ma = Marshmallow(app)

# Swagger Configuration
# @app.route('/static/<path:path>')
# def send_static(path):
#   return send_from_directory('static', path)

# Swagger URL
SWAGGER_URL = '/api/docs' # URL for exposing Swagger UI (without trailing '/')
API_URL = 'http://localhost:5000' # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
SWAGGER_URL, # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
API_URL,
config={ # Swagger UI config overrides
'app_name': "FLASK CRUD Application"
},
# oauth_config={ # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
# 'clientId': "your-client-id",
# 'clientSecret': "your-client-secret-if-required",
# 'realm': "your-realms",
# 'appName': "your-app-name",
# 'scopeSeparator': " ",
# 'additionalQueryStringParams': {'test': "hello"}
# }
)

# Register blueprint at URL
# (URL must match the one given to factory function above)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

app.run()

# Product Class/Model
class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), unique=True)
  description = db.Column(db.String(200))
  price = db.Column(db.Float)
  qty = db.Column(db.Integer)

  def __init__(self, name, description, price, qty):
    self.name = name
    self.description = description
    self.price = price
    self.qty = qty

# Product Schema
class ProductSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'description', 'price', 'qty')

# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a Product
@app.route('/product', methods=['POST'])
def add_product():
  name = request.json['name']
  description = request.json['description']
  price = request.json['price']
  qty = request.json['qty']

  new_product = Product(name, description, price, qty)

  db.session.add(new_product)
  db.session.commit()

  return product_schema.jsonify(new_product)


# Get All Products
@app.route('/product', methods=['GET'])
def get_products():
  all_products = Product.query.all()
  result = products_schema.dump(all_products)
  
  return jsonify(result)

# Get Single Product
@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
  product = Product.query.get(id)
  
  return product_schema.jsonify(product)

# Update a Product
@app.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
  product = Product.query.get(id)
    
  name = request.json['name']
  description = request.json['description']
  price = request.json['price']
  qty = request.json['qty']

  product.name = name
  product.description = description
  product.price = price
  product.qty = qty

  db.session.commit()

  return product_schema.jsonify(product)

# Delete a product
@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
  product = Product.query.get(id)
  db.session.delete(product)
  db.session.commit()

  return product_schema.jsonify(product)


# Run Server
if __name__ == '__main__':
  app.run(debug=True)
