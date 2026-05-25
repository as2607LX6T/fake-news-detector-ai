/**
 * BackgroundEffects — Ambient floating orbs, grid, and noise texture.
 * Purely decorative, pointer-events: none throughout.
 */
export default function BackgroundEffects() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0" aria-hidden="true">
      {/* Grid */}
      <div className="absolute inset-0 grid-bg opacity-60" />

      {/* Orb 1 — top left blue */}
      <div
        className="orb orb-1"
        style={{
          width: '600px',
          height: '600px',
          top: '-200px',
          left: '-200px',
          background: 'radial-gradient(circle, rgba(79,142,247,0.18) 0%, transparent 70%)',
        }}
      />

      {/* Orb 2 — top right purple */}
      <div
        className="orb orb-2"
        style={{
          width: '700px',
          height: '700px',
          top: '-100px',
          right: '-250px',
          background: 'radial-gradient(circle, rgba(124,92,252,0.15) 0%, transparent 70%)',
        }}
      />

      {/* Orb 3 — mid-page cyan */}
      <div
        className="orb orb-3"
        style={{
          width: '500px',
          height: '500px',
          top: '40%',
          left: '25%',
          background: 'radial-gradient(circle, rgba(34,211,238,0.08) 0%, transparent 70%)',
        }}
      />

      {/* Orb 4 — bottom right */}
      <div
        className="orb orb-1"
        style={{
          width: '600px',
          height: '600px',
          bottom: '-200px',
          right: '-100px',
          background: 'radial-gradient(circle, rgba(79,142,247,0.12) 0%, transparent 70%)',
          animationDelay: '-4s',
        }}
      />

      {/* Vignette */}
      <div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at center, transparent 40%, rgba(8,8,16,0.7) 100%)',
        }}
      />
    </div>
  );
}
