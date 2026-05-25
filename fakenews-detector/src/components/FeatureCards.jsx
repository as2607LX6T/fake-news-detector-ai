/**
 * FeatureCards — Grid of feature highlights with glassmorphic cards.
 */
import { motion } from 'framer-motion';
import {
  Brain, Zap, Globe, Lock,
  TrendingUp, MessageSquare, ShieldCheck, Layers,
} from 'lucide-react';

const features = [
  {
    icon:  Brain,
    title: 'Transformer NLP',
    desc:  'Fine-tuned BERT model trained on 2M+ labeled news articles across 40+ topics.',
    color: '#4f8ef7',
    large: true,
  },
  {
    icon:  Zap,
    title: 'Sub-2s Analysis',
    desc:  'GPU-accelerated inference delivers results instantly.',
    color: '#7c5cfc',
  },
  {
    icon:  Globe,
    title: 'Multi-language',
    desc:  'Supports 28 languages with equal accuracy across all.',
    color: '#22d3ee',
  },
  {
    icon:  Lock,
    title: 'Private by Design',
    desc:  'Your text is never stored. Zero data retention policy.',
    color: '#f472b6',
  },
  {
    icon:  TrendingUp,
    title: '97.4% Accuracy',
    desc:  'Validated against human fact-checkers on held-out test sets.',
    color: '#4ade80',
    large: true,
  },
  {
    icon:  MessageSquare,
    title: 'Headline Analysis',
    desc:  'Optimized for short-form content — even single sentences.',
    color: '#fb923c',
  },
  {
    icon:  ShieldCheck,
    title: 'Bias Detection',
    desc:  'Identifies 12 types of media bias beyond just factual accuracy.',
    color: '#a78bfa',
  },
  {
    icon:  Layers,
    title: 'Open API',
    desc:  'RESTful API with SDKs for Python, Node, and Go.',
    color: '#34d399',
  },
];

export default function FeatureCards() {
  return (
    <section id="features" className="relative py-28 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass text-xs font-medium text-white/50 tracking-widest uppercase mb-4">
            Features
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Built for <span className="gradient-text">Precision</span>
          </h2>
          <p className="text-white/40 max-w-md mx-auto">
            Every component engineered for speed, accuracy, and privacy.
          </p>
        </motion.div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map(({ icon: Icon, title, desc, color, large }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.07, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className={`group relative rounded-2xl p-6 glass transition-all duration-500 cursor-default
                hover:bg-white/[0.04] hover:-translate-y-1
                ${large ? 'sm:col-span-2' : ''}
              `}
              style={{
                border: '1px solid rgba(255,255,255,0.05)',
              }}
            >
              {/* Hover glow */}
              <div
                className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                style={{
                  background: `radial-gradient(circle at 50% 0%, ${color}12 0%, transparent 70%)`,
                }}
              />

              {/* Icon */}
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110"
                style={{
                  background: `linear-gradient(135deg, ${color}18, ${color}08)`,
                  border: `1px solid ${color}25`,
                }}
              >
                <Icon size={22} style={{ color }} strokeWidth={1.5} />
              </div>

              <h3 className="text-base font-semibold text-white mb-2">{title}</h3>
              <p className="text-sm text-white/40 leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
