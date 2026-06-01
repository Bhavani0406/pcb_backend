import React from 'react';
import { useAppStore } from './store';
import { Navbar } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { MCQScreen } from './components/MCQScreen';
import { VoiceScreen } from './components/VoiceScreen';
import { SummaryScreen } from './components/SummaryScreen';

export const App: React.FC = () => {
  const { current_view } = useAppStore();

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col relative">
      {/* Sleek cyber grid backdrop decoration */}
      <div className="absolute inset-0 bg-grid-pattern bg-[size:24px_24px] pointer-events-none opacity-40 z-0"></div>
      
      {/* Navbar always pinned to top */}
      <Navbar />

      {/* Dynamic page container */}
      <main className="flex-grow z-10 py-6 px-4">
        {current_view === 'dashboard' && <Dashboard />}
        {current_view === 'mcq' && <MCQScreen />}
        {current_view === 'voice' && <VoiceScreen />}
        {current_view === 'summary' && <SummaryScreen />}
      </main>

      {/* Decorative cyber signature footer (hidden in print) */}
      <footer className="w-full py-4 text-center border-t border-slate-900 bg-slate-950/40 text-[9px] font-mono tracking-widest text-slate-600 uppercase z-10 print:hidden">
        CORE-HARDWARE PANEL SIMULATOR // STATEDIFF: STATELESS_IN_MEMORY // PROT: SECURE_WS
      </footer>
    </div>
  );
};

export default App;
