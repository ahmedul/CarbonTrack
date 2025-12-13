import json
from mangum import Mangum
from app.main import app

# Mangum adapter for AWS Lambda
handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
