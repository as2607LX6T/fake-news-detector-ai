/**
 * HowItWorks — Step-by-step process section with animated connectors.
 */
import { motion } from 'framer-motion';
import { Clipboard, Cpu, BarChart3, CheckCircle } from 'lucide-react';

const steps = [
  {
    icon:  Clipboard,
    step:  '01',
    title: 'Paste Content',
    desc:  'Drop any news article, headline, tweet, or paragraph into the detector input field.',
    color: '#4f8ef7',
  },
  {
    icon:  Cpu,
    step:  '02',
    title: 'AI Processing',
    desc:  'Our transformer model analyzes linguistic patterns, source signals, and sentiment indicators.',
    color: '#7c5cfc',
  },
  {
    icon:  BarChart3,
    step:  '03',
    title: 'Scoring',
    desc:  'A credibility score from 0–100 is calculated along with risk classification.',
    color: '#22d3ee',
  },
  {
    icon:  CheckCircle,
    step:  '04',
    title: 'Verdict',
    desc:  'Receive a clear Fake or Real verdict with detailed signal indicators.',
    color: '#4ade80',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="relative py-28 px-6">
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
            Process
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            How It <span className="gradient-text">Works</span>
          </h2>
          <p className="text-white/40 max-w-md mx-auto">
            From raw text to verified verdict in under two seconds.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Connecting line (desktop) */}
          <div
            className="hidden md:block absolute top-10 left-[12.5%] right-[12.5%] h-px"
            style={{ background: 'linear-gradient(90deg, transparent, rgba(79,142,247,0.3), rgba(124,92,252,0.3), rgba(34,211,238,0.3), transparent)' }}
          />

          {steps.map(({ icon: Icon, step, title, desc, color }, i) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.12, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col items-center text-center group"
            >
              {/* Icon circle */}
              <div className="relative mb-6 z-10">
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  className="w-20 h-20 rounded-2xl flex items-center justify-center glass transition-all duration-300 group-hover:shadow-glow-blue"
                  style={{
                    border: `1px solid ${color}25`,
                    background: `linear-gradient(135deg, ${color}12, transparent)`,
                  }}
                >
                  <Icon size={28} style={{ color }} strokeWidth={1.5} />
                </motion.div>
                {/* Step number */}
                <div
                  className="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                  style={{ background: color, boxShadow: `0 0 12px ${color}60` }}
                >
                  {i + 1}
                </div>
              </div>

              <div className="text-xs font-mono text-white/30 mb-2 tracking-widest">{step}</div>
              <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
              <p className="text-sm text-white/40 leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
