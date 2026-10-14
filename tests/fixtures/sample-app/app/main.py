"""Fictional gym booking API (synthetic fixture)."""
from fastapi import FastAPI

app = FastAPI(title="Gym booking")
CLASSES = {1: {"name": "Yoga", "capacity": 10, "booked": 0}}


@app.post("/reservations/{class_id}")
def reserve(class_id: int):
    item = CLASSES[class_id]
    item["booked"] += 1
    return {"class": item["name"], "booked": item["booked"]}
