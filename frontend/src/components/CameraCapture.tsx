import React, { useRef, useState, useEffect } from 'react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
}

const CameraCapture: React.FC<CameraCaptureProps> = ({ onCapture }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const capturedFileRef = useRef<File | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup: stop camera when component unmounts
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  // Effect to attach stream to video element when stream changes
  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream;
      
      const video = videoRef.current;
      
      const handleCanPlay = () => {
        video.play().catch(err => {
          console.error('Play error in canplay:', err);
        });
      };
      
      const handleLoadedMetadata = () => {
        video.play().catch(err => {
          console.error('Play error in loadedmetadata:', err);
        });
      };
      
      video.addEventListener('canplay', handleCanPlay);
      video.addEventListener('loadedmetadata', handleLoadedMetadata);
      
      // Try to play immediately
      video.play().catch(err => {
        console.error('Immediate play error:', err);
      });
      
      return () => {
        video.removeEventListener('canplay', handleCanPlay);
        video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      };
    }
  }, [stream]);

  const startCamera = async () => {
    try {
      setError(null);
      setIsStreaming(true);
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      
      setStream(mediaStream);
      
      // Use setTimeout to ensure DOM is ready
      setTimeout(() => {
        if (videoRef.current && mediaStream) {
          videoRef.current.srcObject = mediaStream;
          
          // Force play the video
          const playPromise = videoRef.current.play();
          
          if (playPromise !== undefined) {
            playPromise
              .then(() => {
                console.log('Video playing successfully');
              })
              .catch(err => {
                console.error('Error playing video:', err);
                // Try again after a short delay
                setTimeout(() => {
                  if (videoRef.current) {
                    videoRef.current.play().catch(e => {
                      console.error('Retry play failed:', e);
                      setError('Error starting video preview. Please try again.');
                    });
                  }
                }, 500);
              });
          }
          
          // Also handle loadedmetadata event
          videoRef.current.onloadedmetadata = () => {
            if (videoRef.current) {
              videoRef.current.play().catch(err => {
                console.error('Error playing on metadata load:', err);
              });
            }
          };
        }
      }, 100);
      
    } catch (err: any) {
      console.error('Error accessing camera:', err);
      setError(err.message || 'Unable to access camera. Please check permissions.');
      setIsStreaming(false);
      setStream(null);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsStreaming(false);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) {
      setError('Camera not ready. Please wait a moment and try again.');
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) {
      setError('Unable to capture photo. Please try again.');
      return;
    }

    // Check if video is ready
    if (video.readyState < video.HAVE_METADATA) {
      setError('Video not ready. Please wait a moment.');
      return;
    }

    try {
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob and create File
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
          const imageUrl = URL.createObjectURL(blob);
          setCapturedImage(imageUrl);
          capturedFileRef.current = file; // Store file for later use
          stopCamera();
          // Don't automatically send - wait for user confirmation
        } else {
          setError('Failed to capture photo. Please try again.');
        }
      }, 'image/jpeg', 0.9);
    } catch (err) {
      console.error('Error capturing photo:', err);
      setError('Error capturing photo. Please try again.');
    }
  };

  const confirmAndVerify = () => {
    if (capturedFileRef.current) {
      onCapture(capturedFileRef.current);
      capturedFileRef.current = null;
    }
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    startCamera();
  };

  if (capturedImage) {
    return (
      <div className="w-full space-y-4">
        <div className="relative w-full rounded-2xl overflow-hidden border-2 border-cyan-500/50">
          <img 
            src={capturedImage} 
            alt="Captured" 
            className="w-full h-auto"
          />
        </div>
        <div className="text-center text-slate-400 text-sm mb-2">
          <i className="fas fa-check-circle text-cyan-500 mr-2"></i>
          Photo captured! Review and verify
        </div>
        <div className="flex gap-3">
          <button
            onClick={retakePhoto}
            className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-600 transition-colors"
          >
            <i className="fas fa-redo mr-2"></i>Retake
          </button>
          <button
            onClick={confirmAndVerify}
            className="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors font-medium"
          >
            <i className="fas fa-shield-alt mr-2"></i>Verify This Photo
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {error && (
        <div className="p-4 bg-red-950/30 border border-red-500/50 rounded-xl text-red-200 text-sm">
          {error}
        </div>
      )}

      {!isStreaming ? (
        <button
          onClick={startCamera}
          className="w-full py-4 px-6 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-600 transition-all flex items-center justify-center space-x-3"
        >
          <i className="fas fa-camera text-2xl"></i>
          <span className="font-medium">Start Camera</span>
        </button>
      ) : (
        <div className="space-y-4">
          <div className="relative w-full rounded-2xl overflow-hidden border-2 border-cyan-500/50 bg-black" style={{ minHeight: '300px' }}>
            {!stream ? (
              <div className="flex items-center justify-center h-64 text-slate-400">
                <div className="text-center">
                  <i className="fas fa-spinner fa-spin text-3xl mb-2"></i>
                  <p>Starting camera...</p>
                </div>
              </div>
            ) : (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-auto max-h-[500px]"
                style={{ 
                  display: 'block',
                  objectFit: 'contain',
                  backgroundColor: '#000',
                  width: '100%',
                  height: 'auto'
                }}
              />
            )}
            <canvas ref={canvasRef} className="hidden" />
          </div>
          {stream && (
            <div className="flex gap-3">
              <button
                onClick={stopCamera}
                className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-600 transition-colors"
              >
                <i className="fas fa-stop mr-2"></i>Stop Camera
              </button>
              <button
                onClick={capturePhoto}
                className="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors font-medium"
              >
                <i className="fas fa-camera mr-2"></i>Capture Photo
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CameraCapture;

