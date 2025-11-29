import React, { useState, useRef } from 'react';
import { AnalysisState } from './types';
import { verifyFlyer } from './services/apiService';
import AnalysisStatus from './components/AnalysisStatus';
import ReportDashboard from './components/ReportDashboard';
import CameraCapture from './components/CameraCapture';

const App: React.FC = () => {
  const [state, setState] = useState<AnalysisState>({
    status: 'idle',
    progressStep: '',
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedTab, setSelectedTab] = useState<'camera' | 'upload'>('upload');

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    await processImage(file);
  };

  const handleCameraCapture = async (file: File) => {
    await processImage(file);
  };

  const processImage = async (file: File) => {
    // Reset state
    setState({
      status: 'analyzing',
      progressStep: 'Initializing Vision Module...',
      imagePreview: URL.createObjectURL(file)
    });

    try {
      // Update progress
      setState(prev => ({ ...prev, progressStep: 'Processing Image Data...' }));
      
      // Update progress
      setState(prev => ({ ...prev, progressStep: 'Scanning for Entities & Searching Database...' }));
      
      // Call our FastAPI backend
      const result = await verifyFlyer(file);

      // Complete
      setState(prev => ({
        status: 'complete',
        progressStep: 'Analysis Complete',
        result: result,
        imagePreview: prev.imagePreview
      }));

    } catch (error: any) {
      console.error(error);
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error.message || 'An unexpected error occurred during analysis.'
      }));
    }
  };

  const handleReset = () => {
    setState({ status: 'idle', progressStep: '' });
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="min-h-screen bg-[url('https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center bg-fixed bg-no-repeat relative">
      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-sm z-0"></div>

      <div className="relative z-10 container mx-auto px-4 py-8 flex flex-col min-h-screen">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row items-center justify-between mb-12 border-b border-slate-800 pb-8 pt-4">
          <div className="flex items-center gap-5">
             {/* Custom Shield Logo */}
             <div className="relative w-16 h-16 flex items-center justify-center shrink-0">
               <div className="absolute inset-0 bg-cyan-500/10 blur-xl rounded-full"></div>
               <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-[0_0_15px_rgba(34,211,238,0.6)]" fill="none" xmlns="http://www.w3.org/2000/svg">
                  {/* Outer Shield */}
                  <path d="M50 5L90 25V50C90 75 50 95 50 95C50 95 10 75 10 50V25L50 5Z" stroke="#22d3ee" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
                  {/* Inner Tech Details */}
                  <path d="M50 15V35" stroke="#22d3ee" strokeWidth="1" strokeOpacity="0.5" />
                  <path d="M50 95V65" stroke="#22d3ee" strokeWidth="1" strokeOpacity="0.5" />
                  <path d="M10 50H25" stroke="#22d3ee" strokeWidth="1" strokeOpacity="0.5" />
                  <path d="M90 50H75" stroke="#22d3ee" strokeWidth="1" strokeOpacity="0.5" />
                  {/* Central Star */}
                  <path d="M50 25L55 45L75 50L55 55L50 75L45 55L25 50L45 45L50 25Z" fill="#22d3ee" className="animate-pulse" />
               </svg>
             </div>
             
             <div className="flex flex-col justify-center">
               <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white leading-none bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                 AstraShield
               </h1>
               <p className="text-xl md:text-2xl text-cyan-400 font-medium tracking-wide mt-1 drop-shadow-md">
                 Truth that Protects.
               </p>
             </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-grow flex flex-col items-center justify-start">
          
          {state.status === 'idle' && (
            <div className="w-full max-w-2xl text-center space-y-8 animate-fade-in mt-8">
              <div className="space-y-4">
                <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight">
                  Verify Relief Efforts <br/>
                  <span className="text-cyan-400">Instantly</span>
                </h2>
                <p className="text-lg text-slate-400 max-w-lg mx-auto leading-relaxed">
                  Capture or upload a photo of a flyer, QR code, or social media post. Our AI agents will investigate organizations, phone numbers, and domains to detect scams.
                </p>
              </div>

              {/* Tab Selection */}
              <div className="flex gap-2 justify-center mb-4">
                <button
                  onClick={() => setSelectedTab('camera')}
                  className={`px-6 py-3 rounded-xl transition-all ${
                    selectedTab === 'camera'
                      ? 'bg-cyan-600 text-white border-2 border-cyan-500'
                      : 'bg-slate-800 text-slate-300 border-2 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <i className="fas fa-camera mr-2"></i>Camera
                </button>
                <button
                  onClick={() => setSelectedTab('upload')}
                  className={`px-6 py-3 rounded-xl transition-all ${
                    selectedTab === 'upload'
                      ? 'bg-cyan-600 text-white border-2 border-cyan-500'
                      : 'bg-slate-800 text-slate-300 border-2 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <i className="fas fa-upload mr-2"></i>Upload
                </button>
              </div>

              {/* Camera or Upload Section */}
              {selectedTab === 'camera' ? (
                <div className="w-full">
                  <CameraCapture onCapture={handleCameraCapture} />
                </div>
              ) : (
                <div 
                  className="group relative w-full h-64 border-2 border-dashed border-slate-700 rounded-2xl hover:border-cyan-500/50 hover:bg-slate-900/40 transition-all cursor-pointer flex flex-col items-center justify-center"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-xl shadow-black/50 border border-slate-800 group-hover:border-cyan-500/50">
                    <i className="fas fa-upload text-3xl text-slate-300 group-hover:text-cyan-400"></i>
                  </div>
                  <p className="text-slate-300 font-medium text-lg">Click to Upload Flyer Image</p>
                  <p className="text-sm text-slate-500 mt-2">Supports JPG, PNG, WEBP</p>
                  
                  <input 
                    type="file" 
                    ref={fileInputRef}
                    className="hidden" 
                    accept="image/*"
                    onChange={handleFileSelect}
                  />
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 text-left max-w-lg mx-auto">
                <div className="p-3 rounded bg-slate-900/50 border border-slate-800">
                   <div className="text-cyan-500 mb-1"><i className="fas fa-search-dollar"></i></div>
                   <div className="text-xs font-bold text-slate-300">Scam Check</div>
                </div>
                <div className="p-3 rounded bg-slate-900/50 border border-slate-800">
                   <div className="text-cyan-500 mb-1"><i className="fas fa-globe"></i></div>
                   <div className="text-xs font-bold text-slate-300">Domain Age</div>
                </div>
                <div className="p-3 rounded bg-slate-900/50 border border-slate-800">
                   <div className="text-cyan-500 mb-1"><i className="fas fa-building-ngo"></i></div>
                   <div className="text-xs font-bold text-slate-300">NGO Registry</div>
                </div>
              </div>
            </div>
          )}

          {state.status === 'analyzing' && (
             <AnalysisStatus status={state.status} step={state.progressStep} />
          )}

          {state.status === 'error' && (
            <div className="max-w-xl w-full p-6 bg-red-950/30 border border-red-500/50 rounded-xl text-center space-y-4">
              <div className="text-red-500 text-3xl"><i className="fas fa-exclamation-triangle"></i></div>
              <h3 className="text-xl font-bold text-white">Verification Failed</h3>
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

        </main>
      </div>
    </div>
  );
};

export default App;

