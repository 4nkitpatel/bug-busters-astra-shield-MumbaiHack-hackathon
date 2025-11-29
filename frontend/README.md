# Disaster Relief Verifier - React Frontend

Modern React/TypeScript frontend for the Disaster Relief Verification System, matching AstraShield's design.

## Features

- 🎨 Modern, polished UI matching AstraShield design
- 📊 Interactive risk gauge visualization
- 🔍 Entity forensics with detailed verification status
- 📱 Fully responsive design
- ⚡ Fast and smooth animations

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set VITE_API_URL if backend is on different port
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## Development

- Frontend runs on: `http://localhost:3000`
- Backend API should be running on: `http://localhost:8000`

The frontend uses Vite's proxy to forward `/api/*` requests to the backend.

## Tech Stack

- React 19
- TypeScript
- Vite
- Tailwind CSS
- Recharts (for risk gauge)
- Axios (for API calls)

