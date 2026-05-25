/**
 * App.jsx — Root component. Assembles all page sections.
 */
import { motion } from 'framer-motion';
import BackgroundEffects from './components/BackgroundEffects';
import Navbar           from './components/Navbar';
import HeroSection      from './components/HeroSection';
import DetectorCard     from './components/DetectorCard';
import HowItWorks       from './components/HowItWorks';
import FeatureCards     from './components/FeatureCards';
import AccuracySection  from './components/AccuracySection';
import AboutSection     from './components/AboutSection';
import Footer           from './components/Footer';

export default function App() {
  return (
    <div className="relative min-h-screen bg-surface-900 text-white overflow-x-hidden">
      {/* Global ambient background */}
      <BackgroundEffects />

      {/* Page content — above background */}
      <div className="relative z-10">
        <Navbar />

        <main>
          <HeroSection />
          <DetectorCard />
          <HowItWorks />
          <FeatureCards />
          <AccuracySection />
          <AboutSection />
        </main>

        <Footer />
      </div>
    </div>
  );
}
