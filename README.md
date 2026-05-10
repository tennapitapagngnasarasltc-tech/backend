# 🌙 Nidra — Sleep Quality Prediction API

> AI-powered sleep quality prediction backend built with FastAPI, XGBoost, and Supabase.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Backend](#running-the-backend)
- [API Endpoints](#api-endpoints)
- [ML Model](#ml-model)
- [Strategy Engine](#strategy-engine)
- [Supabase Setup](#supabase-setup)
- [Testing with Postman](#testing-with-postman)
- [Environment Variables](#environment-variables)
- [Roadmap](#roadmap)

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Setup
git clone https://github.com/your-username/nidra_backend.git
cd nidra_backend
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install & configure
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Supabase credentials

# 3. Train model (first time only)
python prepare_data.py && python feature_engineering.py && python train_model.py

# 4. Run
uvicorn app.main:app --reload
# API at http://127.0.0.1:8000
# Docs at http://127.0.0.1:8000/docs
```

---

Nidra predicts a user's sleep quality score (1–10) based on personal health inputs and returns personalised improvement strategies. The backend exposes a REST API that can be consumed by a Flutter mobile app.

**How it works:**
```
User inputs → FastAPI → XGBoost model → Sleep score (1–10)
                    ↓
             Strategy engine → Personalised recommendations
                    ↓
             Supabase → Save profile + history
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| ML Model | XGBoost (regression) |
| Data Processing | Pandas, Scikit-learn |
| Database | Supabase (PostgreSQL) |
| Authentication | Supabase Auth (JWT) |
| Model Serialisation | Joblib |
| Server | Uvicorn |
| Language | Python 3.10+ |

---

## Project Structure

```
nidra_backend/
│
├── app/
│   ├── main.py                  # FastAPI app + all endpoints
│   ├── auth.py                  # JWT token verification
│   │
│   ├── schemas/
│   │   └── sleep.py             # Pydantic input model (SleepInput)
│   │
│   ├── model/
│   │   ├── predictor.py         # Loads model + predict()
│   │   ├── model.pkl            # Trained XGBoost model
│   │   ├── scaler.pkl           # StandardScaler
│   │   └── columns.pkl          # Training column order
│   │
│   ├── services/
│   │   ├── supabase_client.py   # Supabase connection
│   │   ├── profile_service.py   # Save/fetch user profiles
│   │   └── strategy.py          # Data-driven strategy engine
│   │
│   ├── utils/
│   │   └── preprocess.py        # Input → model-ready features
│   │
│   └── data/
│       ├── sleep_data.csv        # Raw dataset
│       ├── clean_sleep.csv       # After prepare_data.py
│       └── featured_sleep.csv    # After feature_engineering.py
│
├── prepare_data.py              # Step 1: Clean raw dataset
├── feature_engineering.py      # Step 2: Create derived features
├── train_model.py               # Step 3: Train + save XGBoost model
├── requirements.txt
├── .env                         # Supabase keys (never commit this)
├── .env.example                 # Safe template to share
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Clone & create virtual environment

```bash
git clone https://github.com/your-username/nidra_backend.git
cd nidra_backend

python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
```

### 4. Train the model

Run these scripts in order from the project root:

```bash
python prepare_data.py
python feature_engineering.py
python train_model.py
```

This generates `model.pkl`, `scaler.pkl`, and `columns.pkl` inside `app/model/`.

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

API is live at: `http://127.0.0.1:8000`  
Interactive docs at: `http://127.0.0.1:8000/docs`

---

## Running the Backend

### Quick Start (Development)

```bash
# 1. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 2. Run the server
uvicorn app.main:app --reload
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### Full Step-by-Step

**Step 1: Start in the project directory**
```bash
cd nidra_backend
```

**Step 2: Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

**Step 3: Start the server**
```bash
uvicorn app.main:app --reload
```

**Step 4: Verify it's running**

Open your browser and visit:
- **Health check:** `http://127.0.0.1:8000/` → Should return `{ "message": "Nidra running" }`
- **API Docs:** `http://127.0.0.1:8000/docs` → Interactive Swagger UI
- **Alternative docs:** `http://127.0.0.1:8000/redoc` → ReDoc UI

### Production Mode (No auto-reload)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Running with Multiple Workers

```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Running Backend + Frontend Together

**Terminal 1 (Backend):**
```bash
cd nidra_backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd Nindra-Mobile-apk
flutter run -d android  # or -d ios
```

Make sure your Flutter app's `lib/services/api_service.dart` points to:
```dart
const String API_BASE_URL = 'http://10.0.2.2:8000/api';  // For Android emulator
// OR
const String API_BASE_URL = 'http://localhost:8000/api';  // For physical device on same network
```

---

## API Endpoints

### `GET /`
Health check — no auth required.

**Response:**
```json
{ "message": "Nidra running" }
```

---

### `POST /predict`
Predict sleep quality score and get personalised strategies.

**Auth required:** `Authorization: Bearer <access_token>`

**Request body:**
```json
{
  "gender": "Female",
  "age": 30,
  "occupation": "Nurse",
  "sleep_duration": 6.5,
  "physical_activity_level": 45,
  "stress_level": 6,
  "bmi_category": "Normal",
  "systolic": 118,
  "diastolic": 76
}
```

**Response:**
```json
{
  "user_id": "a271360b-8641-4e5e-bbf8-b748aa8b82ff",
  "email": "user@mail.com",
  "sleep_score": 7.24,
  "score_band": "Good",
  "overall": "🟢 Good sleep quality. You're above average...",
  "priority_fixes": [],
  "strategies": [
    "🏃 Increase activity to 60–75 min/day for optimal sleep quality"
  ],
  "warnings": [],
  "positives": [
    "✅ Normal BMI — good foundation for high sleep quality.",
    "✅ Blood pressure 118/76 is normal."
  ]
}
```

**Score bands:**

| Score | Band |
|---|---|
| < 5.0 | 🔴 Critical |
| 5.0 – 5.9 | 🟠 Poor |
| 6.0 – 6.9 | 🟡 Fair |
| 7.0 – 7.9 | 🟢 Good |
| 8.0 + | 🌟 Excellent |

---

### `GET /profile`
Fetch the saved profile for the logged-in user.

**Auth required:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": "a271360b-8641-4e5e-bbf8-b748aa8b82ff",
  "email": "user@mail.com",
  "gender": "Female",
  "age": 30,
  "occupation": "Nurse",
  "sleep_duration": 6.5,
  "physical_activity_level": 45,
  "stress_level": 6,
  "bmi_category": "Normal",
  "created_at": "2026-04-25T19:54:43+00:00"
}
```

---

## ML Model

**Algorithm:** XGBoost Regressor  
**Target:** `quality_of_sleep` (1–10 scale)  
**Dataset:** 374 records, 12 features

**Input features:**
```
gender, age, occupation, sleep_duration,
physical_activity_level, stress_level,
bmi_category, systolic, diastolic,
sleep_efficiency, stress_activity_ratio
```

**Derived features (feature engineering):**
```python
sleep_efficiency      = sleep_duration / 8
stress_activity_ratio = stress_level / (physical_activity_level + 1)
```

**Model parameters:**
```python
XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6
)
```

---

## Strategy Engine

The strategy engine uses real data distributions from the training dataset to generate evidence-based recommendations. It returns 5 separate categories:

| Category | Description |
|---|---|
| `priority_fixes` | Critical issues needing immediate attention |
| `strategies` | Actionable improvement steps |
| `warnings` | Health flags (BP, BMI, overtraining) |
| `positives` | What the user is doing right |
| `overall` | Score band summary message |

**Key thresholds from dataset analysis:**

| Feature | Insight |
|---|---|
| Sleep duration 7.5h+ | Avg quality **8.8** (best zone) |
| Stress level 8 | Avg quality drops to **5.7** |
| Activity 60–75 min/day | Avg quality **8.8** (optimal) |
| Activity 75+ min/day | Quality drops (overtraining effect) |
| Obese BMI | Avg quality **6.4** |

---

## Supabase Setup

### 1. Create the profiles table

Run this SQL in your Supabase SQL Editor:

```sql
create table public.profiles (
  id uuid not null,
  email text null,
  gender text null,
  age integer null,
  occupation text null,
  sleep_duration double precision null,
  physical_activity_level integer null,
  stress_level integer null,
  created_at timestamp with time zone null default now(),
  bmi_category text null,
  constraint profiles_pkey primary key (id)
) TABLESPACE pg_default;
```

### 2. Disable Row Level Security (for development)

In Supabase → Table Editor → profiles → RLS → **Disable**.

### 3. Get your credentials

Supabase → Settings → API:
- **Project URL** → `SUPABASE_URL`
- **anon public key** → `SUPABASE_KEY`

---

## Testing with Postman

### Step 1 — Get access token

```
POST https://YOUR-PROJECT-ID.supabase.co/auth/v1/token?grant_type=password

Headers:
  Content-Type  : application/json
  apikey        : your-anon-key

Body:
  { "email": "user@mail.com", "password": "password" }
```

Copy the `access_token` from the response.

### Step 2 — Call /predict

```
POST http://127.0.0.1:8000/predict

Headers:
  Content-Type  : application/json
  Authorization : Bearer <access_token>

Body: { ...sleep inputs... }
```

### Step 3 — Verify profile

```
GET http://127.0.0.1:8000/profile

Headers:
  Authorization : Bearer <access_token>
```

---

## Environment Variables

| Variable | Description | Where to find |
|---|---|---|
| `SUPABASE_URL` | Your Supabase project URL | Supabase → Settings → API |
| `SUPABASE_KEY` | Supabase anon public key | Supabase → Settings → API |

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:** Ensure you're running from the project root directory:
```bash
cd nidra_backend
uvicorn app.main:app --reload
```

### Issue: "Supabase connection refused"

**Solution:** Check `.env` file:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Ensure Supabase project is active
- Check firewall/network connectivity

### Issue: "XGBoost model not found"

**Solution:** Run training scripts in order:
```bash
python prepare_data.py
python feature_engineering.py
python train_model.py
```

Verify files exist in `app/model/`:
- `model.pkl`
- `scaler.pkl`
- `columns.pkl`

### Issue: "JWT token verification failed"

**Solution:**
- Ensure `Authorization: Bearer <token>` header is included
- Verify token is not expired
- Check Supabase JWT secret matches configuration

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>

# Or use a different port:
uvicorn app.main:app --reload --port 8001
```

### Issue: "Backend not accessible from mobile device"

**Solution:**
- Get your PC IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Update Flutter app's API URL to `http://YOUR_IP:8000/api`
- Ensure both PC and device are on same network
- Check firewall allows port 8000
- Test from device: Open browser → `http://YOUR_IP:8000`

---

## Development Workflow

### Data Pipeline

1. **Prepare Data** (`prepare_data.py`)
   - Loads `sleep_data.csv`
   - Cleans missing values, handles outliers
   - Outputs → `clean_sleep.csv`

2. **Feature Engineering** (`feature_engineering.py`)
   - Derives new features (e.g., `sleep_efficiency`, `stress_activity_ratio`)
   - Encodes categorical variables
   - Outputs → `featured_sleep.csv`

3. **Model Training** (`train_model.py`)
   - Trains XGBoost regressor
   - Saves model + scaler + column order
   - Outputs → `app/model/*.pkl`

### Running in Debug Mode

```bash
# With auto-reload on code changes
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
pytest tests/ -v
```

---

## Deployment

### Local Production Build

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Deploy to Render.com

1. Push code to GitHub
2. Connect Render to your repo
3. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. Deploy

**Service URL:** `https://your-service-name.onrender.com`

---

## Performance Considerations

- **Model Inference:** ~10-50ms per prediction
- **API Response Time:** ~100-200ms (including DB operations)
- **Scaling:** Horizontal scaling recommended for 1000+ concurrent users

---

## API Response Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Invalid input data |
| `401` | Unauthorized (missing/invalid token) |
| `403` | Forbidden (insufficient permissions) |
| `500` | Server error |

---

## File Descriptions

| File | Purpose |
|---|---|
| `prepare_data.py` | Data cleaning pipeline |
| `feature_engineering.py` | Feature creation & encoding |
| `train_model.py` | Model training & serialization |
| `app/main.py` | FastAPI application & endpoints |
| `app/auth.py` | JWT token verification |
| `app/schemas/sleep.py` | Request/response models |
| `app/model/predictor.py` | Model loading & prediction |
| `app/services/supabase_client.py` | Database client |
| `app/services/profile_service.py` | User profile operations |
| `app/services/strategy.py` | Recommendation engine |
| `app/utils/preprocess.py` | Data preprocessing helpers |

---

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

**Code standards:**
- PEP 8 compliance
- Type hints for functions
- Docstrings for public functions
- Unit tests for new features

---

## Security Best Practices

- ⚠️ **Never commit `.env` file** — it's in `.gitignore`
- Use `.env.example` as a safe template
- Rotate Supabase keys regularly
- Restrict CORS to trusted frontend domains
- Validate all input data

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [XGBoost Guide](https://xgboost.readthedocs.io/)
- [Supabase Python Docs](https://supabase.com/docs/reference/python/introduction)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Mobile App Frontend](../Nindra-Mobile-apk)

---

## Roadmap

- [x] Dataset cleaning + feature engineering
- [x] XGBoost model training
- [x] FastAPI `/predict` endpoint
- [x] Data-driven strategy engine
- [x] Supabase Auth (JWT verification)
- [x] User profile save + fetch
- [ ] Sleep history table + `/history` endpoint
- [ ] Batch prediction API
- [ ] Deploy to Render.com
- [ ] LSTM model for trend-based prediction
- [ ] Weekly sleep report generation
- [ ] Push notifications
- [ ] Admin dashboard

---

## Requirements

```txt
fastapi
uvicorn
pandas
scikit-learn
xgboost
joblib
supabase
python-dotenv
```

Install all:
```bash
pip install -r requirements.txt
```

---

## License

This project is licensed under the MIT License — see LICENSE file for details.

---

*Built with ❤️ — Nidra means sleep in Sanskrit*