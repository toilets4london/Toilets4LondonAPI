# Toilets4LondonAPI

- This is a REST API built with Django Rest Framework
- Intended to be serve as a simple way to manage London toilet data
- Currently deployed at https://toilets4london.herokuapp.com/
- View simple map of data at https://toilets4london.herokuapp.com/toilets/view_map/

# Running Locally

1. Clone the repo `git clone https://github.com/toilets4london/Toilets4LondonAPI.git`
2. (Optional) Create a virtual environment to download all the packages - `python3 -m venv env` and activate it `source env/bin/activate`
3. Install the requirements `pip install -r requirements.txt`
4. Go into `settings.py` and set `DEBUG = True` (remember to set back to False in production)
5. Run `python manage.py migrate` to set up the database
6. Run `python manage.py runserver` to run the development server on localhost
    
