import json
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser
from django.core.exceptions import ValidationError


class ToiletTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.client.post('/auth/users/',data={'email':'user1@example.com','password':'banana678!'})
        response = self.client.post('/auth/token/login/', data={'email': 'user1@example.com', 'password': 'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='TOKEN ' + self.token)

    def test_post_multiple_toilets(self):
        with open('Toilets4LondonAPI/toilets4london/tests/example_data.json') as datafile:
            json_data = datafile.read()
        response = self.client.post(
            '/toilets/',
            data=json_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Toilet.objects.count(), 848)

    def test_pagination(self):
        with open('Toilets4LondonAPI/toilets4london/tests/example_data.json') as datafile:
            json_data = datafile.read()
        self.client.post(
            '/toilets/',
            data=json_data,
            content_type='application/json'
        )
        response = self.client.get('/toilets/?page_size=1000')
        self.assertIsNone(response.data['next'])
        response = self.client.get('/toilets/')
        self.assertIsNotNone(response.data['next'])

    def test_geocoding(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        toilet = Toilet.objects.create(address="Hampton Court Road, Richmond", owner=user)
        self.assertEqual(51.4124879, toilet.latitude)
        self.assertEqual(-0.3587922, toilet.longitude)
        self.assertTrue("Richmond" in toilet.borough)

    def test_geocoding_invalid_address(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        with self.assertRaises(ValidationError):
            Toilet.objects.create(address="Bananarama in pyjamas", owner=user)

    def test_reverse_geocoding_invalid_coords(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        with self.assertRaises(ValidationError):
            Toilet.objects.create(latitude=0,longitude=4545, owner=user)

    def test_error_when_no_location_info(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        with self.assertRaises(ValidationError):
            Toilet.objects.create(owner=user, name="Random toilet with no location")

    def test_reverse_geocoding(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        toilet = Toilet.objects.create(latitude=51.4087329, longitude=-0.3323747, owner=user)
        self.assertTrue("Hampton Court Road" in toilet.address)
        self.assertEqual(toilet.borough, "Richmond upon Thames")

    def test_no_reverse_geocoding_when_address_set(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        toilet = Toilet.objects.create(latitude=51.4087329, longitude=-0.3323747, owner=user, address="random")
        self.assertEqual(toilet.address, "random")
        self.assertEqual(toilet.borough, "")

    def test_borough_added_if_possible(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        toilet = Toilet.objects.create(latitude=51.4087329, longitude=-0.3323747, owner=user, address="a place in Camden")
        self.assertEqual(toilet.address, "a place in Camden")
        self.assertEqual(toilet.borough, "Camden")

    def test_borough_not_changed_if_present(self):
        user = Toilets4LondonUser.objects.create(email="test", password="banana")
        toilet = Toilet.objects.create(latitude=51.4087329, longitude=-0.3323747, owner=user, borough="Random")
        self.assertTrue("Hampton Court Road" in toilet.address)
        self.assertEqual(toilet.borough, "Random")
