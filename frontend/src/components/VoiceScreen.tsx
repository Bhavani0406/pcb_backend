import React, { useState, useEffect, useRef } from 'react';
import { useAppStore } from '../store';
import { Waveform } from './Waveform';
import { Mic, MicOff, Send, Award, ArrowRight, Play, AlertCircle, HelpCircle } from 'lucide-react';

export const VoiceScreen: React.FC = () => {
  const {
    voice_question,
    voice_audio,
    voice_evaluations,
    loading,
    transcription,
    is_recording,
    setRecording,
    setTranscription,
    setError,
    submitVoiceAnswer,
    finishVoiceSession,
  } = useAppStore();

  const [isSpeakingQuestion, setIsSpeakingQuestion] = useState(false);
  const [editingTranscript, setEditingTranscript] = useState('');
  const [showEvaluation, setShowEvaluation] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const [captureStatus, setCaptureStatus] = useState('Ready for microphone capture.');
  
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const finalTranscriptRef = useRef('');

  const activeEvaluation = voice_evaluations[voice_evaluations.length - 1];

  // 1. Core Web Speech API Speech Recognition hook
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscriptRef.current = `${finalTranscriptRef.current} ${event.results[i][0].transcript}`.trim();
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        
        const fullTranscript = `${finalTranscriptRef.current} ${interimTranscript}`.trim();
        if (fullTranscript) {
          setTranscription(fullTranscript);
          setEditingTranscript(fullTranscript);
          setCaptureStatus(interimTranscript ? 'Listening and transcribing...' : 'Speech captured.');
        }
      };

      recognition.onerror = (err: any) => {
        console.error('Speech recognition error:', err);
        const messageByCode: Record<string, string> = {
          'audio-capture': 'No microphone was detected. Check your input device.',
          'not-allowed': 'Microphone permission was blocked. Allow mic access for this site.',
          'no-speech': 'No speech was detected. Try again closer to the microphone.',
          network: 'Speech recognition network service is unavailable. You can type your answer below.',
        };
        const message = messageByCode[err.error] || 'Speech recognition stopped unexpectedly. You can type your answer below.';
        setCaptureStatus(message);
        setError(message);
        setRecording(false);
      };

      recognition.onend = () => {
        setRecording(false);
        if (!finalTranscriptRef.current && !editingTranscript) {
          setCaptureStatus('Capture stopped. No final speech was recognized yet.');
        }
      };

      recognitionRef.current = recognition;
    } else {
      console.warn('Browser does not support SpeechRecognition. Falling back to keyboard typing.');
      setSpeechSupported(false);
      setCaptureStatus('This browser does not support speech recognition. Type your answer below.');
    }
  }, []);

  // 2. TTS audio playback hook - automatically trigger when a new question arrives
  useEffect(() => {
    if (voice_audio) {
      playQuestionAudio();
    } else if (voice_question) {
      speakQuestionBrowserSynthesis();
    }
  }, [voice_question, voice_audio]);

  const playQuestionAudio = () => {
    if (!voice_audio) return;
    
    // Stop any current synthesis or audio
    stopAllSpeech();
    
    setIsSpeakingQuestion(true);
    const audio = new Audio(voice_audio);
    audioRef.current = audio;
    audio.onended = () => {
      setIsSpeakingQuestion(false);
    };
    audio.onerror = () => {
      setIsSpeakingQuestion(false);
      // Fallback
      speakQuestionBrowserSynthesis();
    };
    audio.play().catch(e => {
      console.warn('Autoplay blocked. User interaction required to play audio.', e);
      setIsSpeakingQuestion(false);
    });
  };

  const speakQuestionBrowserSynthesis = () => {
    if (!voice_question) return;
    
    stopAllSpeech();
    setIsSpeakingQuestion(true);
    
    const utterance = new SpeechSynthesisUtterance(voice_question);
    utterance.lang = 'en-US';
    // Choose a standard professional English speaker voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Natural') || v.lang === 'en-US');
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
    
    utterance.onend = () => {
      setIsSpeakingQuestion(false);
    };
    utterance.onerror = () => {
      setIsSpeakingQuestion(false);
    };
    
    window.speechSynthesis.speak(utterance);
  };

  const stopAllSpeech = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    window.speechSynthesis.cancel();
    setIsSpeakingQuestion(false);
  };

  const toggleRecording = async () => {
    if (!recognitionRef.current) {
      setCaptureStatus('Speech recognition is unavailable in this browser. Type your answer below.');
      return;
    }

    if (is_recording) {
      recognitionRef.current.stop();
      setRecording(false);
    } else {
      // Clear transcript state first
      setTranscription('');
      setEditingTranscript('');
      finalTranscriptRef.current = '';
      
      stopAllSpeech();
      try {
        if (navigator.mediaDevices?.getUserMedia) {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach((track) => track.stop());
        }
        recognitionRef.current.start();
        setRecording(true);
        setCaptureStatus('Microphone is active. Speak now.');
      } catch (e) {
        console.error('Recognition start error:', e);
        const message = 'Could not start microphone capture. Allow mic permission, then try again.';
        setCaptureStatus(message);
        setError(message);
        setRecording(false);
      }
    }
  };

  const handleSubmitAnswer = () => {
    const finalAnswer = editingTranscript || transcription;
    if (!finalAnswer.trim()) {
      alert('Please speak or type a response first.');
      return;
    }

    // Stop recording if active
    if (is_recording && recognitionRef.current) {
      recognitionRef.current.stop();
      setRecording(false);
    }

    stopAllSpeech();
    submitVoiceAnswer(finalAnswer);
    setShowEvaluation(true);
  };

  const handleNextQuestion = () => {
    setShowEvaluation(false);
    setTranscription('');
    setEditingTranscript('');
    finalTranscriptRef.current = '';
    setCaptureStatus('Ready for microphone capture.');
  };

  const handleFinish = async () => {
    stopAllSpeech();
    await finishVoiceSession();
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 font-sans select-text">
      {/* Header Info */}
      <div className="mb-6 flex items-center justify-between border-b border-slate-900 pb-4">
        <div>
          <span className="font-mono text-[10px] tracking-widest text-slate-500 uppercase">
            LIVE VERBAL SIMULATION
          </span>
          <h3 className="text-xl font-bold text-slate-200 mt-0.5">
            Technical Panel Discussion
          </h3>
        </div>
        <div className="text-right">
          <span className="font-mono text-xs uppercase bg-cyber-cyan/10 border border-cyber-cyan/30 text-cyber-cyan px-3 py-1 rounded-full font-bold shadow-glow-cyan/5">
            Questions Answered: {voice_evaluations.length}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        {/* Left Side (Question, Input Deck, Waveform): 7 Cols */}
        <div className="lg:col-span-7 space-y-6 flex flex-col justify-between">
          <div className="space-y-6">
            {/* Question Screen Card */}
            <div className="glass-panel p-6 sm:p-8 border-slate-800 bg-slate-950/40 relative overflow-hidden">
              <span className="font-mono text-[9px] text-cyber-cyan uppercase font-bold tracking-wider block mb-2">
                ACTIVE TECHNICAL INTERVIEWER QUESTION
              </span>
              
              <p className="text-[16px] sm:text-[18px] text-slate-200 leading-relaxed font-sans font-medium">
                {voice_question || "Preparing the next scenario. One moment..."}
              </p>

              {/* Play audio helper */}
              <div className="mt-4 flex items-center gap-2">
                <button
                  onClick={voice_audio ? playQuestionAudio : speakQuestionBrowserSynthesis}
                  disabled={isSpeakingQuestion}
                  className="flex items-center gap-1.5 text-[10px] font-mono border border-slate-800 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 transition-all cursor-pointer disabled:opacity-40"
                >
                  <Play className="w-3 h-3 fill-current" />
                  {isSpeakingQuestion ? 'PLAYING...' : 'REPLAY AUDIO'}
                </button>
                {isSpeakingQuestion && (
                  <span className="text-[10px] font-mono text-cyber-cyan tracking-wider animate-pulse uppercase">
                    Interviewer is speaking...
                  </span>
                )}
              </div>
            </div>

            {/* Signal Visualizer Waveform */}
            <Waveform active={is_recording || isSpeakingQuestion} color={is_recording ? 'copper' : 'cyan'} />

            {/* Transcription Deck */}
            <div className="glass-panel p-5 border-slate-800 bg-slate-950/30">
              <div className="flex items-center justify-between mb-3 border-b border-slate-900 pb-2">
                <span className="font-mono text-[9px] text-slate-500 uppercase font-bold tracking-wider">
                  TRANSCRIPTION EDITOR & CAPTURE CONSOLE
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {is_recording ? 'MICROPHONE ACTIVE - SPEAK NOW' : 'EDIT MODE'}
                </span>
              </div>

              <div className={`mb-3 rounded-lg border px-3 py-2 text-[11px] font-mono ${
                speechSupported
                  ? 'border-slate-800 bg-slate-950/40 text-slate-400'
                  : 'border-amber-700/50 bg-amber-950/20 text-amber-300'
              }`}>
                {captureStatus}
              </div>

              {/* Editable Text Area for transcription */}
              <textarea
                value={editingTranscript}
                onChange={(e) => setEditingTranscript(e.target.value)}
                placeholder="Speak into your microphone or manually type your response here... (Provide in-depth electrical engineering reasoning, including return paths, standards, or parasitics)."
                className="w-full h-36 bg-slate-950/40 border border-slate-900 rounded-lg p-3 text-sm text-slate-300 font-sans focus:outline-none focus:border-cyber-copper/60 transition-all resize-none custom-scrollbar"
              />
            </div>
          </div>

          {/* User Controls Panel */}
          <div className="flex items-center gap-4 pt-4 border-t border-slate-900">
            {/* Pulsating Record Button */}
            <button
              onClick={toggleRecording}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl border font-mono text-xs uppercase font-bold tracking-wider transition-all cursor-pointer select-none ${
                is_recording
                  ? 'bg-rose-950/40 border-rose-600 text-rose-300 glow-orb-copper shadow-glow-copper/20'
                  : 'bg-cyber-copperglow border-cyber-copper/50 text-cyber-copper hover:border-cyber-copper hover:shadow-glow-copper/10'
              }`}
            >
              {is_recording ? <MicOff className="w-4 h-4 text-rose-400 animate-pulse" /> : <Mic className="w-4 h-4" />}
              {is_recording ? 'STOP CAPTURING' : 'START SPEAKING'}
            </button>

            {/* Keyboard Submit Button */}
            <button
              onClick={handleSubmitAnswer}
              disabled={loading || !(editingTranscript || transcription).trim()}
              className="flex-grow flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-cyber-cyan bg-cyber-cyan/10 hover:bg-cyber-cyan hover:text-slate-950 text-cyber-cyan font-mono text-xs uppercase font-bold tracking-wider transition-all disabled:opacity-30 disabled:pointer-events-none cursor-pointer"
            >
              <Send className="w-4 h-4" />
              {loading ? 'SUBMITTING...' : 'SUBMIT TECHNICAL ANSWER'}
            </button>
          </div>
        </div>

        {/* Right Side (Active Question Grade & Feedback Summary): 5 Cols */}
        <div className="lg:col-span-5">
          {showEvaluation && activeEvaluation ? (
            <div className="glass-panel p-5 sm:p-6 border-slate-800 bg-slate-950/60 h-full flex flex-col justify-between overflow-hidden relative">
              {/* Overlay loading spinner */}
              {loading && (
                <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center gap-3">
                  <span className="w-8 h-8 rounded-full border-2 border-cyber-cyan border-t-transparent animate-spin"></span>
                  <span className="font-mono text-[10px] text-slate-400 tracking-widest uppercase animate-pulse">
                    Evaluating response metrics...
                  </span>
                </div>
              )}

              <div>
                {/* Score badge & ratings */}
                <div className="flex items-center justify-between border-b border-slate-900 pb-3 mb-4">
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 bg-cyber-cyan/10 rounded-lg text-cyber-cyan border border-cyber-cyan/30">
                      <Award className="w-4 h-4" />
                    </span>
                    <span className="font-mono text-xs font-bold text-slate-200">GRADE ASSESSMENT</span>
                  </div>
                  <div className="flex items-baseline gap-1 bg-slate-900 px-3 py-1 rounded-lg border border-slate-800 shadow-sm">
                    <span className="text-xl font-extrabold text-cyber-copper">{activeEvaluation.score}</span>
                    <span className="text-[10px] font-mono text-slate-500">/ 10</span>
                  </div>
                </div>

                {/* Granular Axis Bars */}
                <div className="space-y-2 mb-6">
                  {[
                    { label: 'Correctness', val: activeEvaluation.technical_analysis.correctness },
                    { label: 'Technical Depth', val: activeEvaluation.technical_analysis.technical_depth },
                    { label: 'Problem Solving', val: activeEvaluation.technical_analysis.problem_solving },
                    { label: 'Communication', val: activeEvaluation.technical_analysis.communication },
                    { label: 'Practical', val: activeEvaluation.technical_analysis.practical_understanding }
                  ].map((axis) => (
                    <div key={axis.label} className="text-xs font-mono">
                      <div className="flex justify-between text-slate-400 text-[10px] uppercase font-medium">
                        <span>{axis.label}</span>
                        <span className="text-slate-300 font-bold">{axis.val}/10</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden mt-0.5 border border-slate-900">
                        <div 
                          className="bg-cyber-cyan h-full transition-all duration-300"
                          style={{ width: `${axis.val * 10}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Strengths & Weaknesses (tabs or list) */}
                <div className="space-y-4 max-h-[220px] overflow-y-auto pr-1 custom-scrollbar">
                  <div>
                    <h5 className="text-[10px] font-mono tracking-widest text-emerald-400 uppercase font-bold flex items-center gap-1">
                      ✓ STRENGTHS IDENTIFIED
                    </h5>
                    <ul className="text-xs text-slate-300 font-sans mt-1.5 space-y-1 pl-1">
                      {activeEvaluation.strengths.map((str, idx) => (
                        <li key={idx} className="flex items-start gap-1.5 leading-relaxed">
                          <span className="text-emerald-500 font-bold flex-shrink-0">•</span>
                          <span>{str}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h5 className="text-[10px] font-mono tracking-widest text-rose-400 uppercase font-bold flex items-center gap-1">
                      ✗ OPPORTUNITIES FOR DEPTH
                    </h5>
                    <ul className="text-xs text-slate-300 font-sans mt-1.5 space-y-1 pl-1">
                      {activeEvaluation.weaknesses.map((weak, idx) => (
                        <li key={idx} className="flex items-start gap-1.5 leading-relaxed">
                          <span className="text-rose-500 font-bold flex-shrink-0">•</span>
                          <span>{weak}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h5 className="text-[10px] font-mono tracking-widest text-cyber-cyan uppercase font-bold flex items-center gap-1">
                      <HelpCircle className="w-3 h-3" /> SENIOR REFERENCE ANSWER
                    </h5>
                    <p className="text-[11px] font-mono text-slate-400 mt-1.5 bg-slate-900/50 p-2.5 rounded border border-slate-900/80 leading-relaxed">
                      {activeEvaluation.ideal_answer}
                    </p>
                  </div>
                </div>
              </div>

              {/* Next controls */}
              <div className="flex items-center gap-3 mt-6 border-t border-slate-900 pt-4 bg-slate-950/20">
                <button
                  onClick={handleNextQuestion}
                  className="flex-grow flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg font-mono text-xs font-bold uppercase tracking-wider bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200 transition-all cursor-pointer"
                >
                  START NEXT QUESTION
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={handleFinish}
                  className="px-4 py-2.5 rounded-lg font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-cyber-copper to-cyber-cyan text-slate-950 hover:shadow-glow-copper/15 transition-all cursor-pointer"
                >
                  CONCLUDE DISCUSSION
                </button>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-6 border-slate-900 bg-slate-950/20 text-center flex flex-col items-center justify-center min-h-[360px] h-full text-slate-500">
              <AlertCircle className="w-12 h-12 stroke-1 stroke-slate-700 animate-pulse mb-3" />
              <p className="text-xs font-mono max-w-[220px] mx-auto leading-relaxed uppercase tracking-wider text-slate-600">
                Awaiting Candidate Voice Response Transcript Submission...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default VoiceScreen;
