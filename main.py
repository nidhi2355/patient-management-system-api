from fastapi import FastAPI
import json

app= FastAPI()

# function to retrieve data from json file in read mode
def load_data():
    with open('patients.json', 'r') as f:
        data= json.load(f)

    return data

@app.get("/")
def hello():
    return {'message': 'Patient Management System API'}


@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}


#endpoint to view all patiennts data
@app.get('/view')
def view():
    data= load_data()
    return data