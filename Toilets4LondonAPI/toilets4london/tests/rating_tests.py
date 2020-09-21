from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser


fakerating = {
    "toilet": 1,
    "rating": 5
}

fakerating2 = {
    "toilet": 1,
    "rating": 4
}

invalidrating1 = {
    "toilet": 100,
    "rating": 5
}

invalidrating2 = {
    "toilet": 1,
    "rating": 66
}


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


class RatingTests(APITestCase):

    def setUp(self):
        create_toilet()
        self.client = APIClient()
        self.user = self.client.post('/auth/users/',data={'email':'user1@example.com','password':'banana678!'})
        response = self.client.post('/auth/token/login/', data={'email': 'user1@example.com', 'password': 'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='TOKEN ' + self.token)

    def test_post_rating_once(self):
        response = self.client.post('/ratings/',fakerating)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_rating_twice(self):
        response = self.client.post('/ratings/',fakerating)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post('/ratings/', fakerating2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"Error":"Cannot review toilet twice"})

    def test_post_rating_invalid_toilet(self):
        response = self.client.post('/ratings/',invalidrating1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_rating_invalid_rating(self):
        response = self.client.post('/ratings/',invalidrating2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_rating(self):
        response = self.client.post('/ratings/', fakerating)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.put('/ratings/1/', fakerating2)
        self.assertEqual(response.status_code,status.HTTP_200_OK)