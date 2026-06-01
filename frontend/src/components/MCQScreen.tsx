import React, { useState } from 'react';
import { useAppStore } from '../store';
import { CheckCircle2, XCircle, AlertCircle, ArrowRight, Award } from 'lucide-react';

export const MCQScreen: React.FC = () => {
  const {
    mcq_questions,
    current_mcq_index,
    mcq_answers,
    loading,
    submitMCQAnswer,
    finishMCQSession,
  } = useAppStore();

  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const activeQuestion = mcq_questions[current_mcq_index];
  const isLastQuestion = current_mcq_index === mcq_questions.length - 1;
  
  if (!activeQuestion) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center p-6">
        <span className="w-8 h-8 rounded-full border-2 border-cyber-copper border-t-transparent animate-spin"></span>
        <p className="mt-4 text-xs font-mono tracking-widest text-slate-400">LOADING QUESTION BANK...</p>
      </div>
    );
  }

  const answer = mcq_answers[activeQuestion.id];
  const isAnswered = !!answer;

  const handleOptionSelect = (optionId: string) => {
    if (isAnswered) return;
    setSelectedOption(optionId);
  };

  const handleSubmit = async () => {
    if (!selectedOption || isAnswered) return;
    await submitMCQAnswer(activeQuestion.id, selectedOption);
  };

  const handleNext = () => {
    setSelectedOption(null);
    useAppStore.setState({ current_mcq_index: current_mcq_index + 1 });
  };

  const handleFinish = async () => {
    await finishMCQSession();
  };

  // Progress Bar
  const total = mcq_questions.length;
  const progressPercent = ((current_mcq_index) / total) * 100;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 font-sans">
      {/* Session Progress Deck */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <span className="font-mono text-[10px] tracking-widest text-slate-500 uppercase">
            TECHNICAL ROUND ASSESSMENT
          </span>
          <h3 className="text-lg font-bold text-slate-200 mt-0.5">
            Question {current_mcq_index + 1} <span className="text-slate-500 font-normal">of {total}</span>
          </h3>
        </div>
        <div className="text-right">
          <span className="font-mono text-[10px] tracking-widest text-cyber-copper uppercase font-bold">
            TOPIC: {activeQuestion.topic}
          </span>
          <div className="text-xs text-slate-500 font-mono mt-0.5">
            Weight: {activeQuestion.difficulty_weight} / 10
          </div>
        </div>
      </div>

      {/* Progress Track */}
      <div className="w-full bg-slate-900 h-1 rounded-full overflow-hidden mb-8 border border-slate-950">
        <div 
          className="bg-gradient-to-r from-cyber-copper to-cyber-cyan h-full transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Question & Options */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 sm:p-8 border-slate-800 bg-slate-950/40 relative overflow-hidden">
            {/* Visual corner accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-slate-800"></div>
            <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-slate-800"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-slate-800"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-slate-800"></div>
            
            <p className="text-[15px] sm:text-[17px] text-slate-200 leading-relaxed font-sans font-medium">
              {activeQuestion.question}
            </p>
          </div>

          {/* Options deck */}
          <div className="space-y-3">
            {activeQuestion.options.map((opt) => {
              const isSelected = selectedOption === opt.id;
              const isCorrectOpt = opt.id === answer?.correct_option;
              const isUserWrongOpt = isAnswered && opt.id === answer?.selected_option && !answer.is_correct;
              
              let borderClass = 'border-slate-800 hover:border-slate-700 bg-slate-950/20';
              let circleBg = 'border-slate-700 text-slate-500';
              
              if (isSelected && !isAnswered) {
                borderClass = 'border-cyber-copper/60 bg-cyber-copperglow';
                circleBg = 'border-cyber-copper text-cyber-copper bg-cyber-copper/10';
              } else if (isAnswered) {
                if (isCorrectOpt) {
                  borderClass = 'border-emerald-600/70 bg-emerald-950/20 text-emerald-200';
                  circleBg = 'border-emerald-500 bg-emerald-500 text-slate-950';
                } else if (isUserWrongOpt) {
                  borderClass = 'border-rose-800/70 bg-rose-950/20 text-rose-200';
                  circleBg = 'border-rose-500 bg-rose-500 text-slate-950';
                } else {
                  borderClass = 'border-slate-900 bg-slate-950/10 opacity-40';
                  circleBg = 'border-slate-800 text-slate-700';
                }
              }

              return (
                <div
                  key={opt.id}
                  onClick={() => handleOptionSelect(opt.id)}
                  className={`flex items-start gap-4 p-4 rounded-xl border transition-all duration-200 select-none ${
                    !isAnswered ? 'cursor-pointer' : 'cursor-default'
                  } ${borderClass}`}
                >
                  <span className={`w-6 h-6 rounded-full border flex items-center justify-center font-mono text-xs font-bold flex-shrink-0 transition-colors ${circleBg}`}>
                    {isCorrectOpt && isAnswered ? '✓' : isUserWrongOpt ? '✗' : opt.id}
                  </span>
                  <span className="text-xs sm:text-sm font-sans text-slate-300 leading-normal pt-0.5">
                    {opt.text}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Action trigger button */}
          <div className="flex items-center justify-between pt-4">
            <div>
              {isAnswered && (
                <div className="flex items-center gap-2">
                  {answer.is_correct ? (
                    <div className="flex items-center gap-1 text-emerald-400 font-bold text-xs uppercase font-mono bg-emerald-950/30 px-3 py-1.5 rounded-lg border border-emerald-900">
                      <CheckCircle2 className="w-4 h-4" /> Correct Answer
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-rose-400 font-bold text-xs uppercase font-mono bg-rose-950/30 px-3 py-1.5 rounded-lg border border-rose-900">
                      <XCircle className="w-4 h-4" /> Incorrect Answer
                    </div>
                  )}
                </div>
              )}
            </div>

            <div>
              {!isAnswered ? (
                <button
                  onClick={handleSubmit}
                  disabled={!selectedOption || loading}
                  className="px-6 py-2.5 rounded-lg font-mono text-xs font-bold uppercase tracking-wider bg-cyber-copper text-slate-950 border border-cyber-copper hover:shadow-glow-copper/20 transition-all disabled:opacity-40 disabled:pointer-events-none cursor-pointer"
                >
                  {loading ? 'ANALYZING...' : 'SUBMIT ANSWER'}
                </button>
              ) : !isLastQuestion ? (
                <button
                  onClick={handleNext}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-lg font-mono text-xs font-bold uppercase tracking-wider bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200 transition-all cursor-pointer"
                >
                  NEXT QUESTION
                  <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={handleFinish}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-lg font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-cyber-copper to-cyber-cyan text-slate-950 hover:shadow-glow-copper/20 transition-all cursor-pointer"
                >
                  FINISH INTERVIEW
                  <Award className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right 1 Col: Explanations terminal (only shown once answered) */}
        <div className="lg:col-span-1">
          {isAnswered ? (
            <div className="glass-panel p-5 border-slate-800/80 bg-slate-950/60 flex flex-col h-full overflow-hidden select-text">
              {/* Terminal header */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                </div>
                <span className="font-mono text-[9px] text-slate-500 tracking-wider font-bold">PHYSICS_EXPLANATION.LOG</span>
              </div>

              <div className="space-y-4 overflow-y-auto max-h-[460px] custom-scrollbar pr-1">
                {/* Explanation */}
                <div>
                  <h4 className="text-xs font-bold font-sans text-cyber-copper flex items-center gap-1.5 uppercase tracking-wider">
                    <AlertCircle className="w-3.5 h-3.5" />
                    Correct Option: {answer.correct_option}
                  </h4>
                  <p className="text-xs text-slate-300 font-sans mt-1.5 leading-relaxed bg-slate-900/40 p-2.5 rounded border border-slate-900">
                    {answer.explanation}
                  </p>
                </div>

                {/* Advanced Physics / EE Reasoning */}
                <div>
                  <h4 className="text-xs font-bold font-sans text-cyber-cyan flex items-center gap-1.5 uppercase tracking-wider">
                    <Award className="w-3.5 h-3.5" />
                    Engineering Reasoning
                  </h4>
                  <p className="text-[11px] font-mono text-slate-400 mt-2 leading-relaxed bg-slate-900/70 p-3 rounded border border-slate-900/60 border-l-2 border-l-cyber-cyan">
                    {answer.engineering_reasoning}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-6 border-slate-900/80 bg-slate-950/20 text-center flex flex-col items-center justify-center min-h-[260px] h-full text-slate-500">
              <AlertCircle className="w-10 h-10 stroke-1 stroke-slate-700 animate-pulse mb-3" />
              <p className="text-xs font-mono max-w-[180px] mx-auto leading-relaxed">
                Submit an answer to activate the technical explanation trace logger.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default MCQScreen;
