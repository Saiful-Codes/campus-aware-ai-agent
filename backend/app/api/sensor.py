from fastapi import APIRouter, HTTPException
from app.services.sensor_service import get_latest_sensor_data

router = APIRouter(prefix="/sensor", tags=["sensor"])


@router.get("/latest")
def get_sensor_latest():
    data = get_latest_sensor_data()

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch sensor data")

    return data