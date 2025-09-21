from typing import Any, Dict
from pydantic import BaseModel
from app.types.common import CommonState

class UserSignup(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str

class GenerateSignupFormState(CommonState):
    pass


class SignupWithDetailsState(CommonState):
    details: Dict[str, Any]
