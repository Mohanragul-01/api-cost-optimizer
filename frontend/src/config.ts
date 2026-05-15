// File: config.ts
// Purpose: Single source of truth for API base URL — switches by environment
// Step: Step-7 (updated for deployment)

// WHY: Vite exposes only variables prefixed with VITE_ to the browser bundle.
// In local dev, VITE_API_BASE is not set so we fall back to localhost.
// On Vercel, set VITE_API_BASE=https://your-backend.onrender.com in project settings.
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000"
export default API_BASE
