from unittest.mock import patch
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from Toilets4LondonAPI.toilets4london.models import Toilet, Rating, Toilets4LondonUser


validSuggestedToilet = {
    "latitude": 51.5074,
    "longitude": 0.1278,
    "details": "Some text"
}

validReport = {
    "toilet": 1,
    "reason": "O",
    "other_description": "Some random description"
}

validRating = {
    'toilet': 1,
    'rating': 5
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
        wheelchair=False,
        baby_change=True
    )


class ThrottlingTests(APITestCase):

    def setUp(self):
        create_toilet()
        self.client = APIClient()
        cache.clear()

    @patch('Toilets4LondonAPI.toilets4london.throttling.PostAnonymousRateThrottle.get_rate')
    def test_throttling_suggest_toilet(self, mock):
        mock.return_value = '1/day'
        self.client.post('/suggestedtoilets/', validSuggestedToilet)
        # If throttling rate is 1 per day, the 2nd post request should return status code 429
        response = self.client.post('/suggestedtoilets/', validSuggestedToilet)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    @patch('Toilets4LondonAPI.toilets4london.throttling.PostAnonymousRateThrottle.get_rate')
    def test_throttling_different_post_requests(self, mock):
        mock.return_value = '1/day'
        self.client.post('/suggestedtoilets/', validSuggestedToilet)
        # If throttling rate is 1 per day, the 2nd post request should return status code 429
        response = self.client.post('/ratings/', validRating)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        cache.clear()
        # Rate then report
        response = self.client.post('/ratings/', validRating)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        response = self.client.post('/reports/', validReport)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )