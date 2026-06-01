import React from 'react';
import { useAppStore } from '../store';
import { Cpu, BookOpen, Printer, RefreshCw, CheckCircle, ShieldAlert } from 'lucide-react';

export const SummaryScreen: React.FC = () => {
  const {
    interview_type,
    mcq_summary,
    voice_summary,
    resetSession,
    difficulty,
    style,
    topic
  } = useAppStore();

  const handlePrint = () => {
    window.print();
  };

  const isMCQ = interview_type === 'mcq';
  
  // Extract info safely depending on mode
  const overallScore = isMCQ 
    ? mcq_summary?.score_percentage 
    : voice_summary?.overall_score;

  const totalQuestions = isMCQ 
    ? mcq_summary?.total_questions 
    : voice_summary?.total_questions;

  const feedbackSummary = isMCQ 
    ? mcq_summary?.analytics.feedback 
    : voice_summary?.feedback_summary;

  const strengths = isMCQ
    ? mcq_summary?.analytics.strengths ?? []
    : [];

  const weaknesses = isMCQ
    ? mcq_summary?.analytics.weaknesses ?? []
    : [];

  const recommendations: string[] = isMCQ
    ? ["Practice circuit calculations daily.", "Review active filter topologies and operational parameters."]
    : voice_summary?.recommendations || [];

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 font-sans select-text print:bg-white print:text-slate-950">
      {/* Printable Report Header (hidden in screen, visible in print) */}
      <div className="hidden print:block text-center border-b-2 border-slate-900 pb-6 mb-8">
        <h1 className="text-3xl font-extrabold tracking-wider">AETHER-PCB PERFORMANCE REPORT</h1>
        <p className="text-xs font-mono text-slate-500 uppercase mt-1">
          CONFIDENTIAL TECHNICAL SCREENING BRIEFING
        </p>
        <div className="grid grid-cols-4 gap-4 mt-6 text-xs text-left font-mono">
          <div><strong>INTERVIEW TYPE:</strong> <span className="uppercase">{interview_type}</span></div>
          <div><strong>DIFFICULTY:</strong> <span className="uppercase">{difficulty}</span></div>
          <div><strong>FOCUS AREA:</strong> <span className="uppercase">{topic}</span></div>
          <div><strong>PANEL ACCENT:</strong> <span className="uppercase">{style}</span></div>
        </div>
      </div>

      {/* Screen Header Info */}
      <div className="mb-8 flex items-center justify-between border-b border-slate-900 pb-4 print:hidden">
        <div>
          <span className="font-mono text-[10px] tracking-widest text-slate-500 uppercase">
            EVALUATION COMPLETED
          </span>
          <h3 className="text-2xl font-bold text-slate-200 mt-0.5">
            Technical Panel Briefing
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 text-xs font-mono border border-slate-800 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 transition-all cursor-pointer"
          >
            <Printer className="w-3.5 h-3.5" />
            EXPORT ASSESSMENT BRIEF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Side: Score Board */}
        <div className="md:col-span-1 space-y-6">
          <div className="glass-panel p-6 border-slate-800 bg-slate-950/40 text-center relative overflow-hidden print:border-slate-300 print:bg-slate-100">
            {/* Holographic glowing ring decoration */}
            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-cyber-copper to-cyber-cyan"></div>
            
            <h4 className="font-mono text-[10px] tracking-widest text-slate-400 uppercase font-bold">
              CONSOLIDATED score
            </h4>

            {/* Score Orb */}
            <div className="my-8 flex flex-col items-center justify-center">
              <div className="w-36 h-36 rounded-full border-4 border-cyber-copper/20 flex flex-col items-center justify-center relative bg-slate-950/80 shadow-glow-copper/10 print:bg-white print:border-slate-300">
                <span className="text-4xl font-extrabold text-cyber-copper font-sans">
                  {overallScore}
                </span>
                <span className="text-[10px] font-mono text-slate-500 uppercase font-bold mt-1">
                  {isMCQ ? 'ACCURACY %' : 'RATING / 10'}
                </span>
              </div>
            </div>

            <div className="text-xs font-mono text-slate-400 space-y-1">
              <div>QUESTIONS POOL: {totalQuestions}</div>
              <div>LEVEL METRIC: {difficulty.toUpperCase()}</div>
            </div>
          </div>

          {/* Voice metrics details if Voice Interview */}
          {!isMCQ && voice_summary && (
            <div className="glass-panel p-5 border-slate-800/80 bg-slate-950/40 print:border-slate-300 print:bg-slate-100">
              <h4 className="font-mono text-[10px] tracking-widest text-cyber-cyan uppercase font-bold mb-4">
                CORE TECHNICAL RATINGS
              </h4>
              <div className="space-y-3 font-mono text-xs">
                {[
                  { label: 'Technical Depth', val: voice_summary.technical_depth_avg },
                  { label: 'Problem Solving', val: voice_summary.problem_solving_avg },
                  { label: 'Communication', val: voice_summary.communication_avg },
                  { label: 'Practical Layout', val: voice_summary.practical_understanding_avg }
                ].map((item) => (
                  <div key={item.label}>
                    <div className="flex justify-between text-slate-400 text-[10px]">
                      <span>{item.label}</span>
                      <span className="text-slate-200 font-bold">{item.val}/10</span>
                    </div>
                    <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden mt-1 border border-slate-900 print:bg-slate-300">
                      <div 
                        className="bg-cyber-cyan h-full"
                        style={{ width: `${item.val * 10}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Performance Summary Logs & Strengths */}
        <div className="md:col-span-2 space-y-6">
          {/* Summary Executive Summary */}
          <div className="glass-panel p-6 border-slate-800 bg-slate-950/40 print:border-slate-300 print:bg-slate-100">
            <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
              <Cpu className="w-4 h-4 text-cyber-copper" />
              Executive Evaluation Summary
            </h4>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans font-medium print:text-slate-800">
              {feedbackSummary || "Simulation concluded successfully. No major defects flagged in the reasoning trace logs."}
            </p>
          </div>

          {/* Topic diagnostics list */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Strengths */}
            <div className="glass-panel p-5 border-slate-800/80 bg-slate-950/40 print:border-slate-300 print:bg-slate-100">
              <h5 className="text-[10px] font-mono tracking-widest text-emerald-400 uppercase font-bold flex items-center gap-1.5 mb-3">
                <CheckCircle className="w-4 h-4 text-emerald-500" />
                STRENGTHS RECORDED
              </h5>
              {strengths.length > 0 ? (
                <ul className="text-xs text-slate-300 font-sans space-y-2 leading-relaxed print:text-slate-800">
                  {strengths.map((str: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-emerald-500">•</span>
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-500 font-sans">
                  Demonstrated solid understanding of PCB routing physics, trace loop inductions, and decoupling layout requirements.
                </p>
              )}
            </div>

            {/* Weaknesses */}
            <div className="glass-panel p-5 border-slate-800/80 bg-slate-950/40 print:border-slate-300 print:bg-slate-100">
              <h5 className="text-[10px] font-mono tracking-widest text-rose-400 uppercase font-bold flex items-center gap-1.5 mb-3">
                <ShieldAlert className="w-4 h-4 text-rose-500" />
                OPPORTUNITIES FLAGGED
              </h5>
              {weaknesses.length > 0 ? (
                <ul className="text-xs text-slate-300 font-sans space-y-2 leading-relaxed print:text-slate-800">
                  {weaknesses.map((weak: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-rose-500">•</span>
                      <span>{weak}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-500 font-sans">
                  Focus on studying microvia aspect ratios, copper thickness capacity calculations, and EMI shielding configurations.
                </p>
              )}
            </div>
          </div>

          {/* Actionable Engineering recommendations list */}
          <div className="glass-panel p-5 border-slate-800/80 bg-slate-950/40 print:border-slate-300 print:bg-slate-100">
            <h4 className="text-xs font-bold font-sans text-cyber-cyan flex items-center gap-1.5 uppercase tracking-wider mb-4">
              <BookOpen className="w-4 h-4 text-cyber-cyan" />
              Strategic Study Guidelines
            </h4>
            <ul className="text-xs text-slate-300 font-sans space-y-3 leading-relaxed pl-1 print:text-slate-800">
              {recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full border border-cyber-cyan/30 text-cyber-cyan flex items-center justify-center font-mono text-[10px] font-bold bg-cyber-cyan/5 flex-shrink-0">
                    {idx + 1}
                  </span>
                  <span className="pt-0.5">{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Reset Action */}
          <div className="pt-4 flex items-center justify-center print:hidden">
            <button
              onClick={resetSession}
              className="flex items-center gap-2 px-8 py-3 rounded-xl border border-cyber-copper bg-cyber-copperglow text-cyber-copper font-mono text-xs uppercase font-bold tracking-wider hover:border-cyber-copper hover:shadow-glow-copper/10 transition-all cursor-pointer"
            >
              <RefreshCw className="w-4 h-4 animate-spin-slow" />
              START A NEW INTERVIEW ROUND
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default SummaryScreen;
