/**
 * AccuracySection — Showcases AI accuracy metrics with animated progress rings.
 */
import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

function CircleProgress({ value, color, label, sublabel }) {
  const [displayed, setDisplayed] = useState(0);
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } }, { threshold: 0.5 });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;
    const duration = 1400;
    const start = performance.now();
    const frame = (now) => {
      const t = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      setDisplayed(Math.round(ease * value));
      if (t < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }, [visible, value]);

  const r = 54;
  const circ = 2 * Math.PI * r;
  const dash = visible ? circ * (1 - value / 100) : circ;

  return (
    <div ref={ref} className="flex flex-col items-center gap-3">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          {/* Track */}
          <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6" />
          {/* Progress */}
          <motion.circle
            cx="60" cy="60" r={r}
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circ}
            initial={{ strokeDashoffset: circ }}
            animate={{ strokeDashoffset: dash }}
            transition={{ duration: 1.4, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
            style={{ filter: `drop-shadow(0 0 8px ${color}80)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{displayed}%</span>
        </div>
      </div>
      <div className="text-center">
        <div className="text-sm font-medium text-white">{label}</div>
        <div className="text-xs text-white/35 mt-0.5">{sublabel}</div>
      </div>
    </div>
  );
}

const metrics = [
  { value: 97, color: '#4f8ef7', label: 'Overall Accuracy', sublabel: 'On test dataset' },
  { value: 96, color: '#7c5cfc', label: 'Fake Detection',   sublabel: 'True positive rate' },
  { value: 98, color: '#22d3ee', label: 'Real Detection',   sublabel: 'True negative rate' },
  { value: 94, color: '#f472b6', label: 'Bias Signals',     sublabel: 'Indicator accuracy' },
];

const benchmarks = [
  { label: 'TruthLens AI',      value: 97.4, color: '#4f8ef7' },
  { label: 'GPT-4 Baseline',    value: 91.2, color: '#7c5cfc' },
  { label: 'Human Fact-checker',value: 88.7, color: '#22d3ee' },
  { label: 'BERT Base',         value: 84.1, color: '#a78bfa' },
];

function BenchmarkBar({ label, value, color, index }) {
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } }, { threshold: 0.3 });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={ref} className="flex items-center gap-4">
      <div className="w-36 text-sm text-white/60 text-right flex-shrink-0">{label}</div>
      <div className="flex-1 h-2 rounded-full overflow-hidden bg-white/[0.05]">
        <motion.div
          className="h-full rounded-full"
          initial={{ width: 0 }}
          animate={{ width: visible ? `${value}%` : 0 }}
          transition={{ delay: index * 0.1 + 0.2, duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
          style={{ background: color, boxShadow: `0 0 10px ${color}60` }}
        />
      </div>
      <div className="w-12 text-sm font-mono text-white/50 flex-shrink-0">{value}%</div>
    </div>
  );
}

export default function AccuracySection() {
  return (
    <section id="accuracy" className="relative py-28 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center mb-20"
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass text-xs font-medium text-white/50 tracking-widest uppercase mb-4">
            Performance
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Accuracy You Can <span className="gradient-text">Trust</span>
          </h2>
          <p className="text-white/40 max-w-md mx-auto">
            Rigorously tested across diverse news sources and fact-checked corpora.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Rings */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="grid grid-cols-2 gap-8 justify-items-center"
          >
            {metrics.map((m) => (
              <CircleProgress key={m.label} {...m} />
            ))}
          </motion.div>

          {/* Benchmark bars */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="glass rounded-2xl p-8"
          >
            <div className="text-sm font-medium text-white/60 mb-6 uppercase tracking-widest text-xs">
              Competitive Benchmark
            </div>
            <div className="flex flex-col gap-5">
              {benchmarks.map((b, i) => (
                <BenchmarkBar key={b.label} {...b} index={i} />
              ))}
            </div>
            <div className="mt-8 pt-6 border-t border-white/[0.05] text-xs text-white/25 leading-relaxed">
              Tested on LIAR-Plus, FakeNewsNet, and BuzzFeed Political News datasets.
              Benchmark conducted Q4 2024.
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
