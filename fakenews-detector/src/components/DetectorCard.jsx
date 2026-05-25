/**
 * DetectorCard — The primary news analysis interface.
 * Handles input, loading states, results, and errors in one cohesive card.
 */
import { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Scan, X, Clipboard, AlertCircle, Sparkles } from 'lucide-react';
import { useDetector, STATES } from '../hooks/useDetector';
import LoadingAnimation from './LoadingAnimation';
import ResultCard from './ResultCard';

const PLACEHOLDER = `Paste a news article, headline, or social media post here…

Example:
"Scientists discover that drinking 10 cups of coffee daily reverses aging by 20 years, study shows — doctors are shocked!"\n\nTip: The more text you provide, the more accurate the analysis.`;

export default function DetectorCard() {
  const {
    inputText, setInputText,
    status, result, error,
    analyze, reset, clearInput,
    isLoading, isSuccess, isError,
  } = useDetector();

  const textareaRef = useRef(null);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setInputText(text);
      textareaRef.current?.focus();
    } catch {
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      if (inputText.trim() && !isLoading) analyze();
    }
  };

  const charCount = inputText.length;
  const isOverLimit = charCount > 5000;

  return (
    <section id="detector" className="relative py-24 px-6">
      <div className="max-w-3xl mx-auto">
        {/* Section label */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-medium text-white/50 tracking-widest uppercase mb-4">
            <Scan size={11} className="text-accent-blue" />
            Detector
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Paste. Analyze. <span className="gradient-text">Know.</span>
          </h2>
          <p className="text-white/40 text-base max-w-lg mx-auto">
            Our AI reads between the lines — analyzing tone, source patterns,
            and linguistic markers to surface the truth.
          </p>
        </motion.div>

        {/* Main card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="relative rounded-3xl p-1"
          style={{
            background: isSuccess
              ? 'linear-gradient(135deg, rgba(79,142,247,0.15), rgba(124,92,252,0.15))'
              : 'linear-gradient(135deg, rgba(79,142,247,0.08), rgba(124,92,252,0.08))',
          }}
        >
          {/* Glow */}
          <div
            className="absolute inset-0 rounded-3xl blur-xl opacity-30 pointer-events-none"
            style={{ background: 'linear-gradient(135deg, rgba(79,142,247,0.3), rgba(124,92,252,0.3))' }}
          />

          <div className="relative rounded-[22px] overflow-hidden"
            style={{
              background: 'rgba(14,14,26,0.95)',
              backdropFilter: 'blur(40px)',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <AnimatePresence mode="wait">

              {/* ── IDLE / INPUT STATE ── */}
              {(status === STATES.IDLE || status === STATES.ERROR) && (
                <motion.div
                  key="input"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="p-6 md:p-8"
                >
                  {/* Toolbar */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Sparkles size={14} className="text-accent-blue" />
                      <span className="text-xs text-white/40 font-mono tracking-wide uppercase">AI Analysis Input</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handlePaste}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs text-white/40 hover:text-white/70 hover:bg-white/[0.05] transition-all"
                      >
                        <Clipboard size={12} />
                        Paste
                      </button>
                      {inputText && (
                        <button
                          onClick={clearInput}
                          className="p-1.5 rounded-xl text-white/30 hover:text-white/60 hover:bg-white/[0.05] transition-all"
                        >
                          <X size={14} />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Textarea */}
                  <div className="relative">
                    <textarea
                      ref={textareaRef}
                      value={inputText}
                      onChange={(e) => { setInputText(e.target.value); if (isError) reset(); }}
                      onKeyDown={handleKeyDown}
                      placeholder={PLACEHOLDER}
                      rows={8}
                      maxLength={5100}
                      className="w-full bg-transparent text-white/80 placeholder-white/[0.18] text-sm leading-relaxed resize-none outline-none font-body"
                      style={{ caretColor: '#4f8ef7' }}
                    />
                    {/* Gradient fade at bottom */}
                    <div
                      className="absolute bottom-0 left-0 right-0 h-8 pointer-events-none"
                      style={{ background: 'linear-gradient(to top, rgba(14,14,26,0.8), transparent)' }}
                    />
                  </div>

                  {/* Footer bar */}
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/[0.05]">
                    <div className="flex items-center gap-3">
                      <span className={`text-xs font-mono ${isOverLimit ? 'text-red-400' : 'text-white/25'}`}>
                        {charCount.toLocaleString()} / 5,000
                      </span>
                      <span className="text-xs text-white/20 hidden sm:block">⌘↵ to analyze</span>
                    </div>

                    <motion.button
                      whileHover={{ scale: inputText.trim() ? 1.02 : 1 }}
                      whileTap={{ scale: inputText.trim() ? 0.97 : 1 }}
                      onClick={analyze}
                      disabled={!inputText.trim() || isOverLimit}
                      className="btn-primary !py-3 !px-7 flex items-center gap-2 text-sm disabled:opacity-30 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
                    >
                      <Scan size={15} strokeWidth={2} />
                      Analyze
                    </motion.button>
                  </div>

                  {/* Error state */}
                  <AnimatePresence>
                    {isError && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4 flex items-center gap-2 px-4 py-3 rounded-xl text-sm"
                        style={{
                          background: 'rgba(239,68,68,0.08)',
                          border: '1px solid rgba(239,68,68,0.25)',
                          color: '#fca5a5',
                        }}
                      >
                        <AlertCircle size={14} className="flex-shrink-0" />
                        {error}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              )}

              {/* ── LOADING STATE ── */}
              {status === STATES.LOADING && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="px-6 md:px-8 py-4"
                >
                  <LoadingAnimation />
                </motion.div>
              )}

              {/* ── RESULT STATE ── */}
              {status === STATES.SUCCESS && result && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="p-6 md:p-8"
                >
                  <ResultCard result={result} onReset={reset} />
                </motion.div>
              )}

            </AnimatePresence>
          </div>
        </motion.div>

        {/* Disclaimer */}
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="text-center text-xs text-white/20 mt-6 leading-relaxed"
        >
          TruthLens uses AI analysis as a guide — always verify important information
          with authoritative sources. Results are probabilistic, not definitive.
        </motion.p>
      </div>
    </section>
  );
}
