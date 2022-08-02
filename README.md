# Sample streamlit project with docker and GCP deployment ready 

**Clone project**

`git clone https://github.com/yuong1979/streamlit_firebase.git`

**Change directory into the project**

`cd streamlit_firebase`

**Start a the virtual environment**

`python3 -m venv venv`

**Run the virtual environment**

`source venv/bin/activate`

**Install the requirements**

`pip install -r requirements.txt`

**Create a serviceaccountkey to connect to firestore**

**Create a firebase app config key to connect to firebase auth**

**Insert both json files in the streamlit_firebase directory**

### Deploy on local without docker

**Run the server only local**

`streamlit run app.py`

Access app through url http://localhost:5000/


### Deploy with docker on local

Comment out the production code on Dockerfile

**Build the image**

`docker build -t finapp .`

**Deploy the image**

`docker run -p 8501:8501 finapp`

Access app through url http://localhost:5000/


### Deploy with docker on production

Comment out the development code on Dockerfile

**Initialize gcloud**

`gcloud init`

**Build image**

`gcloud builds submit --tag gcr.io/test-python-api-spreadsheets/flaskapp`

**Deploy image**

`gcloud run deploy --image gcr.io/test-python-api-spreadsheets/flaskapp`




<!-- export FLASK_APP=app.py
export FLASK_ENV=development
flask run -->
