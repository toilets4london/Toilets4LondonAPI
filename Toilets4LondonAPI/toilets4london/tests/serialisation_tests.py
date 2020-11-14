from rest_framework.test import APITestCase, APIClient
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser
import json


class SerialisationTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.client.post('/auth/users/', data={'email': 'user1@example.com', 'password': 'banana678!'})
        response = self.client.post('/auth/token/login/', data={'email': 'user1@example.com', 'password': 'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def testOwnerAutomaticallyAdded(self):
        self.client.post('/toilets/',{'latitude': 1, 'longitude':1})
        self.assertEqual(Toilet.objects.filter(id=1).first().owner.email, 'user1@example.com')

    def testOwnerFieldHidden(self):
        response = self.client.get('/toilets/')
        self.assertTrue('owner' not in response)

    def testClosedToiletCanBePosted(self):
        self.client.post('/toilets/', json.dumps({'latitude': 2, 'longitude': 1, 'open': False}),
                         content_type='application/json')
        print(Toilet.objects.filter(latitude=2).first())
        self.assertEqual(Toilet.objects.filter(latitude=2).first().open, False)

    def testClosedToiletsExcludedFromResults(self):
        self.client.post('/toilets/', json.dumps({'latitude': 2, 'longitude': 1, 'open': False}),
                         content_type='application/json')
        self.client.post('/toilets/', json.dumps({'latitude': 3, 'longitude': 1, 'open': True}),
                         content_type='application/json')
        response = self.client.get('/toilets/')
        self.assertEqual(response.data['count'],1)
        self.assertEqual(response.data['results'][0]['latitude'], 3)
