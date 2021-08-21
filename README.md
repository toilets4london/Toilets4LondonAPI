# Toilets4LondonAPI

- This is a REST API built with Django Rest Framework
- Intended to be serve as a simple way to manage London toilet data
- iOS app at https://apps.apple.com/us/app/toilets4london/id1543000174
- Android app at https://play.google.com/store/apps/details?id=com.toilets4london.toiletapp
- Basic web app at https://app.toilets4london.com/
- Due to an unfortunate incident when someone attempted to resubmit the iOS app to the app store under a different name with some hidden malicious code, the Swift and Kotlin native app codebases have been closed sourced. If you are interested in getting access to these codebases for educational purposes, to use as the basis of a different app or simply out of interest, feel free to [get in touch](https://www.toilets4london.com/).

## Running Locally

1. Clone the repo `git clone https://github.com/toilets4london/Toilets4LondonAPI.git`
2. cd into the project directory `cd Toilets4LondonAPI`
3. (Optional but recommended) Create a virtual environment to download all the packages - `python3 -m venv env` and activate it `source env/bin/activate`
4. Install the requirements `pip install -r requirements.txt`
5. Go into `settings.py` and set `DEBUG = True` *(remember to set back to False in production)*
6. Run `python manage.py migrate` to set up the database
7. Run `python manage.py createsuperuser` to set up an admin account, following the instructions to add your email address and a password (for testing purposes these can be fake)
8. Run `python manage.py runserver` to run the development server on localhost
9. Navigate to http://127.0.0.1:8000/ or click the link generated by Django to see the browsable API
    
## Endpoints used by mobile apps

- GET all toilets `/toilets/?page_size=2000` (increase `page_size` if there are > 2000 toilets in the database)
- POST star rating { 'toilet' : *valid toilet id* , 'rating': *1-5 star rating* } `/ratings/`
- POST report a toilet { 'toilet' : *valid toilet id* , 'reason' : *valid reason code, see below* , 'other_description' : *text describing problem* } `/reports/`
- POST a suggested toilet { 'latitude': *lat coordinate of suggested toilet*, 'longitude': *long coordinate of suggested toilet*, 'details': *text describing toilet*} `/suggestedtoilets/`

| Problem                               | Report reason code |
| ------------------------------------- | ------------------ |
| This toilet does not exist            | "DNE"              |
| This toilet is very poorly maintained | "O"                |

## Creating an account (allows you to post more ratings / reports per day if you use the Authorization header)

- POST sign up { 'email' : *your email* , 'password' : *your password* } `/auth/users/`
- POST obtain api token { 'email' : *your email* , 'password' : *your password* } `/auth/token/login/`
- POST forgot password { 'email' : *your email* } `/reset-password/`
- POST reset password with token received by email { 'token' : *token in email* , 'password' : *your new password* } `/reset-password/confirm/`
- With an API token you can then use the header { 'Authorization' : *token [valid api token]* } for POST endpoints (`/ratings/` and `/reports/` )

## Example response for GET toilet

```json
{
    "url": "http://127.0.0.1:8000/toilets/2/",
    "id": 2,
    "data_source": "Dataset sent in by Healthmatic 26/10/20",
    "name": "Islington Green Automatic Public Toilet",
    "address": "Islington Green N1",
    "borough": "Islington",
    "latitude": 51.536241,
    "longitude": -0.1024704,
    "opening_hours": "24 hr",
    "wheelchair": true,
    "baby_change": false,
    "fee": "20p",
    "covid": "",
    "rating": null,
    "open": true
}
```
