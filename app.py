# main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import logging
from schema.user_input import UserInput
from schema.prediction_response import PredictionResponse
from model.predict import predict_output, model, MODEL_VERSION

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Insurance Premium Prediction API", version=MODEL_VERSION)


# -------------------------------------------
# Root endpoint (Human-readable)
@app.get('/')
def home():
    """
    Root endpoint to verify the API is live.
    Useful for developers or human-readable check.
    """
    return JSONResponse(
        status_code=200,
        content={'message': 'Welcome to the Insurance Premium Prediction API'}
    )


# -------------------------------------------
# Health check endpoint (Machine-readable)
@app.get('/health')
def health_check():
    """
    Machine-readable health check used by monitoring tools like
    AWS Load Balancers, Kubernetes, etc.
    """
    return {
        'status': 'ok',
        'version': MODEL_VERSION,
        'model_loaded': model is not None,
    }


# -------------------------------------------
# Prediction endpoint
@app.post('/predict', response_model= PredictionResponse)
def predict_premium(data: UserInput):
    """
    Predict insurance premium category based on user input.

    Args:
        data (UserInput): Input features as a Pydantic schema

    Returns:
        JSON: Predicted category or error response
    """
    try:
        # Convert user input to dictionary (or directly to DataFrame if needed)
        user_input_dict = {
            'bmi': data.bmi,
            'age_group': data.age_group,
            'lifestyle_risk': data.lifestyle_risk,
            'city_tier': data.city_tier,
            'income_lpa': data.income_lpa,
            'occupation': data.occupation
        }

        logger.info(f"Received input: {user_input_dict}")

        # Generate prediction
        prediction = predict_output(user_input_dict)

        logger.info(f"Prediction result: {prediction}")

        return JSONResponse(
            status_code=200,
            content={'response': prediction}
        )

    except Exception as e:
        logger.exception("Prediction failed due to an internal error.")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
