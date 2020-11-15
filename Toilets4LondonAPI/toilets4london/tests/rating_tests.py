from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser


fakerating = {
    'toilet': 1,
    'rating': 5
}

fakerating2 = {
    'toilet': 1,
    'rating': 4
}

invalidrating1 = {
    'toilet': 100,
    'rating': 5
}

invalidrating2 = {
    'toilet': 1,
    'rating': 66
}


def create_toilet():
    user = Toilets4LondonUser.objects.create(
        email='hello@example.com',
        password='thisisarandomstring!2'
    )
    Toilet.objects.create(
        address='5 Mill Lane',
        borough='Camden',
        latitude=12,
        longitude=12,
        owner=user,
        opening_hours='',
        name='Fake Toilet',
        wheelchair=False
    )


class RatingTests(APITestCase):

    def setUp(self):
        create_toilet()
        self.client = APIClient()
        self.user = self.client.post('/auth/users/',data={'email':'user1@example.com','password':'banana678!'})
        response = self.client.post('/auth/token/login/', data={'email': 'user1@example.com', 'password': 'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_post_rating_once(self):
        response = self.client.post('/ratings/',fakerating)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

    def test_average_rating_added_1_rating(self):
        toilet = Toilet.objects.get(id=1)
        self.assertEqual(0, toilet.num_ratings)
        self.assertIsNone(toilet.rating)
        self.client.post('/ratings/',fakerating)
        toilet = Toilet.objects.get(id=1)
        self.assertEqual(1, toilet.num_ratings)
        self.assertEqual(5, toilet.rating)

    def test_average_rating_updated_2_ratings(self):
        self.client.post('/ratings/',fakerating)
        self.client.post('/ratings/',fakerating2)
        toilet = Toilet.objects.get(id=1)
        self.assertEqual(4.5, toilet.rating)
        self.assertEqual(2, toilet.num_ratings)

    def test_weighted_average_rating_updated(self):
        self.client.post('/ratings/',{'toilet':1,'rating':5})
        self.client.post('/ratings/',{'toilet':1,'rating':3})
        self.client.post('/ratings/', {'toilet':1, 'rating':1})
        toilet = Toilet.objects.get(id=1)
        self.assertEqual(3, toilet.rating)
        self.assertEqual(3, toilet.num_ratings)

    def test_weighted_average_rating_not_updated_invalid_rating(self):
        self.client.post('/ratings/',{'toilet':1,'rating':5})
        self.client.post('/ratings/',{'toilet':1,'rating':3})
        self.client.post('/ratings/', {'toilet':1, 'rating':100})
        toilet = Toilet.objects.get(id=1)
        self.assertEqual(4, toilet.rating)
        self.assertEqual(2, toilet.num_ratings)