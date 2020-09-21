from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

faketoilet = {
    "address": "50 Mill Lane",
    "borough": "Hornsey",
    "latitude": 1,
    "longitude": 2,
    "opening_hours": "5am to 10pm every day",
    "wheelchair": False,
    "name": "Random toilet"
}

fakerating = {
    "toilet": 1,
    "rating": 5
}


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser('admin@example.com', 'banana678!')
        self.user_1 = self.client.post('/auth/users/',data={'email':'user1@example.com','password':'banana678!'})
        self.user_2 = self.client.post('/auth/users/', data={'email': 'user2@example.com', 'password': 'banana678!'})

    def api_authentication_user1(self):
        response = self.client.post('/auth/token/login/', data={'email':'user1@example.com','password':'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='TOKEN ' + self.token)

    def api_authentication_user2(self):
        response = self.client.post('/auth/token/login/', data={'email':'user2@example.com','password':'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='TOKEN ' + self.token)

    def api_authentication_admin(self):
        self.client.force_login(self.admin_user)

    def create_toilet(self):
        self.api_authentication_admin()
        self.client.post('/toilets/', faketoilet)
        self.client.logout()

    def test_toilet_list_unauthenticated(self):
        response = self.client.get('/toilets/')
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_user_list_unauthenticated(self):
        response = self.client.get('/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_same_user_detail(self):
        self.api_authentication_user1()
        response = self.client.get("/auth/users/2/")
        self.assertEqual(response.data['email'],'user1@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_different_user_detail(self):
        self.api_authentication_user2()
        response = self.client.get("/auth/users/2/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_post_toilet(self):
        self.api_authentication_admin()
        toilet_response = self.client.post('/toilets/', faketoilet)
        self.assertEqual(toilet_response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

    def test_other_post_toilet(self):
        self.api_authentication_user2()
        toilet_response = self.client.post('/toilets/', faketoilet)
        self.assertEqual(toilet_response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_post_toilet(self):
        toilet_response = self.client.post('/toilets/', faketoilet)
        self.assertEqual(toilet_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review(self):
        self.create_toilet()
        self.api_authentication_user1()
        rating_response = self.client.post('/ratings/', fakerating)
        self.assertEqual(rating_response.status_code, status.HTTP_201_CREATED)

    def test_read_own_rating(self):
        self.create_toilet()
        self.api_authentication_user1()
        self.client.post('/ratings/', fakerating)
        rating_detail_response = self.client.get('/ratings/1/')
        self.assertEqual(rating_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(rating_detail_response.data['user'], 2)

    def test_read_others_rating(self):
        self.create_toilet()
        self.api_authentication_user1()
        self.client.post('/ratings/', fakerating)
        self.api_authentication_user2()
        rating_detail_response = self.client.get('/ratings/1/')
        self.assertEqual(rating_detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_ratings_unauthenticated(self):
        response = self.client.get('/ratings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_ratings_authenticated(self):
        self.api_authentication_user1()
        response = self.client.get('/ratings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_can_see_own_ratings(self):
        self.create_toilet()
        self.api_authentication_user1()
        self.client.post('/ratings/', fakerating)
        self.api_authentication_user2()
        self.client.post('/ratings/', fakerating)
        response = self.client.get('/ratings/')
        self.assertEqual(response.data['count'], 1)