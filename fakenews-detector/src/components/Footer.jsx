/**
 * Footer — Clean minimal footer with links and branding.
 */
import { motion } from 'framer-motion';
import { Scan, Github, Twitter, ExternalLink } from 'lucide-react';

const links = {
  Product: ['Detector', 'API Docs', 'Pricing', 'Changelog'],
  Resources: ['Research Paper', 'Dataset', 'Blog', 'Status'],
  Legal: ['Privacy Policy', 'Terms of Use', 'Cookie Policy', 'Contact'],
};

export default function Footer() {
  return (
    <footer className="relative border-t border-white/[0.05] pt-16 pb-10 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, #4f8ef7, #7c5cfc)' }}>
                <Scan size={16} className="text-white" strokeWidth={2.5} />
              </div>
              <span className="text-white font-semibold text-lg tracking-tight">
                Truth<span className="gradient-text">Lens</span>
              </span>
            </div>
            <p className="text-sm text-white/35 leading-relaxed mb-5">
              AI-powered misinformation detection for the modern internet.
            </p>
            <div className="flex gap-3">
              {[
                { icon: Github,  href: 'https://github.com', label: 'GitHub' },
                { icon: Twitter, href: 'https://twitter.com', label: 'Twitter' },
              ].map(({ icon: Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="w-9 h-9 rounded-xl glass flex items-center justify-center text-white/40 hover:text-white/80 transition-colors hover:bg-white/[0.05]"
                >
                  <Icon size={15} />
                </a>
              ))}
            </div>
          </div>

          {/* Link groups */}
          {Object.entries(links).map(([group, items]) => (
            <div key={group}>
              <div className="text-xs font-medium text-white/50 uppercase tracking-widest mb-5">{group}</div>
              <ul className="flex flex-col gap-3">
                {items.map(item => (
                  <li key={item}>
                    <a
                      href="#"
                      className="text-sm text-white/35 hover:text-white/70 transition-colors flex items-center gap-1 group"
                    >
                      {item}
                      <ExternalLink size={10} className="opacity-0 group-hover:opacity-60 transition-opacity" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-8 border-t border-white/[0.04]">
          <p className="text-xs text-white/25">
            © {new Date().getFullYear()} TruthLens. All rights reserved.
          </p>
          <p className="text-xs text-white/20 flex items-center gap-1.5">
            Built with
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="text-red-400/70"
            >
              ♥
            </motion.span>
            for a more informed world.
          </p>
        </div>
      </div>
    </footer>
  );
}
