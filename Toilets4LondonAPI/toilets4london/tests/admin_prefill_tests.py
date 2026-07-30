from django.test import TestCase, Client, override_settings
from Toilets4LondonAPI.toilets4london.admin import SUGGESTION_OWNER_EMAIL
from Toilets4LondonAPI.toilets4london.models import Toilets4LondonUser


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class SuggestionPrefillTests(TestCase):

    def setUp(self):
        self.superuser = Toilets4LondonUser.objects.create_superuser(
            email="admin@example.com", password="pass12345"
        )
        self.nina = Toilets4LondonUser.objects.create_user(
            email=SUGGESTION_OWNER_EMAIL, password="pass12345"
        )
        self.client = Client()
        self.client.force_login(self.superuser)

    def get_add_form(self, params=None):
        response = self.client.get("/admin/toilets4london/toilet/add/", params or {})
        self.assertEqual(response.status_code, 200)
        return response.context["adminform"].form

    def get_initial(self, form, field_name):
        return form.get_initial_for_field(form.fields[field_name], field_name)

    def test_prefill_from_suggestion(self):
        form = self.get_add_form(
            {
                "from_suggestion": "1",
                "latitude": "51.5074",
                "longitude": "-0.1278",
                "details": "Toilet in the nice cafe",
            }
        )
        self.assertEqual(self.get_initial(form, "latitude"), "51.5074")
        self.assertEqual(self.get_initial(form, "longitude"), "-0.1278")
        self.assertEqual(self.get_initial(form, "name"), "Toilet in the nice cafe")
        self.assertEqual(self.get_initial(form, "data_source"), "App upload")
        self.assertEqual(self.get_initial(form, "owner"), self.nina)

    def test_prefill_from_suggestion_without_details(self):
        form = self.get_add_form(
            {
                "from_suggestion": "1",
                "latitude": "51.5074",
                "longitude": "-0.1278",
            }
        )
        self.assertEqual(self.get_initial(form, "name"), "")
        self.assertEqual(self.get_initial(form, "data_source"), "App upload")

    def test_prefill_owner_falls_back_when_suggestion_owner_missing(self):
        self.nina.delete()
        form = self.get_add_form(
            {
                "from_suggestion": "1",
                "latitude": "51.5074",
                "longitude": "-0.1278",
                "details": "Some toilet",
            }
        )
        self.assertEqual(self.get_initial(form, "owner"), self.superuser)

    def test_normal_add_form_not_prefilled(self):
        form = self.get_add_form()
        self.assertEqual(self.get_initial(form, "name"), "")
        self.assertNotEqual(self.get_initial(form, "data_source"), "App upload")
        self.assertEqual(self.get_initial(form, "owner"), self.superuser)
