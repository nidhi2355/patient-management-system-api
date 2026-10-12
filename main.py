from fastapi import FastAPI , Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app= FastAPI()

# pydantic model 
class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the Patient')]
    city: Annotated[str, Field(..., description='City of the Patient')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the Patient')]
    gender: Annotated[Literal['male', 'female','other'], Field(..., description='Gender of the Patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the Patient n mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the Patient in kgs')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi= round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi<30:
            return 'Normal'
        else:
            return 'Obese'


# pydantic model to update patients-> we can't use the above model bcoz above all the fields are necessary so we cant just pass less details

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female','other']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]



# function to retrieve data from json file in read mode
def load_data():
    with open('patients.json', 'r') as f:
        data= json.load(f)

    return data


# function to save the dictionary format data in json file
def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

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


#endpoint to get a particular patients data
@app.get('/patient/{patient_id}')
def view_patient(patient_id : str = Path(..., description= 'ID of the patient in the DB', examples=['P001'])):
    #load all patients
    data= load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail= 'Patient not found')


#endpoint to fetch patients in a sorted format
#sort_by-> weight, height, bmi
#order-> ASC, DESC

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description= 'Sort on the bases of height, weight, bmi'), order: str = Query('asc', description= 'sort in ascending or descending order')):

    valid_fields= ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code= 400, detail='Invalid field. Select from {valid_fiels}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code= 400, detail='Invalid order. Select between asc and desc')

    data = load_data()

    sort_order= True if order=='desc' else False

    sorted_data= sorted(data.values(), key= lambda x: x.get(sort_by, 0), reverse= sort_order)

    return sorted_data


# create endpoint
@app.post('/create')
def create_patient(patient: Patient):

    #load existing data
    data= load_data()

    # check if the patient already exist(same pid)
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    
    #new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into json file
    save_data(data)

    # return a success response that patient created successfully
    return JSONResponse(status_code=201, content= {'message':'Patient created successfully'})


# edit endpoint
@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data= load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    patient_info= data[patient_id]

    updated_info= patient_update.model_dump(exclude_unset=True)

    for key, value in updated_info.items():
        patient_info[key]= value

    # any chanes in height or weight will also change bmi and verdict. so we need to create a new pydantic object from this updated dictionary patient_info so that we have our new bmi and verdict. after that we will convert it into dictionary and then push in our json file.

    # adding patient_id 
    patient_info[id]= patient_id
    patient_pydantic_object = Patient(**patient_info) # patient pydantic object

    patient_info= patient_pydantic_object.model_dump(exclude='id')

    data[patient_id]= patient_info

    save_data(data)

    return JSONResponse(status_code=200, content= 'Patient Updated')


# delete patient endpoint
@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    data= load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content='Patient Deleted successfully')