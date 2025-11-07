"""Module APP"""
import json
import pytest

class TestGetCars:
    """Tests pour GET /cars"""

    def test_get_cars_empty(self, client_postgres):
        """Test GET /cars sans données"""
        response = client_postgres.get('/cars')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['cars'] == []

    def test_get_cars_with_data(self, client_postgres):
        """Test GET /cars avec données"""
        response = client_postgres.get('/cars')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 3
        assert len(data['cars']) == 3

        # Vérifier la structure des données
        first_car = data['cars'][0]
        assert 'name' in first_car
        assert 'model' in first_car
        assert 'doors' in first_car
        # Note: engine n'est pas dans la réponse

    def test_get_cars_response_structure(self, client_postgres):
        """Test de la structure de la réponse"""
        response = client_postgres.get('/cars')
        data = json.loads(response.data)

        # Vérifier que Toyota existe
        toyota = next((car for car in data['cars'] if car['name'] == 'Toyota'), None)
        assert toyota is not None
        assert toyota['model'] == 'Corolla'
        assert toyota['doors'] == 4


class TestPostCars:
    """Tests pour POST /cars"""

    def test_create_car_success(self, client_postgres, sample_car):
        """Test POST /cars avec données valides"""
        response = client_postgres.post(
            '/cars',
            data=json.dumps(sample_car),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Toyota' in data['message']
        assert 'created successfully' in data['message']

        # Vérifier que la voiture a été ajoutée
        response = client_postgres.get('/cars')
        data = json.loads(response.data)
        assert data['count'] == 1

    def test_create_car_complete_data(self, client_postgres):
        """Test avec toutes les données"""
        new_car = {
            'name': 'BMW',
            'model': 'M3',
            'doors': 4,
            'engine': 'V6'
        }
        response = client_postgres.post('/cars', json=new_car)
        assert response.status_code == 200

        # Vérifier en base
        response = client_postgres.get('/cars')
        data = json.loads(response.data)
        bmw = next((car for car in data['cars'] if car['name'] == 'BMW'), None)
        assert bmw is not None
        assert bmw['model'] == 'M3'

    def test_create_car_not_json(self, client_postgres):
        """Test POST avec données non-JSON"""
        response = client_postgres.post(
            '/cars',
            data='not json data',
            content_type='text/plain'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not in JSON format' in data['error']

    def test_create_car_invalid_content_type(self, client_postgres, sample_car):
        """Test avec mauvais Content-Type"""
        response = client_postgres.post(
            '/cars',
            data=json.dumps(sample_car),
            content_type='text/html'  # Mauvais content-type
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_multiple_cars(self, client_postgres):
        """Test création de plusieurs voitures"""
        cars = [
            {'name': 'Audi', 'model': 'A4', 'doors': 4, 'engine': 'V4'},
            {'name': 'Mercedes', 'model': 'C-Class', 'doors': 4, 'engine': 'V6'},
            {'name': 'Porsche', 'model': '911', 'doors': 2, 'engine': 'V8'}
        ]

        for car in cars:
            response = client_postgres.post('/cars', json=car)
            assert response.status_code == 200

        # Vérifier le total
        response = client_postgres.get('/cars')
        data = json.loads(response.data)
        assert data['count'] == 3


class TestCarsMissingFields:
    """Tests avec champs manquants"""

    def test_create_car_missing_name(self, client_postgres):
        """Test sans le champ 'name'"""
        incomplete_car = {
            'model': 'Test',
            'doors': 4,
            'engine': 'V4'
        }
        with pytest.raises(KeyError):
            client_postgres.post('/cars', json=incomplete_car)

    def test_create_car_missing_model(self, client_postgres):
        """Test sans le champ 'model'"""
        incomplete_car = {
            'name': 'Test',
            'doors': 4,
            'engine': 'V4'
        }
        with pytest.raises(KeyError):
            client_postgres.post('/cars', json=incomplete_car)

    def test_create_car_missing_doors(self, client_postgres):
        """Test sans le champ 'doors'"""
        incomplete_car = {
            'name': 'Test',
            'model': 'TestModel',
            'engine': 'V4'
        }
        with pytest.raises(KeyError):
            client_postgres.post('/cars', json=incomplete_car)

    def test_create_car_missing_engine(self, client_postgres):
        """Test sans le champ 'engine'"""
        incomplete_car = {
            'name': 'Test',
            'model': 'TestModel',
            'doors': 4
        }
        with pytest.raises(KeyError):
            client_postgres.post('/cars', json=incomplete_car)


class TestCarsDataTypes:
    """Tests de validation des types de données"""

    def test_create_car_doors_as_string(self, client_postgres):
        """Test avec doors en string au lieu de int"""
        car = {
            'name': 'Test',
            'model': 'Test',
            'doors': '4',  # String au lieu de int
            'engine': 'V4'
        }
        response = client_postgres.post('/cars', json=car)
        # Devrait fonctionner car SQLAlchemy convertit
        assert response.status_code == 200

    def test_create_car_with_extra_fields(self, client_postgres):
        """Test avec champs supplémentaires"""
        car = {
            'name': 'Test',
            'model': 'Test',
            'doors': 4,
            'engine': 'V4',
            'color': 'Red',  # Champ supplémentaire
            'year': 2023
        }
        response = client_postgres.post('/cars', json=car)
        # Devrait fonctionner, les champs supplémentaires sont ignorés
        assert response.status_code == 200


class TestCarsIntegration:
    """Tests d'intégration"""

    def test_full_workflow(self, client_postgres):
        """Test du workflow complet : créer et lire"""
        # 1. Vérifier que c'est vide
        response = client_postgres.get('/cars')
        data = json.loads(response.data)
        assert data['count'] == 0

        # 2. Créer une voiture
        new_car = {
            'name': 'Tesla',
            'model': 'Model 3',
            'doors': 4,
            'engine': 'Electric'
        }
        response = client_postgres.post('/cars', json=new_car)
        assert response.status_code == 200

        # 3. Vérifier qu'elle existe
        response = client_postgres.get('/cars')
        data = json.loads(response.data)
        assert data['count'] == 1
        assert data['cars'][0]['name'] == 'Tesla'
        assert data['cars'][0]['model'] == 'Model 3'

    def test_multiple_operations(self, client_postgres):
        """Test avec plusieurs opérations"""
        cars = [
            {'name': 'Car1', 'model': 'Model1', 'doors': 2, 'engine': 'V4'},
            {'name': 'Car2', 'model': 'Model2', 'doors': 4, 'engine': 'V6'},
            {'name': 'Car3', 'model': 'Model3', 'doors': 4, 'engine': 'V8'}
        ]

        # Créer toutes les voitures
        for car in cars:
            client_postgres.post('/cars', json=car)

        # Vérifier le compte
        response = client_postgres.get('/cars')
        data = json.loads(response.data)
        assert data['count'] == 3

        # Vérifier les noms
        car_names = [car['name'] for car in data['cars']]
        assert 'Car1' in car_names
        assert 'Car2' in car_names
        assert 'Car3' in car_names
