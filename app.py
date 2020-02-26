from flask import Flask, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


# Model
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    productDescription = db.Column(db.String(100))
    productBrand = db.Column(db.String(20))
    price = db.Column(db.Integer)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, title, productDescription, productBrand, price):
        self.title = title
        self.productBrand = productBrand
        self.productDescription = productDescription
        self.price = price

    def __repr__(self):
        return '' % self.id


db.create_all()


class ProductSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Product
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    title = fields.String(required=True)
    productDescription = fields.String(required=True)
    productBrand = fields.String(required=True)
    price = fields.Number(required=True)


@app.route('/products', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        data = request.get_json()
        product_schema = ProductSchema()
        product = product_schema.load(data)
        result = product_schema.dump(product.create())
        return make_response(jsonify({'product': result}), 200)

    if request.method == 'GET':
        get_products = Product.query.all()
        product_schema = ProductSchema()
        products = product_schema.dump(get_products, many=True)
        return make_response(jsonify({'products': products}))


@app.route('/products/<id>', methods=['PUT', 'DELETE'])
def update_product_by_id(id):
    data = request.get_json()
    get_product = Product.query.get(id)

    if request.method == "PUT":
        # change to new data
        if data.get('title'):
            get_product.title = data['title']
        if data.get('productDescription'):
            get_product.productDescription = data['productDescription']
        if data.get('productBrand'):
            get_product.productBrand = data['productBrand']
        if data.get('price'):
            get_product.price = data['price']

        db.session.add(get_product)
        db.session.commit()

        product_schema = ProductSchema(only=['id', 'title', 'productDescription', 'productBrand', 'price'])
        product = product_schema.dump(get_product)
        
        return make_response(jsonify({'product': product}))

    if request.method == "DELETE":
        db.session.delete(get_product)
        db.session.commit()

        return make_response("", 204)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
