import React from 'react';
import { useAppStore } from '../store';
import { Award, Layers, Zap, Radio, CheckSquare, MessageSquare, Shield, HelpCircle, Flame } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const {
    difficulty,
    topic,
    style,
    loading,
    setDifficulty,
    setTopic,
    setStyle,
    initMCQSession,
    initVoiceSession
  } = useAppStore();

  const topics = [
    { name: 'General Hardware Design', icon: Layers, desc: 'Covering general analog, digital, and layout principles.' },
    { name: 'PCB Design Fundamentals', icon: Layers, desc: 'Layer stack-ups, copper weights, footprint geometries, and via types.' },
    { name: 'Advanced PCB Design', icon: Zap, desc: 'High-speed signal integrity, DDR routing, crosstalk, and return paths.' },
    { name: 'Analog Electronics', icon: HelpCircle, desc: 'BJTs, MOSFETs, Operational Amplifiers, differential pairs, and active filters.' },
    { name: 'Digital Electronics', icon: HelpCircle, desc: 'Setup/hold times, metastability, clock distribution, and FPGA constraints.' },
    { name: 'Embedded Systems', icon: HelpCircle, desc: 'ARM Cortex, DMA, interrupts, hardware buses (CAN, SPI, I2C, USB).' },
    { name: 'Power Electronics', icon: Flame, desc: 'DC-DC SMPS design (Buck, Boost), thermal vias, snubber layers.' },
    { name: 'EMI / EMC Compliance', icon: Shield, desc: 'Radiated emissions, ESD shielding, TVS diodes, CE/FCC regulations.' },
    { name: 'RF PCB Design', icon: Radio, desc: 'Microstrips, striplines, coplanar waveguides, antenna tuning.' },
    { name: 'PCB Manufacturing', icon: Layers, desc: 'DFM/DFA parameters, ENIG/HASL, reflow profiling, solder bridging.' },
    { name: 'Hardware Debugging', icon: Zap, desc: 'Oscilloscope probing, logic analyzer debugging, clock crash diagnosis.' }
  ];

  const companyStyles = [
    { name: 'Intel Board Division', desc: 'Focus: Multi-layer server motherboards, DDR5 fly-by, and high-speed memory interfaces.' },
    { name: 'Qualcomm RF Team', desc: 'Focus: BLE/WiFi radio layouts, coplanar impedance matching, S-parameters, VNA usage.' },
    { name: 'Nvidia GPU Architectures', desc: 'Focus: Extreme current draw transient response, PDN impedance target loops, thermal designs.' },
    { name: 'Texas Instruments Analog', desc: 'Focus: Low-noise active op-amps, switching regulators, snubber layers, ADC/DAC conversions.' },
    { name: 'Apple HDI Packaging', desc: 'Focus: High-Density Interconnect (HDI), microvias, compact multi-board arrangements, rigid-flex design.' },
    { name: 'Automotive Hardware Panel', desc: 'Focus: High voltage creepage & clearance, CAN bus protection, rugged design, thermal stress.' },
    { name: 'General Engineering Panel', desc: 'Focus: Well-balanced mixed signal hardware design and fundamental electronics principles.' }
  ];

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 font-sans">
      {/* Title Hero */}
      <div className="text-center mb-12">
        <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-cyber-copper via-slate-100 to-cyber-cyan bg-clip-text text-transparent">
          PCB & Hardware Interview Simulator
        </h2>
        <p className="mt-3 text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
          Experience realistic technical interview panels tailored for world-class hardware divisions. Statelessly test your schematic, physics, and layout skills.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Side Settings (Difficulty & Company Style) */}
        <div className="lg:col-span-1 space-y-6">
          {/* Difficulty Level */}
          <div className="glass-panel p-6 border-slate-800">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-cyber-copper">
              <Award className="w-5 h-5" />
              DIFFICULTY LEVEL
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {['easy', 'medium', 'hard'].map((level) => (
                <button
                  key={level}
                  onClick={() => setDifficulty(level)}
                  className={`py-2.5 rounded-lg font-mono text-xs uppercase font-bold tracking-wider transition-all border cursor-pointer ${
                    difficulty === level
                      ? 'bg-cyber-copper/10 border-cyber-copper text-cyber-copper shadow-glow-copper/5'
                      : 'bg-slate-950/40 border-slate-800 hover:border-slate-700 text-slate-400'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
            <p className="text-[10px] text-slate-500 mt-3 font-mono leading-relaxed">
              {difficulty === 'easy' && 'Focuses on basic RLC components, diode equations, bypass caps, DMM operations.'}
              {difficulty === 'medium' && 'Focuses on 4-layer stack-up, SPI/I2C buses, layout grounding, switcher loops.'}
              {difficulty === 'hard' && 'Focuses on DDR routing, differential microstrips, target PDN impedance, EMC shielding, RF parameters.'}
            </p>
          </div>

          {/* Company Interview Panel Accent */}
          <div className="glass-panel p-6 border-slate-800">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-cyber-cyan">
              <Layers className="w-5 h-5" />
              COMPANY PANEL STYLE
            </h3>
            <p className="text-[10px] text-slate-500 -mt-2 mb-4 font-mono leading-relaxed">
              Tunes question wording and emphasis toward a selected company-style interview panel.
            </p>
            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1 custom-scrollbar">
              {companyStyles.map((item) => (
                <button
                  key={item.name}
                  onClick={() => setStyle(item.name)}
                  className={`w-full text-left p-3 rounded-lg border text-xs transition-all cursor-pointer block ${
                    style === item.name
                      ? 'bg-cyber-cyan/10 border-cyber-cyan/60 text-cyber-cyan shadow-glow-cyan/5'
                      : 'bg-slate-950/40 border-slate-900 hover:bg-slate-900/60 hover:border-slate-800 text-slate-300'
                  }`}
                >
                  <span className="font-bold block font-sans text-[13px]">{item.name}</span>
                  <span className="text-[10px] text-slate-400 mt-1 block leading-normal">{item.desc}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Center/Right Side Topics Selection */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 border-slate-800">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-slate-200">
              <Zap className="w-5 h-5 text-cyber-gold" />
              INTERVIEW FOCUS TOPIC
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[460px] overflow-y-auto pr-1 custom-scrollbar">
              {topics.map((t) => {
                const IconComponent = t.icon;
                const isSelected = topic === t.name;
                return (
                  <div
                    key={t.name}
                    onClick={() => setTopic(t.name)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer flex gap-3 ${
                      isSelected
                        ? 'bg-slate-800/40 border-cyber-copper/40 shadow-glow-copper/5'
                        : 'bg-slate-950/30 border-slate-900 hover:border-slate-800 hover:bg-slate-900/20'
                    }`}
                  >
                    <div className={`p-2 h-fit rounded-lg border flex-shrink-0 ${
                      isSelected ? 'border-cyber-copper/50 text-cyber-copper bg-cyber-copperglow' : 'border-slate-800 text-slate-500'
                    }`}>
                      <IconComponent className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className={`text-xs font-bold font-sans text-[13px] ${isSelected ? 'text-cyber-copper' : 'text-slate-200'}`}>
                        {t.name}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1 leading-normal font-sans">
                        {t.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Simulator Initiation Deck */}
      <div className="mt-12 max-w-2xl mx-auto glass-panel p-8 border-slate-800/80 text-center relative overflow-hidden bg-slate-950/80">
        {/* Holographic grid border decoration */}
        <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-cyber-copper via-cyber-cyan to-cyber-green"></div>

        <h3 className="text-xl font-extrabold text-slate-200">Launch Interview Panel Simulation</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          Choose your evaluation channel. Live adaptive questioning algorithms will process your inputs dynamically.
        </p>

        {loading ? (
          <div className="flex flex-col items-center justify-center gap-3 mt-6 py-4">
            <span className="w-8 h-8 rounded-full border-2 border-cyber-copper border-t-transparent animate-spin"></span>
            <span className="font-mono text-xs text-slate-400 uppercase tracking-widest animate-pulse">
              Synthesizing Interview Environment...
            </span>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
            {/* Launch MCQ */}
            <button
              onClick={initMCQSession}
              className="group p-5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900 hover:border-cyber-copper/50 text-left transition-all cursor-pointer shadow-sm hover:shadow-glow-copper/5"
            >
              <div className="flex items-center justify-between">
                <span className="p-2 rounded-lg border border-slate-800 text-cyber-copper bg-slate-950 group-hover:bg-cyber-copperglow group-hover:border-cyber-copper/40 transition-colors">
                  <CheckSquare className="w-5 h-5" />
                </span>
                <span className="font-mono text-[9px] text-slate-500 uppercase font-bold">MODE: MCQ POOL</span>
              </div>
              <h4 className="text-sm font-bold text-slate-200 mt-4 group-hover:text-cyber-copper transition-colors">
                AI MCQ Assessment
              </h4>
              <p className="text-[11px] text-slate-400 mt-1 leading-normal">
                Generates a pool of 20 randomized, highly challenging technical multiple-choice items with instant grading and physics-based engineering rationale reviews.
              </p>
            </button>

            {/* Launch Voice */}
            <button
              onClick={initVoiceSession}
              className="group p-5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900 hover:border-cyber-cyan/50 text-left transition-all cursor-pointer shadow-sm hover:shadow-glow-cyan/5"
            >
              <div className="flex items-center justify-between">
                <span className="p-2 rounded-lg border border-slate-800 text-cyber-cyan bg-slate-950 group-hover:bg-cyan-950 group-hover:border-cyber-cyan/40 transition-colors">
                  <MessageSquare className="w-5 h-5" />
                </span>
                <span className="font-mono text-[9px] text-slate-500 uppercase font-bold">MODE: REAL-TIME INTERACTIVE</span>
              </div>
              <h4 className="text-sm font-bold text-slate-200 mt-4 group-hover:text-cyber-cyan transition-colors">
                Interactive Voice Interview
              </h4>
              <p className="text-[11px] text-slate-400 mt-1 leading-normal">
                Speak directly. Features an adaptive verbal question queue, live browser audio transcription, browser speech synthesis, and in-depth conceptual breakdown metrics.
              </p>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
export default Dashboard;
