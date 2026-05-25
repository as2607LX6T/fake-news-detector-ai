/**
 * HeroSection — Full-viewport hero with animated headline, subtext, and CTAs.
 */
import { motion } from 'framer-motion';
import { ArrowDown, Shield, Sparkles } from 'lucide-react';

const fadeUp = (delay = 0) => ({
  initial:   { opacity: 0, y: 40 },
  animate:   { opacity: 1, y: 0 },
  transition: { duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] },
});

export default function HeroSection() {
  const scrollToDetector = () => {
    document.querySelector('#detector')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center pt-24 pb-20 px-6 text-center overflow-hidden">

      {/* Badge */}
      <motion.div {...fadeUp(0.1)} className="mb-8">
        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass gradient-border text-xs font-medium text-white/70 tracking-wider uppercase">
          <Sparkles size={12} className="text-accent-blue" />
          AI-Powered News Intelligence
          <Sparkles size={12} className="text-accent-purple" />
        </span>
      </motion.div>

      {/* Headline */}
      <motion.h1 {...fadeUp(0.2)} className="max-w-4xl text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-[1.05] tracking-tight mb-6">
        <span className="text-white">Detect Lies.</span>
        <br />
        <span className="gradient-text">Reveal Truth.</span>
      </motion.h1>

      {/* Sub-headline */}
      <motion.p {...fadeUp(0.35)} className="max-w-2xl text-lg md:text-xl text-white/50 font-light leading-relaxed mb-12 text-balance">
        Advanced AI that cuts through misinformation in seconds.
        Paste any article or headline and get instant credibility analysis
        with confidence scoring.
      </motion.p>

      {/* CTAs */}
      <motion.div {...fadeUp(0.5)} className="flex flex-col sm:flex-row gap-4 items-center mb-20">
        <button
          onClick={scrollToDetector}
          className="btn-primary flex items-center gap-2 text-base"
        >
          <Shield size={18} strokeWidth={2} />
          Analyze Article
        </button>
        <a
          href="#how-it-works"
          onClick={(e) => {
            e.preventDefault();
            document.querySelector('#how-it-works')?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="px-8 py-4 rounded-2xl glass gradient-border text-white/70 hover:text-white text-base font-medium transition-all duration-300 hover:bg-white/[0.05]"
        >
          How It Works
        </a>
      </motion.div>

      {/* Stats row */}
      <motion.div
        {...fadeUp(0.65)}
        className="flex flex-wrap justify-center gap-12 mb-16"
      >
        {[
          { value: '97.4%', label: 'Accuracy Rate' },
          { value: '<2s',   label: 'Analysis Time' },
          { value: '50M+',  label: 'Articles Scanned' },
          { value: '12',    label: 'Bias Indicators' },
        ].map(({ value, label }) => (
          <div key={label} className="text-center">
            <div className="text-2xl md:text-3xl font-bold gradient-text mb-1">{value}</div>
            <div className="text-xs text-white/40 uppercase tracking-widest">{label}</div>
          </div>
        ))}
      </motion.div>

      {/* Scroll indicator */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.8 }}
        onClick={scrollToDetector}
        className="flex flex-col items-center gap-2 text-white/30 hover:text-white/60 transition-colors group"
        aria-label="Scroll down"
      >
        <span className="text-xs tracking-widest uppercase">Scroll</span>
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
        >
          <ArrowDown size={18} />
        </motion.div>
      </motion.button>

      {/* Decorative glowing line */}
      <motion.div
        initial={{ scaleX: 0, opacity: 0 }}
        animate={{ scaleX: 1, opacity: 1 }}
        transition={{ delay: 0.8, duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-px h-20"
        style={{
          background: 'linear-gradient(to bottom, rgba(79,142,247,0.6), transparent)',
        }}
      />
    </section>
  );
}
