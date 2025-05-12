from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os
from datetime import datetime
import json

app = FastAPI()

# Retrieve COS URL and Bearer token from environment variables
COS_URL = os.getenv("COS_URL")  # e.g., "https://s3.us-south.cloud-object-storage.appdomain.cloud/leavedetails/op14.txt"
BEARER_TOKEN = os.getenv("BEARER_TOKEN")  # Your IAM token for COS
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # The secret you set in watsonx Assistant

security = HTTPBearer()

@app.post("/cdr-log")
async def receive_and_store(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify the secret token
    if credentials.credentials != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Get current UTC time
    current_time = datetime.utcnow().isoformat() + "Z"

    # Prepare the data to be stored
    data = {
        "timestamp": current_time
    }

    # Store the timestamp in COS
    response = requests.put(
        COS_URL,
        headers={
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )

    if response.status_code == 200:
        return {"status": "Timestamp logged to COS"}
    else:
        raise HTTPException(status_code=500, detail="Failed to upload timestamp to COS")
