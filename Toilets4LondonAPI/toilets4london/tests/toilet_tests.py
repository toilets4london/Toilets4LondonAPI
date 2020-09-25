import json
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser


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
