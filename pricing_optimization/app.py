import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import mlflow
from typing import Union

### 
# configurations 
###

class PredictionFeatures(BaseModel):
    model_key: str
    mileage: int
    engine_power: int
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

description = """
Welcome to the GetAround API ! This app is made to give you the optimum price at which you should rent your car on the GetAround app.
The model used for prediction is a Random Forest trained from data collected by the GetAround data scientits team.

## Machine Learning 

This machine learning endpoint predict the optimum rental price per day given your car features.

Endpoints:

* `/predict`
"""

tags_metadata = [
    {
        "name": "Machine Learning",
        "description": "Prediction Endpoint."
    }
]

app = FastAPI(
    title="🚘📲 pricing-predictor API",
    description=description,
    version="0.1",
    contact={
        "name": "Baptiste Cournault",
        "url": "https://github.com/croustibats",
    },
    openapi_tags=tags_metadata
)

###
# endpoints 
###

@app.get("/")
async def index():

    message = "Hello there! This `/` is the most simple and default endpoint. If you want to learn more, check out documentation of the api at `/docs`"

    return message

@app.post("/predict", tags=["Machine Learning"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Prediction of rental price per day for a given getaround car

    You must fill in :

    * model_key : Citroën Peugeot, PGO, Renault, Audi, BMW, Ford, Mercedes, Opel,
                  Porsche, Volkswagen, KIA Motors, Alfa Romeo, Ferrari, Fiat, 
                  Lamborghini, Maserati, Lexus, Honda, Mazda, Mini, Mitsubishi,
                  Nissan, SEAT, Subaru, Suzuki, Toyota, Yamaha
    * mileage : enter numerical value
    * engine_power : enter numerical value
    * fuel : diesel, petrol, hybrid_petrol, electro
    * paint_color : black, grey, white, red, silver, blue, orange, beige, brown, green
    * car_type : convertible, coupe, estate, hatchback, sedan, subcompact, suv, van
    * private_parking_available : True, False
    * has_gps : True, False
    * has_air_conditioning : True, False
    * automatic_car : True, False
    * has_getaround_connect : True, False
    * has_speed_regulator : True, False
    * winter_tires : True, False
    """
    # Read data 
    car_features = pd.DataFrame({
        "model_key": [predictionFeatures.model_key],
        "mileage": [predictionFeatures.mileage],
        "engine_power": [predictionFeatures.engine_power],
        "fuel": [predictionFeatures.fuel],
        "paint_color": [predictionFeatures.paint_color],
        "car_type": [predictionFeatures.car_type],
        "private_parking_available": [predictionFeatures.private_parking_available],
        "has_gps": [predictionFeatures.has_gps],
        "has_air_conditioning": [predictionFeatures.has_air_conditioning],
        "automatic_car": [predictionFeatures.automatic_car],
        "has_getaround_connect": [predictionFeatures.has_getaround_connect],
        "has_speed_regulator": [predictionFeatures.has_speed_regulator],
        "winter_tires": [predictionFeatures.winter_tires]
        })

    # Log model from mlflow 
    logged_model = 'runs:/e7b55ffde42e46feb1033e76f85e70f3/pricing_optimization'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(car_features)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
    # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)