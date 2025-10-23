# Quick Start Guide - Rate Limiting

## 🚀 Installation

```bash
# Install dependencies
cd /Users/ajaykumar/Desktop/personals/comcom
uv sync

# Initialize database (creates new tables)
uv run python main.py
# Or start the server - it will auto-initialize
uvicorn main:app --reload
```

## ✅ System Status

**Implementation**: Complete and Tested  
**Status**: Production Ready

## 📊 Current Limits

| User Type      | Limit          | Window   | Tracking   |
| -------------- | -------------- | -------- | ---------- |
| **Logged-Out** | 20 requests    | Per hour | IP Address |
| **Logged-In**  | 100,000 tokens | Per day  | User ID    |

## 🔧 How to Adjust Limits

### Method 1: Environment Variables (Recommended)

Create/edit `.env` file:

```bash
# For logged-out users
RATE_LIMIT_REQUESTS_PER_HOUR=20
RATE_LIMIT_WINDOW_HOURS=1

# For logged-in users
DAILY_TOKEN_LIMIT=100000
TOKEN_LIMIT_RESET_HOUR=0
```

### Method 2: Direct Config (app/core/config.py)

```python
RATE_LIMIT_REQUESTS_PER_HOUR = 20        # Change this
DAILY_TOKEN_LIMIT = 100000               # Change this
```

## 📝 Testing

### Test Logged-Out User (20 requests limit)

```bash
# Make multiple requests without auth
for i in {1..21}; do
  echo "Request $i"
  curl -X POST http://localhost:8000/api/chat/stream \
    -H "Content-Type: application/json" \
    -d '{"query": "Hello", "thread_id": "test"}'
done
# Request 21 should return 429
```

### Test Logged-In User (token limit)

```bash
# Check your current status
curl http://localhost:8000/api/rate-limit/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Make a chat request
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about your products", "thread_id": "test123"}'
```

## 🎯 What Happens When Limits Are Reached

### Logged-Out User (After 20 requests)

```json
HTTP 429 Too Many Requests
{
  "error": "Rate limit exceeded",
  "message": "Maximum 20 requests per hour. Please sign in for higher limits.",
  "retry_after": 3456,
  "suggestion": "Please sign in to continue chatting with higher limits."
}
```

### Logged-In User (After 100k tokens)

```json
HTTP 429 Too Many Requests
{
  "error": "Daily token limit exceeded",
  "message": "You have reached your daily token usage limit. Your limit will reset tomorrow.",
  "tokens_used": 100500,
  "daily_limit": 100000,
  "reset_date": "2025-10-19"
}
```

## 🔍 Monitoring

### Check Rate Limit Status

```bash
# For any user (authenticated or not)
GET /api/rate-limit/status
```

### View Application Metrics

```bash
# View all metrics
GET /api/metrics
```

## 👨‍💼 Admin Functions

These require code access (add to your admin panel later):

```python
from app.services.rate_limiter import rate_limiter_service

# Reset a user's daily tokens
await rate_limiter_service.reset_user_daily_tokens(user_id=123)

# Give user custom token limit (e.g., premium user)
await rate_limiter_service.update_user_token_limit(
    user_id=123,
    new_limit=250000  # 2.5x normal limit
)

# Check specific user's status
status = await rate_limiter_service.get_user_token_status(user_id=123)
print(status)
```

## 📂 Key Files

| File                                   | Purpose                         |
| -------------------------------------- | ------------------------------- |
| `app/services/rate_limiter.py`         | Main rate limiting logic        |
| `app/services/token_counter.py`        | Token counting                  |
| `app/api/routes/chat.py`               | Rate limit enforcement          |
| `app/services/stream.py`               | Token tracking during streaming |
| `app/core/config.py`                   | Configuration                   |
| `docs/RATE_LIMITING_IMPLEMENTATION.md` | Full documentation              |

## 🐛 Troubleshooting

### Issue: Users getting blocked too early

**Solution**: Increase `RATE_LIMIT_REQUESTS_PER_HOUR` or `DAILY_TOKEN_LIMIT`

### Issue: Token counts seem wrong

**Solution**: Check logs for token counting. Verify tiktoken is installed: `pip show tiktoken`

### Issue: Limits not resetting

**Solution**: Check `TOKEN_LIMIT_RESET_HOUR` setting. Verify database has new tables.

### Issue: Database errors

**Solution**: Re-run database initialization:

```bash
# Delete and recreate
rm app_database.sqlite
uv run python main.py
```

## 📱 Frontend Integration Ideas

1. **Show usage badge**: Display remaining tokens/requests in UI
2. **Progress bar**: Visual indicator of quota usage
3. **Warning popup**: Alert at 80% usage
4. **Upgrade prompt**: When limit reached, offer sign-in or upgrade
5. **Token costs**: Show estimated token cost before sending

Example UI text:

- "15 messages remaining this hour"
- "97,550 tokens remaining today (97.6%)"
- "⚠️ You're at 85% of your daily limit"

## 🚀 Next Steps

1. ✅ **Done**: Basic implementation
2. **Recommended**: Add frontend display of limits
3. **Optional**: Implement tiered user limits
4. **Future**: Analytics dashboard for usage patterns

## 📞 Quick Reference

```bash
# Start server
uvicorn main:app --reload

# Check rate limit status
curl http://localhost:8000/api/rate-limit/status

# Test chat (no auth)
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello"}'

# Test chat (with auth)
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello"}'
```

## ✨ Summary

✅ **Logged-out users**: 20 requests/hour (IP-based)  
✅ **Logged-in users**: 100,000 tokens/day (~50-100 conversations)  
✅ **Automatic reset**: Hourly for requests, daily for tokens  
✅ **Clear errors**: Users know why they're blocked and when they can retry  
✅ **Admin controls**: Adjust limits per user if needed  
✅ **Production ready**: Fully tested and documented

---

**Need help?** See `docs/RATE_LIMITING_IMPLEMENTATION.md` for detailed documentation.
