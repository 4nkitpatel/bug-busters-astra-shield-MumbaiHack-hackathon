# Frontend Setup Guide

## Quick Start

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Start Backend API (Terminal 1)

```bash
# From project root
cd /Users/upmanyujha/Documents/mumbai_hacks_BB
source venv/bin/activate
uvicorn src.api:app --reload --port 8000
```

### 3. Start React Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AnalysisStatus.tsx    # Loading/analyzing state
│   │   ├── ReportDashboard.tsx   # Results display
│   │   └── RiskGauge.tsx         # Risk score visualization
│   ├── services/
│   │   └── apiService.ts         # API client for FastAPI
│   ├── types.ts                  # TypeScript type definitions
│   ├── App.tsx                   # Main application component
│   ├── main.tsx                   # React entry point
│   └── index.css                 # Tailwind CSS
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Key Features

### ✅ Replicates AstraShield Design
- Same dark theme with cyan accents
- Identical layout and components
- Matching animations and transitions

### ✅ Connected to Python Backend
- Uses FastAPI backend for verification
- Transforms backend response to match frontend types
- Handles errors gracefully

### ✅ Enhanced Features
- Entity forensics display
- Evidence log visualization
- Risk gauge chart
- Responsive design

## Troubleshooting

### Backend Connection Issues

If you see connection errors:
1. Ensure backend is running on port 8000
2. Check CORS settings in `src/api.py`
3. Verify `VITE_API_URL` in `.env` file

### Build Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

```bash
# Check TypeScript compilation
npm run build
```

## Production Build

```bash
npm run build
# Output in dist/ directory
```

Serve with any static file server or deploy to Vercel/Netlify.

