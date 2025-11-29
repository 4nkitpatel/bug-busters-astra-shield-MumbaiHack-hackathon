import React, { useState, useRef } from 'react';
import { AnalysisState, VerificationResult } from './types';
import {
  analyzeFlyer,
  fileToGenerativePart,
  verifyTextClaim,
} from './services/geminiService';
import AnalysisStatus from './components/AnalysisStatus';
import ReportDashboard from './components/ReportDashboard';
import MonitoringDashboard from './components/MonitoringDashboard';

const App: React.FC = () => {
  const [state, setState] = useState<AnalysisState>({
    status: 'idle',
    progressStep: '',
  });

  const [activeMode, setActiveMode] = useState<'image' | 'text'>('image');
  const [textInput, setTextInput] = useState('');

  // New state to pass result to monitoring feed
  const [lastResult, setLastResult] = useState<VerificationResult | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Reset state
    setState({
      status: 'analyzing',
      progressStep: 'Initializing Vision Module...',
      imagePreview: URL.createObjectURL(file),
    });

    try {
      // 1. Convert image
      setState((prev) => ({
        ...prev,
        progressStep: 'Processing Image Data...',
      }));
      const base64Data = await fileToGenerativePart(file);

      // 2. Send to Gemini
      setState((prev) => ({
        ...prev,
        progressStep: 'Scanning for Entities & Searching Database...',
      }));
      const result = await analyzeFlyer(base64Data, file.type);

      // 3. Complete
      setState((prev) => ({
        status: 'complete',
        progressStep: 'Analysis Complete',
        result: result,
        imagePreview: prev.imagePreview,
      }));

      // Trigger feed update
      setLastResult(result);
    } catch (error: any) {
      console.error(error);
      setState((prev) => ({
        ...prev,
        status: 'error',
        error: error.message || 'An unexpected error occurred during analysis.',
      }));
    }
  };

  const handleTextSubmit = async () => {
    if (!textInput.trim()) return;

    setState({
      status: 'analyzing',
      progressStep: 'Initializing Text Analysis Module...',
    });

    try {
      setState((prev) => ({
        ...prev,
        progressStep: 'Cross-referencing with Global News Network...',
      }));
      const result = await verifyTextClaim(textInput);

      setState((prev) => ({
        status: 'complete',
        progressStep: 'Analysis Complete',
        result: result,
      }));

      setLastResult(result);
    } catch (error: any) {
      console.error(error);
      setState((prev) => ({
        ...prev,
        status: 'error',
        error: error.message || 'An unexpected error occurred during analysis.',
      }));
    }
  };

  const handleReset = () => {
    setState({ status: 'idle', progressStep: '' });
    setTextInput('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="min-h-screen bg-[url('https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-fixed bg-no-repeat relative">
      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-sm z-0"></div>

      <div className="relative z-10 container mx-auto px-4 py-4 flex flex-col min-h-screen">
        {/* Header */}
        <header className="flex flex-col md:flex-row items-center justify-between mb-1 border-b border-slate-800 pb-8 pt-4">
          <div
            className="flex items-center gap-6 cursor-pointer"
            onClick={handleReset}
          >
            {/* Custom AstraShield Logo */}
            <div className="relative w-16 h-16 flex items-center justify-center shrink-0">
              <div className="absolute inset-0 bg-cyan-500/10 blur-xl rounded-full"></div>
              <svg
                viewBox="0 0 100 100"
                className="w-full h-full drop-shadow-[0_0_15px_rgba(34,211,238,0.6)]"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                {/* Outer Shield */}
                <path
                  d="M50 5L90 25V50C90 75 50 95 50 95C50 95 10 75 10 50V25L50 5Z"
                  stroke="#22d3ee"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]"
                />
                {/* Inner Tech Details */}
                <path
                  d="M50 15V35"
                  stroke="#22d3ee"
                  strokeWidth="1"
                  strokeOpacity="0.5"
                />
                <path
                  d="M50 95V65"
                  stroke="#22d3ee"
                  strokeWidth="1"
                  strokeOpacity="0.5"
                />
                <path
                  d="M10 50H25"
                  stroke="#22d3ee"
                  strokeWidth="1"
                  strokeOpacity="0.5"
                />
                <path
                  d="M90 50H75"
                  stroke="#22d3ee"
                  strokeWidth="1"
                  strokeOpacity="0.5"
                />
                {/* Central Star (Astra) */}
                <path
                  d="M50 25L55 45L75 50L55 55L50 75L45 55L25 50L45 45L50 25Z"
                  fill="#22d3ee"
                  className="animate-pulse"
                />
              </svg>
            </div>

            <div className="flex flex-col justify-center">
              <h1 className="text-3xl md:text-3xl font-black tracking-tighter text-white leading-none bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                AstraShield
              </h1>
              <p className="text-1xl md:text-1xl text-cyan-400 font-medium tracking-wide mt-2 drop-shadow-md">
                Truth that Protects.
              </p>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-grow flex flex-col items-center justify-start w-full">
          {state.status === 'idle' && (
            <div className="w-full max-w-3xl text-center space-y-8 animate-fade-in mt-4 mb-12">
              <div className="space-y-4">
                <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight">
                  Verify Relief Efforts <br />
                  <span className="text-cyan-400">Instantly</span>
                </h2>
                <p className="text-lg text-slate-400 max-w-lg mx-auto leading-relaxed">
                  Analyze flyers, QR codes, or text claims to detect scams using
                  multimodal AI forensics.
                </p>
              </div>

              {/* Mode Switcher Chips */}
              <div className="flex justify-center mb-6">
                <div className="bg-slate-900 p-1 rounded-full border border-slate-700 flex space-x-1">
                  <button
                    onClick={() => setActiveMode('image')}
                    className={`px-6 py-2 rounded-full text-sm font-bold transition-all duration-300 flex items-center space-x-2 ${
                      activeMode === 'image'
                        ? 'bg-cyan-500 text-slate-950 shadow-[0_0_15px_rgba(34,211,238,0.5)]'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    <i className="fas fa-image"></i>
                    <span>Upload Image</span>
                  </button>
                  <button
                    onClick={() => setActiveMode('text')}
                    className={`px-6 py-2 rounded-full text-sm font-bold transition-all duration-300 flex items-center space-x-2 ${
                      activeMode === 'text'
                        ? 'bg-cyan-500 text-slate-950 shadow-[0_0_15px_rgba(34,211,238,0.5)]'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    <i className="fas fa-keyboard"></i>
                    <span>Verify Text</span>
                  </button>
                </div>
              </div>

              <div className="transition-all duration-500 ease-in-out">
                {activeMode === 'image' ? (
                  // Image Upload Mode
                  <div
                    className="group relative w-full h-64 border-2 border-dashed border-slate-700 rounded-2xl hover:border-cyan-500/50 hover:bg-slate-900/40 transition-all cursor-pointer flex flex-col items-center justify-center animate-fade-in"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-xl shadow-black/50 border border-slate-800 group-hover:border-cyan-500/50">
                      <i className="fas fa-camera text-3xl text-slate-300 group-hover:text-cyan-400"></i>
                    </div>
                    <p className="text-slate-300 font-medium text-lg">
                      Click to Upload Flyer Image
                    </p>
                    <p className="text-sm text-slate-500 mt-2">
                      Supports JPG, PNG, WEBP
                    </p>

                    <input
                      type="file"
                      ref={fileInputRef}
                      className="hidden"
                      accept="image/*"
                      onChange={handleFileSelect}
                    />
                  </div>
                ) : (
                  // Text Input Mode
                  <div className="w-full bg-slate-900/50 border border-slate-800 rounded-2xl p-6 shadow-xl animate-fade-in">
                    <div className="flex flex-col space-y-4">
                      <label className="text-left text-sm font-bold text-slate-400 uppercase tracking-wide">
                        <i className="fas fa-quote-left mr-2 text-cyan-500"></i>
                        Enter claim or headline
                      </label>
                      <div className="relative group">
                        <input
                          type="text"
                          className="w-full bg-slate-950 border border-slate-700 rounded-xl px-5 py-4 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all text-lg shadow-inner"
                          placeholder="e.g. 'Did the Eiffel tower catch fire yesterday?'"
                          value={textInput}
                          onChange={(e) => setTextInput(e.target.value)}
                          onKeyDown={(e) =>
                            e.key === 'Enter' && handleTextSubmit()
                          }
                        />
                        <button
                          onClick={handleTextSubmit}
                          className="absolute right-2 top-2 bottom-2 bg-blue-700 hover:bg-blue-600 text-white px-6 rounded-lg font-bold transition-all flex items-center space-x-2"
                        >
                          <span>Analyze</span>
                          <i className="fas fa-arrow-right"></i>
                        </button>
                      </div>
                      <p className="text-xs text-slate-500 text-left pl-1">
                        Veritas will cross-reference this with Google Grounding
                        to detect misinformation.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Status Indicators (Common) */}
              <div className="grid grid-cols-3 gap-4 text-left max-w-lg mx-auto mt-8">
                <div className="p-3 rounded bg-slate-900/50 border border-slate-800">
                  <div className="text-cyan-500 mb-1">
                    <i className="fas fa-search-dollar"></i>
                  </div>
                  <div className="text-xs font-bold text-slate-300">
                    Scam Check
                  </div>
                </div>
                <div className="p-3 rounded bg-slate-900/50 border border-slate-800">
                  <div className="text-cyan-500 mb-1">
                    <i className="fas fa-globe"></i>
                  </div>
                  <div className="text-xs font-bold text-slate-300">
                    Global Verification
                  </div>
                </div>
                <div className="p-3 rounded bg-slate-900/50 border border-slate-800">
                  <div className="text-cyan-500 mb-1">
                    <i className="fas fa-hand-holding-heart"></i>
                  </div>
                  <div className="text-xs font-bold text-slate-300">
                    NGO Registry
                  </div>
                </div>
              </div>
            </div>
          )}

          {state.status === 'analyzing' && (
            <AnalysisStatus status={state.status} step={state.progressStep} />
          )}

          {state.status === 'error' && (
            <div className="max-w-xl w-full p-6 bg-red-950/30 border border-red-500/50 rounded-xl text-center space-y-4 mb-12">
              <div className="text-red-500 text-3xl">
                <i className="fas fa-exclamation-triangle"></i>
              </div>
              <h3 className="text-xl font-bold text-white">
                Verification Failed
              </h3>
              <p className="text-red-200">{state.error}</p>
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-red-900/50 hover:bg-red-900 rounded border border-red-700 text-red-100 transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {state.status === 'complete' && state.result && (
            <ReportDashboard result={state.result} onReset={handleReset} />
          )}

          {/* Real-Time Monitoring Feed - Appended below main content */}
          {/* Work In Progress - 40% task is already done :) */}
          {/* <MonitoringDashboard userResult={lastResult} /> */}
        </main>
      </div>
    </div>
  );
};

export default App;
