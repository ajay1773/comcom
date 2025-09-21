# Authentication Middleware

This auth middleware provides JWT-based authentication for protected workflows in the application. It acts as a middleware layer that can be plugged in front of any workflow that requires authentication.

## Architecture

The auth middleware follows these principles:

1. **Middleware Pattern**: Similar to Express.js middleware, it intercepts requests before they reach protected workflows
2. **JWT Token Validation**: Uses the existing JWT service to validate tokens
3. **Conditional Routing**: Routes to different nodes based on token validity
4. **Error Handling**: Provides user-friendly error messages via LLM

## Components

### State (`types.py`)

- `AuthMiddlewareState`: Extends CommonState with auth-specific fields
- Tracks token validity, user ID, target workflow, and error messages

### Nodes

- `parse_token`: Validates JWT token from global state
- `should_token_validate`: Conditional edge function for routing
- `handle_valid_token`: Processes successful authentication
- `handle_invalid_token`: Generates user-friendly error messages

### Graph (`graph.py`)

- Defines the auth middleware workflow as a LangGraph subgraph
- Entry point → parse_token → conditional routing → exit

### Runner (`nodes/runner.py`)

- Integrates auth middleware with global state
- Updates authentication status in global state
- Handles workflow continuation or termination

## Usage

### Protected Workflows

The middleware is automatically applied to protected workflows:

- `product_search` → `auth_protected_product_search_workflow`
- `place_order` → `auth_protected_place_order_workflow`

### Flow

1. User makes request to protected workflow
2. Auth middleware extracts token from `session_token` field
3. JWT token is validated
4. If valid: continues to target workflow with authenticated state
5. If invalid: returns error message and stops execution

### Adding New Protected Workflows

1. Create auth-protected wrapper function in `base.py`
2. Add new node name to `NodeName` enum
3. Update graph routing in `create_base_graph()`

## Example Usage

```python
# Token from Authorization header is stored in GlobalState
state = {
    "session_token": "eyJhbGciOiJIUzI1NiIs...",
    "user_message": "show me some shoes",
    "current_workflow": "product_search"
}

# Auth middleware automatically runs before product search
# If token is valid: user gets product search results
# If token is invalid: user gets friendly error message
```

## Integration Points

- **GlobalState**: Uses `session_token` field for JWT token
- **JWTService**: Leverages existing JWT validation logic
- **LLM Service**: Generates user-friendly error messages
- **Base Graph**: Integrated into main workflow routing
- **Error Handling**: Follows existing error handling patterns
