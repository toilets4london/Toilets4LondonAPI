from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser


def create_toilet():

    user = Toilets4LondonUser.objects.create(
        email="hello@example.com",
        password="thisisarandomstring!2"
    )
    Toilet.objects.create(
        address="5 Mill Lane",
        borough="Camden",
        latitude=12,
        longitude=12,
        owner=user,
        opening_hours="",
        name="Fake Toilet",
        wheelchair=False
    )


class ToiletTests(APITestCase):

    def setUp(self):
        create_toilet()
        self.client = APIClient()
        self.user = self.client.post('/auth/users/',data={'email':'user1@example.com','password':'banana678!'})
        response = self.client.post('/auth/token/login/', data={'email': 'user1@example.com', 'password': 'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='TOKEN ' + self.token)

    def test_post_rating_once(self):
