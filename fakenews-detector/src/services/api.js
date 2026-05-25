/**
 * API Service Layer
 * Handles all communication with the fake news detection backend.
 * Base URL can be configured via environment variable.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Analyze text for fake news detection.
 * POST /predict
 *
 * @param {string} text - The article or headline to analyze
 * @returns {Promise<{ prediction: string, confidence: string, reasoning?: string }>}
 */
export async function analyzeText(text) {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Server error: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Health check for the backend API.
 * GET /health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.ok;
}

/**
 * Mock analysis for demo purposes (when no backend is available).
 * Simulates realistic prediction with a configurable delay.
 *
 * @param {string} text - The article or headline to analyze
 * @returns {Promise<{ prediction: string, confidence: string, risk: string }>}
 */
export async function mockAnalyzeText(text) {
  // Simulate network latency
  await new Promise(resolve => setTimeout(resolve, 2200 + Math.random() * 800));

  // Very simple heuristic for demo — not real ML
  const suspiciousKeywords = [
    'shocking', 'exclusive', 'breaking', 'hoax', 'exposed', 'cover-up',
    'secret', 'leaked', 'conspiracy', 'they don\'t want you to know',
    'mainstream media', 'wake up', 'share before removed'
  ];

  const lower = text.toLowerCase();
  const hits = suspiciousKeywords.filter(kw => lower.includes(kw)).length;
  const isFake = hits >= 2 || (hits >= 1 && text.includes('!'));

  const confidence = isFake
    ? 72 + Math.floor(Math.random() * 25)
    : 68 + Math.floor(Math.random() * 28);

  const risk = confidence > 85 ? 'HIGH' : confidence > 65 ? 'MEDIUM' : 'LOW';

  return {
    prediction: isFake ? 'Fake' : 'Real',
    confidence: `${confidence}%`,
    risk,
  };
}
