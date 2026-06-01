import React from 'react';
import { useAppStore } from '../store';
import { Cpu, RotateCcw, AlertTriangle } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { current_view, resetSession, difficulty, style, error, setError } = useAppStore();

  return (
    <nav className="w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 py-4 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand logo & status indicator */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={resetSession}>
          <div className="p-2 bg-cyber-copperglow border border-cyber-copper/40 rounded-lg text-cyber-copper shadow-glow-copper/10">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-cyber-copper to-cyber-cyan bg-clip-text text-transparent font-sans">
              AETHER-PCB
            </h1>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
                AI Interview Panel v1.0
              </span>
            </div>
          </div>
        </div>

        {/* Global info or action buttons */}
        {current_view !== 'dashboard' && (
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-3 text-xs font-mono border border-slate-800 px-3 py-1.5 rounded-lg bg-slate-900/60">
              <span className="text-slate-500">STYLE:</span>
              <span className="text-cyber-cyan uppercase">{style}</span>
              <span className="text-slate-700">|</span>
              <span className="text-slate-500">LEVEL:</span>
              <span className={`uppercase font-bold ${
                difficulty === 'hard' ? 'text-rose-400' : difficulty === 'medium' ? 'text-amber-400' : 'text-emerald-400'
              }`}>{difficulty}</span>
            </div>

            <button
              onClick={resetSession}
              className="flex items-center gap-1.5 text-xs font-mono border border-slate-800 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 hover:border-slate-700 text-slate-300 transition-all cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              ABANDON SESSION
            </button>
          </div>
        )}
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="max-w-7xl mx-auto mt-4 px-4 py-3 bg-rose-950/40 border border-rose-800/80 rounded-lg text-rose-300 text-xs flex items-center justify-between gap-3 animate-bounce">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button 
            onClick={() => setError(null)} 
            className="font-mono font-bold hover:text-white px-2 py-1 hover:bg-rose-900/40 rounded transition-all"
          >
            DISMISS
          </button>
        </div>
      )}
    </nav>
  );
};
export default Navbar;
