# Previous imports remain...
"""app module"""
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:admin@localhost:5432/testdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'options': '-csearch_path=testdb,public'
    }
}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class CarsModel(db.Model):
    """class cars"""
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    model = db.Column(db.String())
    doors = db.Column(db.Integer())
    engine = db.Column(db.String())

    def __init__(self, name, model, doors, engine):
        self.name = name
        self.model = model
        self.doors = doors
        self.engine = engine

    def __repr__(self):
        return f"<Car {self.name}>"

# Imports and CarsModel truncated

@app.route('/cars', methods=['POST', 'GET'])
def handle_cars():
    """get and post cars"""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_car = CarsModel(name=data['name'], model=data['model'],
                                doors=data['doors'], engine=data['engine'])
            db.session.add(new_car)
            db.session.commit()
            return {"message": f"car {new_car.name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        cars = CarsModel.query.all()
        results = [
            {
                "name": car.name,
                "model": car.model,
                "doors": car.doors
            } for car in cars]

        return {"count": len(results), "cars": results}
