/**
 * useScrollReveal — Returns a ref and visible boolean for scroll-triggered reveals.
 */
import { useEffect, useRef, useState } from 'react';

export function useScrollReveal(options = {}) {
  const ref     = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          // Once revealed, stop observing
          observer.unobserve(el);
        }
      },
      { threshold: 0.15, ...options }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return { ref, visible };
}
