# How to work on Flask Backend
```bash
cd flask-api # go to the flask directory
```
```bash
python3 -m venv .venv #creates a new python environment for flask 
```
- this ^ will be ignored by git, so we all need to individually do it on our machines
```bash
. .venv/bin/activate # activate the environment
```

```bash
# For windows!
Set-ExecutionPolicy Bypass -Scope Process # prepare computer
. .venv\Scripts\Activate.ps1 # activate the environment
```
```bash
pip install -r requirements.txt # install dependencies
```


## Running the application for test Purposes

#### Make sure you are in flask-api/src folder
```bash
cd flask-api/src
```

#### Simply Running the App
```bash
cd flask-api
cd src
python application.py
```

```bash
flask --app application run
```
#### Watch Mode
This will update website (after refreshing the page) with changes to code
```bash
flask --app application --debug run 
```