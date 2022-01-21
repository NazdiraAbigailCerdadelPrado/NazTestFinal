# Cisco Meraki Speech Recognition Module 

## Internal Structure and File Organization.-
The web application structure is based on a clean architecture template based on the Flask Web Development 2nd edition book by Miguel Grinberg:
* Templates: Contains the HTML files for every page of the app.
* application.py: The main python function of the program.
* s3bucket.py: The main python file that functions for the automatizatization of the speech recognition tasks.

## Personalization.-
This app can be deployed for different companies. To adapt the app for different companies the following components must be modified in the App Settings tab:
* Company name
* Company logo

After wirting the information required and uploading the company logo, it is necessary to submit the changes for the web app to change its template with the personalized information.

## How to run.-
### At powershell:
1. Clone this repository
>```` git clone ````
* Install Python 3.9.7
2. Open PowerShell as an administrator and run the following commands:
* Create a new environment
>```` python -m venv venv ````
* Activate the environment
. .\venv\Scripts\Activate.ps1
* Upgrade the pip and install the project requirements
>```` pip install --upgrade pip ````
>```` pip install -r requirements.txt ````
3. Create APPLICATION environment variable
>```` $env:FLASK_APP=”application.py” ````
4. Run de application on localhost (Only for development)
>```` flask run ````

* The application will run most likely on http://localhost:5000

### At Ubuntu Linux:
1. Clone this repository
>```` git clone ````
2. Create an new virtual environment. In a terminal window, cd to the project directory and run:
>```` python -m venv venv ````
>```` . venv/bin/activate ````
* Upgrade the pip and install the project requirements
>```` pip install --upgrade pip ````
>```` pip install -r requirements.txt ````
3. Create APPLICATION environment variable
>```` export FLASK_APP=application.py ````
4. Run de application
>````

