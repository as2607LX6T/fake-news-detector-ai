/**
 * AboutSection — Project mission and team description.
 */
import { motion } from 'framer-motion';
import { Heart, Globe, Code2 } from 'lucide-react';

export default function AboutSection() {
  return (
    <section id="about" className="relative py-28 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left — text */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <span className="inline-block px-4 py-1.5 rounded-full glass text-xs font-medium text-white/50 tracking-widest uppercase mb-6">
              About
            </span>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
              Fighting Misinformation
              <br />
              <span className="gradient-text">At Scale</span>
            </h2>
            <p className="text-white/50 leading-relaxed mb-5">
              TruthLens was built in response to the accelerating spread of
              AI-generated misinformation. We believe everyone deserves access
              to tools that help distinguish fact from fiction.
            </p>
            <p className="text-white/40 leading-relaxed text-sm">
              Our model is trained on millions of verified and debunked articles
              sourced from reputable fact-checking organizations worldwide, including
              Snopes, PolitiFact, and FactCheck.org.
            </p>

            <div className="flex gap-6 mt-10">
              {[
                { icon: Heart, label: 'Open Source' },
                { icon: Globe, label: 'Global Coverage' },
                { icon: Code2, label: 'API First' },
              ].map(({ icon: Icon, label }) => (
                <div key={label} className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-xl glass flex items-center justify-center">
                    <Icon size={16} className="text-accent-blue" />
                  </div>
                  <span className="text-xs text-white/40">{label}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right — quote card */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="relative"
          >
            <div
              className="relative rounded-3xl p-8 overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, rgba(79,142,247,0.08), rgba(124,92,252,0.08))',
                border: '1px solid rgba(79,142,247,0.15)',
              }}
            >
              {/* Decorative glow */}
              <div
                className="absolute top-0 right-0 w-48 h-48 rounded-full pointer-events-none"
                style={{
                  background: 'radial-gradient(circle, rgba(124,92,252,0.2) 0%, transparent 70%)',
                  filter: 'blur(30px)',
                  transform: 'translate(30%, -30%)',
                }}
              />

              <div className="text-5xl text-white/10 font-serif mb-4 leading-none">"</div>
              <p className="text-white/70 text-lg leading-relaxed mb-6 italic font-light">
                Truth is not partisan. Our mission is to arm every reader —
                regardless of background or belief — with the same analytical
                tools that professional fact-checkers use.
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white"
                  style={{ background: 'linear-gradient(135deg, #4f8ef7, #7c5cfc)' }}>
                  TL
                </div>
                <div>
                  <div className="text-sm font-medium text-white">TruthLens Team</div>
                  <div className="text-xs text-white/35">AI Research & Engineering</div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
