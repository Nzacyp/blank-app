from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def consult():
    return {"report": "This is a consultation report"}

@router.get("/history/{user_id}")
def history(user_id: int):
    return {"history": f"Consultation history for user {user_id}"}