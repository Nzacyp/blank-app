from fastapi import FastAPI
from routes import auth, consult

app = FastAPI(title="Medical Consultation API")

app.include_router(auth.router, prefix="/auth")
app.include_router(consult.router, prefix="/consult")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Consultation API"}