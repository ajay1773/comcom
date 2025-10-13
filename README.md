# 🛍️ ComCom - AI-Powered E-commerce Chatbot

**ComCom** is a sophisticated, conversational AI shopping assistant that provides a natural, intelligent e-commerce experience. Built with cutting-edge LLM technology and modern web frameworks, ComCom understands context, maintains conversation history, and helps users shop seamlessly through natural language interactions.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![React](https://img.shields.io/badge/React-19.1+-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.6+-purple.svg)

---

## ✨ Features

### 🤖 **Conversational AI Assistant**

- **Context-Aware**: Remembers previous messages and understands references like "that shirt" or "the blue one"
- **Intent Classification**: Automatically routes queries to appropriate workflows
- **Natural Language Understanding**: Powered by Groq's Llama 3.3 70B model
- **Conversation History**: Maintains context across entire shopping sessions

### 🛒 **Complete Shopping Experience**

- **Product Search**: Advanced full-text search with filters (price, brand, category, ratings, etc.)
- **Product Comparison**: Side-by-side comparison of products
- **Smart Cart Management**:
  - Add items with natural language ("add blue Nike shirt size large")
  - View cart contents
  - **Edit items contextually** ("change that to size XL", "make it 3 instead of 2")
  - Remove items
- **Checkout Flow**: Multi-step checkout with address selection and payment
- **Order Management**: View order history and track orders

### 👤 **User Management**

- **Authentication**: Secure JWT-based authentication
- **Profile Management**: View and update user profiles
- **Address Book**: Save, edit, and delete shipping addresses
- **Order History**: Track all past orders

### 🎯 **Advanced Workflows**

- **LangGraph State Machines**: Complex workflows with conditional branching
- **Auth Middleware**: Protected workflows with automatic authentication
- **Error Handling**: Graceful error recovery with user-friendly messages
- **Resilience Patterns**: Circuit breakers and retry logic for reliability

### 🎨 **Modern UI**

- **React 19**: Latest React with hooks and context
- **Tailwind CSS**: Beautiful, responsive design
- **shadcn/ui**: High-quality UI components
- **Real-time Updates**: Streaming responses for instant feedback
- **Dark Mode**: Built-in theme switching

---

## 🏗️ Architecture

### Backend Stack

- **FastAPI**: High-performance Python web framework
- **LangGraph**: Stateful workflow orchestration for AI agents
- **LangChain**: LLM integration and tool calling
- **Groq API**: Ultra-fast LLM inference
- **SQLite**: Embedded database for products, users, and conversations
- **Pydantic**: Type-safe data validation
- **JWT**: Secure authentication tokens

### Frontend Stack

- **React 19**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Lightning-fast build tool
- **Tailwind CSS v4**: Utility-first styling
- **Zustand**: Lightweight state management
- **Axios**: HTTP client
- **React Router**: Client-side routing

### AI/ML Components

- **Intent Classification**: LLM-based intent detection
- **Entity Extraction**: Structured output parsing
- **Conversation Context**: History-aware responses
- **Full-Text Search**: SQLite FTS5 for product search
- **Semantic Understanding**: Context-aware cart editing

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** (required)
- **Node.js 18+** (required for frontend)
- **pnpm** (recommended) or npm
- **Make** (usually pre-installed on Unix systems)
- **Groq API Key** (required) - [Get one here](https://console.groq.com/keys)

### Installation

#### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd comcom
```

#### 2. Set Up Environment Variables

```bash
# Copy the sample environment file
cp .env.sample .env

# Edit .env and add your keys
nano .env  # or use your favorite editor
```

**Required Environment Variables:**

```env
GROQ_API_KEY=your_groq_api_key_here    # Get from https://console.groq.com/keys
JWT_SECRET=your_jwt_secret_key_here    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

See [Environment Variables](#environment-variables) section for complete configuration options.

#### 3. Install Backend Dependencies

```bash
make install
```

This will:

- Create a virtual environment
- Install Python dependencies via `uv`
- Set up the database schema
- Seed initial product data

#### 4. Install Frontend Dependencies

```bash
cd client
pnpm install  # or npm install
cd ..
```

---

## 🎮 Running the Application

### Development Mode

#### Start Backend (Terminal 1)

```bash
make dev
```

The API will be available at `http://localhost:8000`

#### Start Frontend (Terminal 2)

```bash
cd client
pnpm dev  # or npm run dev
```

The UI will be available at `http://localhost:5173`

### Production Mode

#### Backend

```bash
make start
```

#### Frontend

```bash
cd client
pnpm build
pnpm preview
```

---

## 📚 API Documentation

Once the backend is running, access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

### Main Endpoints

#### Chat API

```
POST /api/chat
```

**Request:**

```json
{
  "query": "Show me blue Nike shoes",
  "thread_id": "optional-session-id",
  "user_id": 1,
  "session_token": "jwt-token"
}
```

**Response (Streaming):**

```json
{
  "type": "text_chunk",
  "content": "I found several blue Nike shoes...",
  "done": false
}
```

#### Conversations

```
GET  /api/conversations                    # List all conversations
GET  /api/conversations/{conversation_id}  # Get specific conversation
POST /api/conversations                    # Create new conversation
```

---

## 🔐 Authentication Flow

ComCom uses JWT-based authentication:

1. **Sign Up**: `user_message: "Sign up with email and password"`
2. **Sign In**: `user_message: "Login with email: user@example.com password: yourpassword"`
3. **Token Storage**: Frontend stores JWT token
4. **Protected Workflows**: Cart, checkout, orders require authentication
5. **Auto-redirect**: Unauthenticated users prompted to login

---

## 🛠️ Development Commands

### Backend

```bash
make dev         # Run development server with hot reload
make start       # Run production server
make install     # Install dependencies
make clean       # Clean Python cache files
make format      # Format code with black
make lint        # Run linting with ruff
make test        # Run tests (when implemented)
```

### Frontend

```bash
pnpm dev         # Start development server
pnpm build       # Build for production
pnpm preview     # Preview production build
pnpm lint        # Run ESLint
```

---

## 🌍 Environment Variables

### Required Variables

| Variable       | Description                      | Example                 | Required |
| -------------- | -------------------------------- | ----------------------- | -------- |
| `GROQ_API_KEY` | Groq API key for LLM inference   | `gsk_...`               | ✅ Yes   |
| `JWT_SECRET`   | Secret key for JWT token signing | `random-32-char-string` | ✅ Yes   |

### Optional Variables

| Variable                            | Description                   | Default                   | Required |
| ----------------------------------- | ----------------------------- | ------------------------- | -------- |
| `GROQ_MODEL`                        | Groq model to use             | `llama-3.3-70b-versatile` | ❌ No    |
| `LLM_TEMPERATURE`                   | Temperature for LLM (0.0-2.0) | `1.0`                     | ❌ No    |
| `OLLAMA_MODEL`                      | Local Ollama model (if used)  | `llama3.1:8b`             | ❌ No    |
| `DATABASE_URL`                      | LangGraph checkpoint database | `langgraph.sqlite`        | ❌ No    |
| `APP_DATABASE_URL`                  | Application database          | `app_database.sqlite`     | ❌ No    |
| `LOG_LEVEL`                         | Logging level                 | `INFO`                    | ❌ No    |
| `STREAM_JSON_BUFFER_SIZE`           | Streaming buffer size         | `10000`                   | ❌ No    |
| `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | Circuit breaker threshold     | `5`                       | ❌ No    |
| `CIRCUIT_BREAKER_RECOVERY_TIMEOUT`  | Recovery timeout (seconds)    | `60`                      | ❌ No    |
| `RETRY_MAX_ATTEMPTS`                | Max retry attempts            | `3`                       | ❌ No    |
| `RETRY_BASE_DELAY`                  | Base retry delay (seconds)    | `1.0`                     | ❌ No    |

### Generating Secure Keys

**JWT Secret:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Groq API Key:**

1. Visit [Groq Console](https://console.groq.com/keys)
2. Create a new API key
3. Copy and paste into `.env`

---

## 📖 Workflows Documentation

ComCom uses LangGraph for complex, stateful AI workflows:

### Core Workflows

1. **Product Search** (`product_search`)

   - Full-text search with FTS5
   - Advanced filtering (price, brand, category, rating, etc.)
   - Contextual suggestions

2. **Add to Cart** (`add_to_cart`)

   - Natural language product selection
   - Quantity and size specification
   - Duplicate detection

3. **View Cart** (`view_cart`)

   - Display cart items with product details
   - Calculate totals
   - Show cart summary

4. **Edit Cart** (`edit_cart`) ⭐ **NEW**

   - Context-aware editing: "change that to size large"
   - Quantity updates: "make it 3 instead of 2"
   - Remove items: "remove that shirt"
   - Replace products: "swap for the blue one"

5. **Checkout** (`checkout`)

   - Multi-step process
   - Address selection
   - Payment collection
   - Order creation

6. **Order View** (`order_view`)
   - View all orders
   - View specific order details
   - Order status tracking

### Authentication Workflows

- **Sign Up** (`generate_signup_form`, `signup_with_details`)
- **Sign In** (`generate_signin_form`, `login_with_credentials`)
- **Auth Middleware** (protects workflows automatically)

For detailed workflow documentation, see:

- `docs/EDIT_CART_IMPLEMENTATION_SUMMARY.md` - Edit cart feature
- `docs/AUTH_FLOW_DOCUMENTATION.md` - Authentication flows
- `docs/FALLBACK_WORKFLOW_DOCUMENTATION.md` - Fallback handling

---

## 🎯 Example Conversations

### Product Search

```
User: "Show me blue Nike shoes under $100"
ComCom: "I found 8 blue Nike shoes under $100. Here are the top matches:
         1. Nike Air Max - $89.99
         2. Nike Revolution 5 - $79.99
         ..."
```

### Context-Aware Cart Editing

```
User: "Add Summer Breeze T-shirt by Nike size M"
ComCom: "Added Summer Breeze T-shirt (M) to your cart!"

User: "Actually, make that size large"
ComCom: "Updated Summer Breeze T-shirt to size Large!"

User: "And I want 2 of them"
ComCom: "Updated quantity to 2. Your cart total is now $59.98"
```

### Order Placement

```
User: "I want to checkout"
ComCom: "Great! Let me prepare your checkout.
         Cart: 2 items - $59.98
         Select a shipping address:
         1. Home - 123 Main St
         2. Work - 456 Office Blvd
         ..."
```

---

## 🗄️ Database Schema

ComCom uses SQLite with two databases:

### 1. Application Database (`app_database.sqlite`)

- **users**: User accounts
- **products**: Product catalog (1000+ items seeded)
- **user_carts**: Shopping carts
- **cart_items**: Cart line items
- **orders**: Order records
- **order_items**: Order line items
- **user_addresses**: Saved addresses
- **user_sessions**: Session management

### 2. LangGraph Database (`langgraph.sqlite`)

- Conversation checkpoints
- Workflow state persistence
- Message history

---

## 🧪 Testing

### Backend Testing

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Frontend Testing

```bash
cd client
pnpm test
```

### Manual Testing

Use the provided test cases in `docs/ECOMMERCE_TEST_CASES.md`

---

## 🏭 Production Deployment

### Backend

1. **Set environment variables** in your hosting platform
2. **Use production ASGI server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
3. **Set up reverse proxy** (Nginx/Caddy)
4. **Enable HTTPS**
5. **Configure CORS** for your frontend domain

### Frontend

1. **Build optimized bundle**:
   ```bash
   cd client
   pnpm build
   ```
2. **Serve static files** via CDN or static hosting
3. **Update API endpoint** in `client/src/config/index.ts`

### Environment-Specific Config

**Backend `main.py`:**

```python
# Change CORS origins for production
allow_origins=["https://yourdomain.com"]
```

**Frontend `config/index.ts`:**

```typescript
export const API_BASE_URL = import.meta.env.PROD
  ? "https://api.yourdomain.com"
  : "http://localhost:8000";
```

---

## 📁 Project Structure

```
comcom/
├── app/                          # Backend application
│   ├── api/                      # API routes
│   │   └── routes/
│   │       ├── chat.py          # Chat endpoint
│   │       └── conversations.py # Conversation management
│   ├── core/                     # Core configuration
│   │   ├── config.py            # Settings & env vars
│   │   └── enums.py             # Enums & types
│   ├── graph/                    # LangGraph workflows
│   │   ├── nodes/               # Core orchestration nodes
│   │   ├── subgraphs/           # Legacy subgraphs
│   │   └── workflows/           # Main workflows
│   │       ├── auth_middleware/ # Authentication
│   │       ├── order_management/# Cart & checkout
│   │       ├── product_search/  # Search workflows
│   │       ├── signin/          # Sign-in flows
│   │       └── signup/          # Sign-up flows
│   ├── models/                   # Pydantic models
│   ├── services/                 # Business logic
│   │   └── db/                  # Database services
│   ├── types/                    # Type definitions
│   └── utils/                    # Utilities
├── client/                       # Frontend application
│   ├── public/                  # Static assets
│   └── src/
│       ├── components/          # React components
│       ├── features/            # Feature modules
│       ├── store/               # State management
│       └── types/               # TypeScript types
├── docs/                         # Documentation
├── tests/                        # Test suites
├── .env.sample                   # Environment template
├── main.py                       # FastAPI entry point
├── Makefile                      # Development commands
└── README.md                     # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Code Style

- **Backend**: Follow PEP 8, use `black` and `ruff`
- **Frontend**: Follow TypeScript best practices, use ESLint
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

---

## 🐛 Troubleshooting

### Common Issues

**1. "GROQ_API_KEY not found"**

- Ensure `.env` file exists in project root
- Verify `GROQ_API_KEY` is set correctly
- Restart the backend server

**2. "Database locked" errors**

- Close any SQLite browser connections
- Restart the backend
- Delete `.sqlite-wal` and `.sqlite-shm` files

**3. Frontend can't connect to backend**

- Verify backend is running on `localhost:8000`
- Check CORS settings in `main.py`
- Update `client/src/config/index.ts` if needed

**4. "Module not found" errors**

- Backend: Run `make install` again
- Frontend: Delete `node_modules`, run `pnpm install`

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **LangChain** - LLM application framework
- **LangGraph** - Stateful agent orchestration
- **Groq** - Ultra-fast LLM inference
- **shadcn/ui** - Beautiful UI components
- **Tailwind CSS** - Utility-first CSS

---

## 📞 Support

For questions, issues, or feature requests:

- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review the API documentation at `/docs`

---

<div align="center">

**Built with ❤️ using Python, React, and LangGraph**

⭐ Star this repo if you find it helpful!

</div>
