from typing import Dict
from app.models.user import User
from app.types.common import CommonState
    
class GenerateSigninFormState(CommonState):
    pass

class LoginWithCredentialsState(CommonState):
    credentials: Dict[str, str]
    user: User | None
    is_authenticated: bool
    user_id: int | None