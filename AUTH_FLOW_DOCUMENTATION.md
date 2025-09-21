# Authentication Flow Documentation

## Overview

The authentication system uses a structured 3-node workflow with interrupts to handle user registration and signin. The flow is designed to be conversational, secure, and seamlessly integrate with protected workflows.

## Architecture

### Core Components

1. **Auth Guard** (`app/services/auth_guard.py`)

   - Protects workflows: `place_order`, `initiate_payment`, `payment_status`
   - Redirects unauthenticated users to auth workflow
   - Preserves pending workflow for resumption after auth

2. **Auth Workflow** (`app/graph/subgraphs/auth/graph.py`)

   - 3-node structured flow with smart routing
   - Uses interrupts for proper state management
   - Handles both signin and signup flows

3. **Auth Service** (`app/services/auth.py`)
   - Database operations (user creation, authentication)
   - Session management (thread-based sessions)
   - Password hashing and validation

## Workflow Nodes

### 1. Request Email Node (`request_email.py`)

**Purpose:** Initial entry point that requests user email

**Triggers:**

- User says "I want to register" or "I want to sign in"
- Auth Guard redirects from protected workflow

**Logic:**

- Checks if user is already authenticated
- Determines intent (register/signin/generic)
- Asks for email address

**Output:**

```json
{
  "template": "request_email",
  "payload": {
    "intent": "register|signin|auth",
    "message": "What's your email address?"
  }
}
```

### 2. Check Email Exists Node (`check_email_exists.py`)

**Purpose:** Validates email and determines signin vs signup flow

**Triggers:**

- User provides valid email format

**Logic:**

- Validates email format
- Checks if user exists in database
- Sets auth flow direction (signin/signup)
- Stores email in workflow state

**Output for Existing User (Signin):**

```json
{
  "template": "request_credentials",
  "payload": {
    "flow_type": "signin",
    "email": "user@example.com",
    "fields_needed": ["password"]
  }
}
```

**Output for New User (Signup):**

```json
{
  "template": "request_credentials",
  "payload": {
    "flow_type": "signup",
    "email": "user@example.com",
    "fields_needed": ["password", "first_name", "last_name"]
  }
}
```

### 3. Process Credentials Node (`process_credentials.py`)

**Purpose:** Processes signin/signup credentials and creates sessions

**Triggers:**

- User provides credentials after email check

**Signin Logic:**

- Validates password against stored hash
- Creates session on success
- Updates user state and profile

**Signup Logic:**

- Parses structured credential format
- Validates all required fields
- Creates new user account and session

**Credential Format for Signup:**

```
Password: [your password]
First Name: [your first name]
Last Name: [your last name]
```

**Success Output:**

```json
{
  "template": "signin_success|signup_success",
  "payload": {
    "user": {user_profile},
    "continue_workflow": "place_order|null"
  }
}
```

## Flow Examples

### Registration Flow

```
1. User: "I want to register"
   → Classifier: Intent = "auth"
   → Auth Workflow: request_email_node
   → Response: "Great! Let's create a new account for you. What's your email address?"

2. User: "john@example.com"
   → check_email_exists_node
   → Database check: User doesn't exist
   → Sets: auth_flow="signup", email="john@example.com"
   → Response: "I don't see an account with that email. Let's create a new account!
              Please provide your details in this format:
              Password: [your password]
              First Name: [your first name]
              Last Name: [your last name]"

3. User: "Password: mypassword123
          First Name: John
          Last Name: Doe"
   → process_credentials_node
   → Parses credentials, validates format
   → Creates user account with hashed password
   → Creates session linked to thread_id
   → Response: "Welcome John! Your account has been created and you're signed in.
              How can I help you?"
```

### Signin Flow

```
1. User: "I want to sign in"
   → Auth Workflow: request_email_node
   → Response: "Perfect! Please provide your email address to sign in."

2. User: "john@example.com"
   → check_email_exists_node
   → Database check: User exists
   → Sets: auth_flow="signin", email="john@example.com"
   → Response: "I found your account! Please provide your password to sign in."

3. User: "mypassword123"
   → process_credentials_node
   → Validates password against hash
   → Creates session linked to thread_id
   → Response: "Welcome back, John! You're now signed in. How can I help you?"
```

### Protected Workflow Flow

```
1. User: "I want to buy shoes"
   → Classifier: Intent = "place_order"
   → Orchestrator: Workflow = "place_order"
   → Auth Guard: User not authenticated
   → Sets: pending_workflow="place_order", current_workflow="auth"
   → Response: "To place an order, I need you to sign in first.
              Please provide your email address to continue."

2. [User completes authentication flow]
   → process_credentials_node: Authentication successful
   → Checks: pending_workflow="place_order"
   → Sets: current_workflow="place_order", pending_workflow=null
   → Response: "Welcome back, John! You're now signed in.
              Let's continue with your place order request."
   → Workflow continues to place_order
```

## State Management

### Global State Fields

```python
{
  "user_id": int | None,           # Authenticated user ID
  "session_token": str | None,     # Session token
  "is_authenticated": bool,        # Auth status
  "auth_required": bool,           # Whether auth is needed
  "pending_workflow": str | None,  # Workflow waiting for auth
  "thread_id": str,               # Chat thread ID
  "user_profile": dict            # User information
}
```

### Workflow State Fields

```python
{
  "email": str,                   # User's email
  "auth_flow": "signin|signup",   # Flow direction
  "user_exists": bool            # Whether user exists
}
```

## Session Management

### Thread-Based Sessions

- Sessions are linked to chat `thread_id`
- Stored in `user_sessions` table with expiration
- Default session duration: 7 days
- Automatic cleanup of expired sessions

### Session Lifecycle

1. **Creation:** After successful signin/signup
2. **Validation:** On each protected workflow access
3. **Expiration:** Automatic after 7 days
4. **Cleanup:** Periodic removal of expired sessions

## Security Features

### Password Security

- **Hashing:** bcrypt with salt
- **Validation:** Minimum 8 characters
- **Storage:** Only hashed passwords stored

### Input Validation

- **Email format:** Regex validation
- **Required fields:** All signup fields mandatory
- **Error handling:** Clear validation messages

### Session Security

- **Unique tokens:** Cryptographically secure tokens
- **Expiration:** Time-based session expiry
- **Thread isolation:** Sessions tied to specific threads

## Error Handling

### Validation Errors

- Invalid email format
- Password too short
- Missing required fields
- Malformed credential format

### Authentication Errors

- Invalid password
- Account creation failures
- Session creation failures

### Recovery Options

- Clear error messages with retry instructions
- Format examples for credential input
- Graceful fallback to restart auth flow

## Integration Points

### Frontend Templates

- `request_email`: Email input form
- `request_credentials`: Credential input (signin/signup)
- `signin_success`: Welcome back message
- `signup_success`: Account created message
- `auth_error`: Error display with retry
- `validation_error`: Field validation errors

### Database Tables

- `users`: User accounts with hashed passwords
- `user_sessions`: Active sessions with expiration
- `user_addresses`: User shipping/billing addresses

### Workflow Integration

- **Auth Guard:** Automatic protection for sensitive workflows
- **Interrupts:** Proper workflow pausing and resumption
- **State Persistence:** Maintains context across auth flow

## Performance Considerations

### Database Queries

- Indexed email lookups
- Efficient session validation
- Batch cleanup of expired sessions

### Memory Management

- Minimal state storage
- Automatic state cleanup
- Thread-based isolation

### Scalability

- Stateless node design
- Database-backed sessions
- Horizontal scaling ready

## Monitoring and Debugging

### Logging

- Auth flow progression
- Email validation results
- Session creation/validation
- Error conditions with context

### Metrics

- Authentication success/failure rates
- Session duration statistics
- Workflow interruption frequency
- Error type distribution
