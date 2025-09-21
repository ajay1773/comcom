# ComCom API

A simple chat API built with FastAPI.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Make (usually pre-installed on Unix-based systems)

### Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd comcom
```

2. Install dependencies:

```bash
make install
```

### Development

To run the development server with hot reload:

```bash
make dev
```

The API will be available at `http://localhost:8000`

### Other Commands

- `make start` - Run production server
- `make clean` - Clean Python cache files
- `make format` - Format code using black
- `make lint` - Run linting using ruff

### API Documentation

Once the server is running, you can access:

- API documentation at `http://localhost:8000/docs`
- OpenAPI specification at `http://localhost:8000/openapi.json`

## API Endpoints

### Chat

- `POST /api/chat`
  - Request body: `{ "query": "your message", "session_id": "optional-session-id" }`
  - Response: `{ "response": "echo response", "done": true }`
