from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Toilets4LondonAPI.toilets4london.models import Toilet, Toilets4LondonUser


fakereport1 = {
    "toilet": 1,
    "reason": "O",
    "other_description": "Some random description"
}

fakereport2 = {
    "toilet": 1,
    "reason": "DNE",
}

invalidreport1 = {
    "toilet": 1,
}

invalidreport2 = {
    "toilet": 1,
    "reason": "banana",
    "other_description": "Some random description"
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


class ReportTests(APITestCase):

    def setUp(self):
        create_toilet()
        self.client = APIClient()
        self.user = self.client.post('/auth/users/',data={'email':'user1@example.com','password':'banana678!'})
        response = self.client.post('/auth/token/login/', data={'email': 'user1@example.com', 'password': 'banana678!'})
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='TOKEN ' + self.token)

    def test_post_report_once(self):
        response = self.client.post('/reports/',fakereport1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_report_invalid_toilet(self):
        response = self.client.post('/reports/',invalidreport1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_report_invalid_report(self):
        response = self.client.post('/reports/',invalidreport2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_report(self):
        response = self.client.post('/reports/', fakereport1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.put('/reports/1/', fakereport2)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
