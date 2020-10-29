from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser, Rating


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
        print(response.data)
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

    def test_importing_exported_data(self):
        # This works provided "1" and "0" are replaced with "true" and "false"
        with open('Toilets4LondonAPI/toilets4london/tests/example_old_data.json') as datafile:
            json_data = datafile.read()
        response = self.client.post(
            '/toilets/',
            data=json_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get('/toilets/')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_average_rating_serialised(self):

        user1 = Toilets4LondonUser.objects.create(
            email="hello@example.com",
            password="thisisarandomstring!2"
        )

        user2 = Toilets4LondonUser.objects.create(
            email="hello@banana.com",
            password="thisisarandomstring!2"
        )

        toilet1 = Toilet.objects.create(
            borough="Camden",
            latitude=12,
            longitude=12,
            owner=user1
        )

        Rating.objects.create(
            toilet=toilet1,
            user=user1,
            rating=5
        )

        Rating.objects.create(
            toilet=toilet1,
            user=user2,
            rating=4
        )

        response = self.client.get('/toilets/')
        results = response.data['results']
        self.assertEqual(results[0]['rating'], 4.5)



