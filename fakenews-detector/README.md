# TruthLens — AI Fake News Detector

> Premium frontend for AI-powered news credibility analysis. Built with React, Vite, Tailwind CSS, and Framer Motion.

![TruthLens Preview](preview.png)

---

## ✨ Features

- **Glassmorphic dark UI** — Material 3-inspired, Pixel Buds aesthetic
- **Framer Motion animations** — Page reveals, loading states, result transitions
- **Floating orbs & grid background** — Ambient, depth-creating effects
- **Confidence meter** — Animated progress bar with confidence %
- **Risk classification** — LOW / MEDIUM / HIGH risk indicators
- **Mock mode** — Works out of the box without a backend
- **Responsive** — Mobile-first, works on all devices
- **Accessible** — Semantic HTML, ARIA labels, keyboard navigation

---

## 🗂 Folder Structure

```
fakenews-detector/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── BackgroundEffects.jsx   # Floating orbs, grid
│   │   ├── Navbar.jsx              # Sticky blur navbar
│   │   ├── HeroSection.jsx         # Landing hero
│   │   ├── DetectorCard.jsx        # Main input card
│   │   ├── LoadingAnimation.jsx    # AI scan animation
│   │   ├── ResultCard.jsx          # Prediction results
│   │   ├── HowItWorks.jsx          # Step-by-step process
│   │   ├── FeatureCards.jsx        # Feature grid
│   │   ├── AccuracySection.jsx     # Metrics & benchmarks
│   │   ├── AboutSection.jsx        # Mission statement
│   │   └── Footer.jsx              # Site footer
│   ├── hooks/
│   │   ├── useDetector.js          # Detection state & logic
│   │   └── useScrollReveal.js      # Scroll-triggered visibility
│   ├── services/
│   │   └── api.js                  # API layer + mock mode
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css                   # Tailwind + global styles
├── .env.example
├── vercel.json
├── tailwind.config.js
├── vite.config.js
└── package.json
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd fakenews-detector
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000   # Your backend URL
VITE_USE_MOCK=true                        # false = real backend
```

### 3. Run dev server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## 🔌 Backend Integration

The frontend expects your backend at `POST /predict`:

**Request:**
```json
{ "text": "News article or headline here..." }
```

**Response:**
```json
{
  "prediction": "Fake",
  "confidence": "94%",
  "risk": "HIGH"
}
```

> `risk` is optional — the frontend derives it from confidence if not provided.

---

## 🌐 Deploy to Vercel

### One-click deploy:

```bash
npm install -g vercel
vercel --prod
```

### Or via Vercel dashboard:
1. Push repo to GitHub
2. Import at [vercel.com/new](https://vercel.com/new)
3. Add environment variables:
   - `VITE_API_BASE_URL` → your backend URL
   - `VITE_USE_MOCK` → `false`
4. Deploy ✅

---

## 🎨 Design System

| Token | Value | Usage |
|---|---|---|
| `surface-900` | `#080810` | Page background |
| `surface-800` | `#0e0e1a` | Card backgrounds |
| `accent-blue` | `#4f8ef7` | Primary accents |
| `accent-purple` | `#7c5cfc` | Secondary accents |
| `accent-cyan` | `#22d3ee` | Tertiary / data viz |
| Font | DM Sans | Body & display |
| Mono | JetBrains Mono | Code, labels |

---

## 📦 Tech Stack

| Library | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| Vite | 5 | Build tool |
| Tailwind CSS | 3 | Styling |
| Framer Motion | 11 | Animations |
| Lucide React | 0.383 | Icons |

---

## 🔧 Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start dev server at :5173 |
| `npm run build` | Production build → `dist/` |
| `npm run preview` | Preview production build |
| `npm run lint` | ESLint check |

---

## 📄 License

MIT — free for personal and commercial use.

---

*Built with ♥ for a more informed world.*
