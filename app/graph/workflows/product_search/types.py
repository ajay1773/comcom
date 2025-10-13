
from typing import Any, Dict, List
from app.types.common import CommonState, AuthState
from app.services.db.db import Product

    
class ProductSearchState(CommonState, AuthState):
    search_parameters: Dict[str, Any]
    search_results: List[Product]
    result_count: int
    # search_query, suggestions, thread_id, conversation_history inherited from CommonState
    # user_id, session_token, is_authenticated, auth_required inherited from AuthState


