/**
 * Navbar — Sticky top bar with blur-glass effect and responsive mobile menu.
 */
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Scan, Menu, X, Github, Zap } from 'lucide-react';

const navLinks = [
  { label: 'Detector',  href: '#detector' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Features',  href: '#features' },
  { label: 'About',     href: '#about' },
];

export default function Navbar() {
  const [scrolled,     setScrolled]     = useState(false);
  const [mobileOpen,   setMobileOpen]   = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleNavClick = (href) => {
    setMobileOpen(false);
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <>
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled
            ? 'py-3 bg-surface-900/80 backdrop-blur-2xl border-b border-white/[0.04] shadow-glass'
            : 'py-5'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          {/* Logo */}
          <a
            href="#"
            className="flex items-center gap-2.5 group"
            onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
          >
            <div className="relative w-8 h-8 flex items-center justify-center">
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple opacity-90 group-hover:opacity-100 transition-opacity" />
              <Scan size={16} className="relative z-10 text-white" strokeWidth={2.5} />
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple blur-md opacity-40 group-hover:opacity-70 transition-opacity" />
            </div>
            <span className="text-white font-semibold text-lg tracking-tight">
              Truth<span className="gradient-text">Lens</span>
            </span>
          </a>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <button
                key={link.href}
                onClick={() => handleNavClick(link.href)}
                className="px-4 py-2 text-sm text-white/60 hover:text-white/90 transition-colors duration-200 rounded-xl hover:bg-white/[0.04]"
              >
                {link.label}
              </button>
            ))}
          </div>

          {/* CTA */}
          <div className="hidden md:flex items-center gap-3">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-white/50 hover:text-white/80 transition-colors rounded-xl hover:bg-white/[0.04]"
              aria-label="GitHub"
            >
              <Github size={18} />
            </a>
            <button
              onClick={() => handleNavClick('#detector')}
              className="btn-primary !py-2 !px-5 text-sm flex items-center gap-2"
            >
              <Zap size={14} strokeWidth={2.5} />
              Try Now
            </button>
          </div>

          {/* Mobile menu toggle */}
          <button
            className="md:hidden p-2 text-white/70 hover:text-white rounded-xl hover:bg-white/[0.05] transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </motion.nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            className="fixed top-[60px] left-0 right-0 z-40 bg-surface-900/95 backdrop-blur-2xl border-b border-white/[0.06] md:hidden"
          >
            <div className="px-6 py-4 flex flex-col gap-1">
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => handleNavClick(link.href)}
                  className="w-full text-left px-4 py-3 text-white/70 hover:text-white hover:bg-white/[0.04] rounded-xl transition-colors text-sm"
                >
                  {link.label}
                </button>
              ))}
              <div className="mt-3 pt-3 border-t border-white/[0.06]">
                <button
                  onClick={() => handleNavClick('#detector')}
                  className="btn-primary w-full !py-3 text-sm flex items-center justify-center gap-2"
                >
                  <Zap size={14} strokeWidth={2.5} />
                  Try Now
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
