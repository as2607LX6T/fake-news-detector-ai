/**
 * ResultCard — Animated, premium result display with confidence meter and risk badge.
 */
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, AlertTriangle, RotateCcw, TrendingUp } from 'lucide-react';

const RISK_CONFIG = {
  LOW:    { color: '#22d3ee', bg: 'rgba(34,211,238,0.1)',  border: 'rgba(34,211,238,0.3)'  },
  MEDIUM: { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.3)'  },
  HIGH:   { color: '#ef4444', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.3)'   },
};

export default function ResultCard({ result, onReset }) {
  const isFake = result.prediction === 'Fake';
  const risk   = RISK_CONFIG[result.risk] || RISK_CONFIG.MEDIUM;

  const mainColor    = isFake ? '#ef4444' : '#22c55e';
  const mainColorBg  = isFake ? 'rgba(239,68,68,0.08)' : 'rgba(34,197,94,0.08)';
  const gradientFrom = isFake ? '#ef4444' : '#22c55e';
  const gradientTo   = isFake ? '#f97316' : '#4ade80';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    >
      {/* Verdict banner */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.15, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="flex flex-col items-center gap-4 py-8 mb-6"
      >
        {/* Icon */}
        <motion.div
          initial={{ scale: 0, rotate: -30 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: 0.25, duration: 0.6, type: 'spring', stiffness: 200 }}
          className="relative"
        >
          <div
            className="w-20 h-20 rounded-full flex items-center justify-center"
            style={{
              background: mainColorBg,
              boxShadow: `0 0 50px ${mainColor}30`,
              border: `2px solid ${mainColor}40`,
            }}
          >
            {isFake
              ? <XCircle size={40} style={{ color: mainColor }} strokeWidth={1.5} />
              : <CheckCircle2 size={40} style={{ color: mainColor }} strokeWidth={1.5} />
            }
          </div>
          {/* Glow ring */}
          <motion.div
            className="absolute inset-0 rounded-full"
            animate={{ scale: [1, 1.4], opacity: [0.4, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
            style={{ border: `2px solid ${mainColor}` }}
          />
        </motion.div>

        {/* Verdict text */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="text-center"
        >
          <div
            className="text-5xl font-bold mb-2 tracking-tight"
            style={{
              background: `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {result.prediction}
          </div>
          <p className="text-white/50 text-sm">
            {isFake
              ? 'This content shows signs of misinformation'
              : 'This content appears to be credible'}
          </p>
        </motion.div>
      </motion.div>

      {/* Metrics grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        {/* Confidence meter */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="glass rounded-2xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-xs text-white/40 uppercase tracking-widest mb-1">Confidence</div>
              <div className="text-3xl font-bold text-white">{result.confidence}%</div>
            </div>
            <TrendingUp size={20} className="text-white/30" />
          </div>

          {/* Progress bar */}
          <div className="h-1.5 w-full rounded-full overflow-hidden bg-white/[0.06]">
            <motion.div
              className="h-full rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${result.confidence}%` }}
              transition={{ delay: 0.7, duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
              style={{
                background: `linear-gradient(90deg, ${gradientFrom}, ${gradientTo})`,
                boxShadow: `0 0 10px ${mainColor}60`,
              }}
            />
          </div>

          {/* Ticks */}
          <div className="flex justify-between mt-2">
            {['0', '25', '50', '75', '100'].map(v => (
              <span key={v} className="text-xs text-white/20 font-mono">{v}</span>
            ))}
          </div>
        </motion.div>

        {/* Risk level */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.55, duration: 0.5 }}
          className="glass rounded-2xl p-5 flex flex-col justify-between"
        >
          <div>
            <div className="text-xs text-white/40 uppercase tracking-widest mb-1">Risk Level</div>
            <div className="flex items-center gap-2 mt-3">
              <AlertTriangle size={18} style={{ color: risk.color }} />
              <span
                className="text-2xl font-bold tracking-wide"
                style={{ color: risk.color }}
              >
                {result.risk}
              </span>
            </div>
          </div>

          <div
            className="mt-4 px-3 py-2 rounded-xl text-xs font-medium text-center"
            style={{
              background: risk.bg,
              border: `1px solid ${risk.border}`,
              color: risk.color,
            }}
          >
            {result.risk === 'HIGH'   && 'Exercise extreme caution'}
            {result.risk === 'MEDIUM' && 'Verify before sharing'}
            {result.risk === 'LOW'    && 'Generally reliable source'}
          </div>
        </motion.div>
      </div>

      {/* Indicator pills */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7, duration: 0.5 }}
        className="glass rounded-2xl p-4 mb-6"
      >
        <div className="text-xs text-white/40 uppercase tracking-widest mb-3">AI Signal Indicators</div>
        <div className="flex flex-wrap gap-2">
          {(isFake
            ? ['Emotional Language', 'Vague Attribution', 'Sensational Framing', 'Missing Context', 'Unverified Claims']
            : ['Neutral Tone', 'Named Sources', 'Factual Language', 'Consistent Data', 'Verifiable Context']
          ).map((tag) => (
            <span
              key={tag}
              className="px-3 py-1 rounded-full text-xs font-medium"
              style={{
                background: isFake ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)',
                border: `1px solid ${isFake ? 'rgba(239,68,68,0.25)' : 'rgba(34,197,94,0.25)'}`,
                color: isFake ? '#fca5a5' : '#86efac',
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      </motion.div>

      {/* Reset button */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        onClick={onReset}
        className="w-full flex items-center justify-center gap-2 py-3 rounded-2xl text-white/50 hover:text-white/80 glass hover:bg-white/[0.05] transition-all duration-300 text-sm group"
      >
        <motion.div
          className="group-hover:rotate-180 transition-transform duration-500"
        >
          <RotateCcw size={14} />
        </motion.div>
        Analyze another article
      </motion.button>
    </motion.div>
  );
}
