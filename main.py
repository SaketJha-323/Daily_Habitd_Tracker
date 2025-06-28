from fastapi import FastAPI
from auth import router as auth_router
from habits import router as habits_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(habits_router)

@app.get("/")
def root():
    return {"msg": "Daily Habits Tracker API is running!"}