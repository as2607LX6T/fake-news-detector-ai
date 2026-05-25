/**
 * useDetector — Custom hook encapsulating all fake news detection state & logic.
 * Keeps DetectorCard component clean and focused on rendering.
 */
import { useState, useCallback } from 'react';
import { mockAnalyzeText, analyzeText } from '../services/api';

export const STATES = {
  IDLE:    'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR:   'error',
};

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'; // default to mock

export function useDetector() {
  const [inputText, setInputText]   = useState('');
  const [status,    setStatus]      = useState(STATES.IDLE);
  const [result,    setResult]      = useState(null);
  const [error,     setError]       = useState(null);

  const analyze = useCallback(async () => {
    const trimmed = inputText.trim();
    if (!trimmed) return;

    setStatus(STATES.LOADING);
    setResult(null);
    setError(null);

    try {
      const data = USE_MOCK
        ? await mockAnalyzeText(trimmed)
        : await analyzeText(trimmed);

      // Normalize confidence to a number (strip % if present)
      const confidenceNum = parseInt(String(data.confidence).replace('%', ''), 10);

      // Derive risk from confidence if not provided by backend
      const risk = data.risk || (
        confidenceNum > 85 ? 'HIGH' :
        confidenceNum > 65 ? 'MEDIUM' : 'LOW'
      );

      setResult({
        prediction:  data.prediction,   // "Fake" | "Real"
        confidence:  confidenceNum,      // number 0–100
        risk,                            // "LOW" | "MEDIUM" | "HIGH"
      });
      setStatus(STATES.SUCCESS);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
      setStatus(STATES.ERROR);
    }
  }, [inputText]);

  const reset = useCallback(() => {
    setStatus(STATES.IDLE);
    setResult(null);
    setError(null);
  }, []);

  const clearInput = useCallback(() => {
    setInputText('');
    reset();
  }, [reset]);

  return {
    inputText,
    setInputText,
    status,
    result,
    error,
    analyze,
    reset,
    clearInput,
    isLoading: status === STATES.LOADING,
    isSuccess: status === STATES.SUCCESS,
    isError:   status === STATES.ERROR,
    isIdle:    status === STATES.IDLE,
  };
}
