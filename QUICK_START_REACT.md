# Quick Start - React Frontend

## 🚀 Setup Instructions

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 2: Start Backend (Terminal 1)

```bash
# From project root
cd /Users/upmanyujha/Documents/mumbai_hacks_BB
source venv/bin/activate  # or: venv/bin/activate
uvicorn src.api:app --reload --port 8000
```

### Step 3: Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

### Step 4: Open Browser

Navigate to: **http://localhost:3000**

## ✅ What's Changed

### Backend (FastAPI)
- ✅ Added CORS middleware for React frontend
- ✅ Added `transform_to_astrashield_format()` function
- ✅ API now returns data in AstraShield-compatible format

### Frontend (React/TypeScript)
- ✅ Complete React/TypeScript application
- ✅ Matches AstraShield design exactly
- ✅ Connected to FastAPI backend
- ✅ All components replicated (RiskGauge, ReportDashboard, AnalysisStatus)

## 📁 New Files Created

```
frontend/
├── src/
│   ├── components/
│   │   ├── AnalysisStatus.tsx
│   │   ├── ReportDashboard.tsx
│   │   └── RiskGauge.tsx
│   ├── services/
│   │   └── apiService.ts
│   ├── types.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## 🎨 Features

- **Exact AstraShield Design**: Dark theme, cyan accents, same layout
- **Risk Gauge**: Interactive pie chart visualization
- **Entity Forensics**: Detailed entity cards with verification status
- **Evidence Log**: Structured evidence display
- **Responsive**: Works on mobile and desktop

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Change port in vite.config.ts
server: { port: 3001 }
```

### Backend Connection Error
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify CORS settings in `src/api.py`
3. Check browser console for errors

### Build Errors
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📝 Next Steps

1. Test the application with a sample image
2. Customize branding/colors if needed
3. Deploy frontend (Vercel/Netlify) and backend (Railway/Render)

