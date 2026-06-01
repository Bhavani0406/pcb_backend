import React, { useEffect, useRef } from 'react';

interface WaveformProps {
  active: boolean;
  color?: 'copper' | 'cyan';
}

export const Waveform: React.FC<WaveformProps> = ({ active, color = 'copper' }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle high DPI screens
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;
    
    let phase = 0;
    const speed = active ? 0.15 : 0.03;
    const amplitudeBase = active ? 22 : 4;

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      
      const primaryColor = color === 'copper' ? '#f97316' : '#06b6d4';
      const secondaryColor = color === 'copper' ? 'rgba(249, 115, 22, 0.2)' : 'rgba(6, 182, 212, 0.2)';

      // 1. Draw grid background lines
      ctx.strokeStyle = 'rgba(30, 41, 59, 0.3)';
      ctx.lineWidth = 0.5;
      
      // Horizontal center line
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();

      // Vertical marker grids
      for (let x = 0; x < width; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }

      // 2. Draw Multi-layered sine waves
      // Draw secondary background wave first
      ctx.beginPath();
      ctx.strokeStyle = secondaryColor;
      ctx.lineWidth = 1;
      for (let x = 0; x < width; x++) {
        // Compose multiple sine inputs for complexity
        const sinInput1 = (x * 0.015) + phase;
        const sinInput2 = (x * 0.03) - phase * 0.5;
        const y = (height / 2) + Math.sin(sinInput1) * Math.cos(sinInput2) * (amplitudeBase * 0.7);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Draw primary main wave
      ctx.beginPath();
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 2;
      
      // Add subtle drop shadow glow
      ctx.shadowBlur = active ? 8 : 0;
      ctx.shadowColor = primaryColor;

      for (let x = 0; x < width; x++) {
        const sinInput1 = (x * 0.02) - phase;
        const sinInput2 = (x * 0.007) + phase * 0.8;
        // Fade amplitude at edges (Gaussian window-like envelope)
        const edgeEnvelope = Math.sin((x / width) * Math.PI);
        const y = (height / 2) + Math.sin(sinInput1) * Math.cos(sinInput2) * amplitudeBase * edgeEnvelope;
        
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      
      // Reset shadow
      ctx.shadowBlur = 0;

      phase += speed;
      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [active, color]);

  return (
    <div className="w-full relative glass-panel bg-slate-950/60 p-2 overflow-hidden h-24 flex items-center justify-center">
      {/* Decorative calibration grids */}
      <span className="absolute top-1 left-2 font-mono text-[8px] text-slate-600">CH1 [SIGNAL LOG]</span>
      <span className="absolute bottom-1 right-2 font-mono text-[8px] text-slate-600">50mV / div</span>
      <canvas 
        ref={canvasRef} 
        className="w-full h-full block"
      />
    </div>
  );
};
export default Waveform;
