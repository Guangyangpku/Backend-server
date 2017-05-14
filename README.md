# flask-server
## Usage:
* Recreate the Flask env by: pip install -r requirements.txt
* export environment variables: MAIL_USERNAME and MAIL_PASSWORD
* for the Spark installation, please follow the official instruction. (Optional)
* run server by: python manage.py runserver --host "hostname"

## Structure:
* app/api_1.0: a Restful API for android app
* app/auth: contains cookie based authentication
* app/main: API for normal web application
* models: contains the ORM implimentation of our database and Sklearn based recommendation.
* spark_als: CF algorithm implementation
