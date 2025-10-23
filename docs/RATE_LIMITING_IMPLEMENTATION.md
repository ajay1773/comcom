# Rate Limiting & Token Usage Tracking Implementation

## Overview

This document describes the comprehensive rate limiting and token usage tracking system implemented for the ComCom chatbot application.

## Features

### 1. **Logged-Out Users (Guest Users)**

- **Rate Limit**: 20 requests per hour (IP-based)
- **Tracking Method**: IP address
- **Enforcement**: Requests are blocked after limit is reached
- **Reset**: Every hour (rolling window)
- **Error Response**: HTTP 429 with suggestion to sign in

### 2. **Logged-In Users (Authenticated Users)**

- **Rate Limit**: 100,000 tokens per day
- **Tracking Method**: User ID with actual token consumption
- **Enforcement**: Requests are blocked when daily token quota is exceeded
- **Reset**: Daily at midnight (configurable)
- **Token Counting**: Uses tiktoken library for accurate token estimation

## Architecture

### Database Schema

#### `user_token_usage` Table

Tracks daily token usage for authenticated users:

```sql
CREATE TABLE user_token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    daily_limit INTEGER DEFAULT 100000,
    reset_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(user_id, reset_date)
)
```

#### `rate_limit_tracking` Table

Tracks request counts for IP addresses (logged-out users):

```sql
CREATE TABLE rate_limit_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    request_count INTEGER DEFAULT 0,
    window_start DATETIME NOT NULL,
    window_end DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip_address, window_start)
)
```

### Services

#### `RateLimiterService` (`app/services/rate_limiter.py`)

Main service for rate limiting and token tracking:

**Key Methods:**

- `check_rate_limit_for_ip(ip_address)` - Check request limit for logged-out users
- `check_token_limit_for_user(user_id)` - Check token limit for logged-in users
- `record_token_usage(user_id, tokens_used)` - Record token consumption
- `get_user_token_status(user_id)` - Get current usage status
- `update_user_token_limit(user_id, new_limit)` - Admin function to adjust limits
- `reset_user_daily_tokens(user_id)` - Admin function to reset usage

#### `TokenCounterService` (`app/services/token_counter.py`)

Service for counting LLM tokens:

**Key Methods:**

- `count_tokens(text)` - Count tokens in text
- `count_messages_tokens(messages)` - Count tokens in conversation
- `estimate_completion_tokens(prompt, completion)` - Estimate for prompt-completion pairs

### API Endpoints

#### `POST /api/chat/stream`

Main chat endpoint with integrated rate limiting:

**Behavior:**

- **Logged-out users**: Checks IP-based rate limit before processing
- **Logged-in users**: Checks token quota before processing
- Returns HTTP 429 if limit exceeded with detailed error message
- Tracks token usage in real-time during streaming
- Sends token usage info to client after each conversation

**Error Response (429 - Rate Limit Exceeded):**

```json
{
  "error": "Rate limit exceeded",
  "message": "Rate limit exceeded. Maximum 20 requests per hour. Please sign in for higher limits.",
  "retry_after": 3456,
  "limit_type": "requests",
  "suggestion": "Please sign in to continue chatting with higher limits."
}
```

**Token Usage Event (sent to client):**

```json
{
  "event_name": "token_usage",
  "prompt_tokens": 45,
  "completion_tokens": 312,
  "total_tokens": 357,
  "tokens_used_today": 2450,
  "remaining_tokens": 97550,
  "daily_limit": 100000
}
```

#### `GET /api/rate-limit/status`

Check current rate limit status:

**Logged-in User Response:**

```json
{
  "user_type": "authenticated",
  "user_id": 123,
  "tokens_used": 2450,
  "remaining_tokens": 97550,
  "daily_limit": 100000,
  "reset_date": "2025-10-19",
  "limit_type": "tokens"
}
```

**Logged-out User Response:**

```json
{
  "user_type": "guest",
  "ip_address": "192.168.1.1",
  "remaining_requests": 15,
  "limit": 20,
  "reset_time": "2025-10-18T15:00:00",
  "limit_type": "requests"
}
```

## Configuration

Settings in `app/core/config.py`:

```python
# Rate Limiting Configuration
# For logged-out users (IP-based)
RATE_LIMIT_REQUESTS_PER_HOUR: int = 20
RATE_LIMIT_WINDOW_HOURS: int = 1

# For logged-in users (token-based)
DAILY_TOKEN_LIMIT: int = 100000  # ~50-100 conversations per day
TOKEN_LIMIT_RESET_HOUR: int = 0  # Reset at midnight
```

### Environment Variables

You can override defaults in `.env`:

```bash
RATE_LIMIT_REQUESTS_PER_HOUR=20
RATE_LIMIT_WINDOW_HOURS=1
DAILY_TOKEN_LIMIT=100000
TOKEN_LIMIT_RESET_HOUR=0
```

## Token Limit Recommendations

### Why 100,000 Tokens Per Day?

**Calculation:**

- Average conversation: 10-20 messages
- Average message: 50-100 tokens (user) + 200-500 tokens (assistant)
- Average tokens per conversation: ~1,000-2,000 tokens
- 100,000 tokens = **50-100 conversations per day**

**Adjusting Limits:**

- **Light users**: 50,000 tokens (25-50 conversations)
- **Normal users**: 100,000 tokens (50-100 conversations)
- **Power users**: 250,000 tokens (125-250 conversations)
- **Premium/Enterprise**: Unlimited or custom limits

## Implementation Flow

### Logged-Out User Request Flow

```
1. User sends message (no auth token)
2. Extract IP address from request
3. Check rate_limit_tracking table
4. If < 20 requests in current hour window:
   - Increment counter
   - Process request
5. If >= 20 requests:
   - Return HTTP 429 with error
   - Suggest user to sign in
```

### Logged-In User Request Flow

```
1. User sends message (with auth token)
2. Verify token and get user_id
3. Check user_token_usage table for today
4. If tokens_used < daily_limit:
   - Process request
   - Track tokens during streaming
   - Record token usage after completion
5. If tokens_used >= daily_limit:
   - Return HTTP 429 with error
   - Show reset date
```

## Token Tracking During Streaming

The system tracks tokens in real-time:

1. **Before streaming**: Count prompt tokens from user message
2. **During streaming**: Accumulate all streamed text
3. **After streaming**: Count completion tokens from accumulated response
4. **Record usage**: Save total tokens to database
5. **Notify client**: Send token usage event via SSE

## Maintenance & Cleanup

### Automatic Cleanup

- **Rate limit records**: Auto-deleted after 24 hours
- **Token usage records**: Auto-deleted after 30 days

### Manual Cleanup

You can trigger cleanup manually:

```python
# Clean up old rate limit records
await rate_limiter_service._cleanup_old_rate_limits()

# Clean up old token records
await rate_limiter_service.cleanup_old_token_records()
```

## Admin Functions

### Reset User's Daily Tokens

```python
await rate_limiter_service.reset_user_daily_tokens(user_id)
```

### Update User's Token Limit

```python
# Set custom limit for specific user
await rate_limiter_service.update_user_token_limit(user_id, 250000)
```

## Error Handling

### Rate Limit Exceeded (Logged-out)

- **HTTP 429** with retry_after seconds
- Clear message encouraging sign-in
- Client should show login prompt

### Token Limit Exceeded (Logged-in)

- **HTTP 429** with reset date
- Clear message about daily limit
- Client should show upgrade prompt or wait message

### Edge Cases Handled

- Invalid IP addresses (fallback to "unknown")
- Missing tokens (treat as logged-out)
- Database errors (graceful degradation)
- Token counting failures (fallback estimation)

## Testing

### Test Logged-Out User Rate Limiting

```bash
# Make 21 requests from same IP
for i in {1..21}; do
  curl -X POST http://localhost:8000/api/chat/stream \
    -H "Content-Type: application/json" \
    -d '{"query": "Hello", "thread_id": "test"}' &
done

# 21st request should return 429
```

### Test Logged-In User Token Tracking

```bash
# Check current status
curl http://localhost:8000/api/rate-limit/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Make requests until limit exceeded
# Monitor token usage in response
```

## Monitoring

### Metrics to Track

- Total requests blocked (logged-out users)
- Total requests blocked (token limit)
- Average tokens per conversation
- Users hitting token limits
- Peak usage times

### Logs

The system logs:

- Rate limit checks and violations
- Token usage per conversation
- User limit adjustments
- Cleanup operations

## Future Enhancements

1. **Dynamic Limits**: Adjust limits based on user tier/subscription
2. **Token Rollover**: Allow unused tokens to roll over to next day
3. **Burst Allowance**: Allow temporary bursts above limit
4. **Per-Workflow Limits**: Different limits for different workflows
5. **Cost Tracking**: Track actual API costs per user
6. **Analytics Dashboard**: Visualize usage patterns
7. **Warning Notifications**: Alert users at 80% usage

## Security Considerations

1. **IP Spoofing**: Rate limiting by IP is vulnerable to proxies/VPNs
2. **Token Exhaustion**: Users could intentionally exhaust tokens
3. **DDoS Protection**: Additional layer needed for distributed attacks
4. **Database Load**: High traffic requires caching layer

## Best Practices

1. **Monitor Usage**: Regularly check token usage patterns
2. **Adjust Limits**: Based on actual user behavior and costs
3. **Communicate Clearly**: Show users their usage and limits
4. **Provide Upgrades**: Offer higher limits for premium users
5. **Log Everything**: Track all rate limit events for analysis
