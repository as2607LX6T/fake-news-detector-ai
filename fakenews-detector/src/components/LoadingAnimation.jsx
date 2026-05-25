/**
 * LoadingAnimation — Cinematic AI scanning animation shown during analysis.
 */
import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';

const steps = [
  'Parsing content structure…',
  'Cross-referencing sources…',
  'Analyzing linguistic patterns…',
  'Running credibility model…',
];

export default function LoadingAnimation() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center gap-8 py-12"
    >
      {/* Central AI orb */}
      <div className="relative w-24 h-24 flex items-center justify-center">
        {/* Outer pulse rings */}
        {[1, 2, 3].map((i) => (
          <motion.div
            key={i}
            className="absolute inset-0 rounded-full border border-accent-blue/30"
            animate={{ scale: [1, 1.8 + i * 0.3], opacity: [0.5, 0] }}
            transition={{
              duration: 2,
              delay: i * 0.4,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        ))}

        {/* Core */}
        <div className="relative w-16 h-16 rounded-full flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, rgba(79,142,247,0.2), rgba(124,92,252,0.2))',
            boxShadow: '0 0 40px rgba(79,142,247,0.3)',
            border: '1px solid rgba(79,142,247,0.4)',
          }}
        >
          {/* Scan line inside core */}
          <div className="absolute inset-0 rounded-full overflow-hidden">
            <motion.div
              className="absolute left-0 right-0 h-0.5"
              style={{ background: 'linear-gradient(90deg, transparent, rgba(79,142,247,0.8), transparent)' }}
              animate={{ top: ['0%', '100%', '0%'] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            />
          </div>

          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
          >
            <Brain size={24} className="text-accent-blue" />
          </motion.div>
        </div>
      </div>

      {/* Animated steps */}
      <div className="flex flex-col gap-2 w-full max-w-xs">
        {steps.map((step, i) => (
          <motion.div
            key={step}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.55, duration: 0.4 }}
            className="flex items-center gap-3"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.55 + 0.2 }}
              className="w-1.5 h-1.5 rounded-full flex-shrink-0"
              style={{ background: i < 2 ? '#4f8ef7' : 'rgba(79,142,247,0.4)' }}
            />
            <span className="text-xs text-white/50 font-mono tracking-wide">{step}</span>
          </motion.div>
        ))}
      </div>

      {/* Progress bar */}
      <div className="w-full max-w-xs">
        <div className="flex justify-between text-xs text-white/30 mb-2">
          <span className="font-mono">ANALYZING</span>
          <motion.span
            className="font-mono"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            PROCESSING…
          </motion.span>
        </div>
        <div className="h-0.5 w-full rounded-full overflow-hidden bg-white/[0.06]">
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'linear-gradient(90deg, #4f8ef7, #7c5cfc)' }}
            animate={{ x: ['-100%', '100%'] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
          />
        </div>
      </div>
    </motion.div>
  );
}
