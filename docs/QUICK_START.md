# 🚀 ComCom - Quick Start Guide

Get up and running with ComCom in 5 minutes!

## Prerequisites

- Python 3.12+
- Node.js 18+
- pnpm (or npm)
- Groq API Key ([Get one free here](https://console.groq.com/keys))

## Step 1: Environment Setup

```bash
# Clone the repository
cd comcom

# Copy environment template
cp .env.sample .env

# Edit .env and add your keys
nano .env  # or your favorite editor
```

**Required in `.env`:**

```env
GROQ_API_KEY=your_actual_groq_api_key
JWT_SECRET=generate_with_python_secrets
```

**Generate JWT Secret:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 2: Install Backend

```bash
make install
```

This will:

- Create virtual environment
- Install Python dependencies
- Initialize database
- Seed product data (1000+ products)

## Step 3: Install Frontend

```bash
cd client
pnpm install
cd ..
```

## Step 4: Run the Application

**Terminal 1 - Backend:**

```bash
make dev
```

Backend will run on `http://localhost:8000`

**Terminal 2 - Frontend:**

```bash
cd client
pnpm dev
```

Frontend will run on `http://localhost:5173`

## Step 5: Try It Out!

Open `http://localhost:5173` in your browser and try:

1. **Sign Up:**

   - "Sign up with email: test@example.com password: Test123!"

2. **Search Products:**

   - "Show me blue Nike shoes"
   - "Find smartphones under $500"

3. **Add to Cart:**

   - "Add that first one to my cart"

4. **Edit Cart:**

   - "Make it size large"
   - "I want 2 of them"

5. **Checkout:**
   - "I want to checkout"

## 🎉 That's It!

You're now running ComCom locally. Explore the full features:

- 📚 Full documentation: `README.md`
- 🔧 API docs: `http://localhost:8000/docs`
- 📖 Workflow docs: `docs/` folder

## Common Issues

**"GROQ_API_KEY not found"**

- Check `.env` file exists
- Verify key is correctly set
- Restart backend server

**Frontend can't connect**

- Ensure backend is running on port 8000
- Check browser console for errors

**Database errors**

- Run `make clean` then `make install`

---

Need help? Check the full README.md or open an issue!
