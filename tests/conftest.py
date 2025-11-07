"""test"""
import pytest
from app import db, app, CarsModel

@pytest.fixture
def client_postgres():
    """Client avec PostgreSQL de test (optionnel)"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/test_db'

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def sample_car():
    """Fixture pour une voiture exemple"""
    return {
        'name': 'Toyota',
        'model': 'Corolla',
        'doors': 4,
        'engine': 'V4'
    }

@pytest.fixture
def init_database():
    """Initialise la base avec des données de test"""
    with app.app_context():
        car1 = CarsModel(name='Toyota', model='Corolla', doors=4, engine='V4')
        car2 = CarsModel(name='Honda', model='Civic', doors=4, engine='V4')
        car3 = CarsModel(name='Ford', model='Mustang', doors=2, engine='V8')
        db.session.add_all([car1, car2, car3])
        db.session.commit()
    yield
