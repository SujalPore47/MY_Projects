import React, { useState, useRef, useEffect, useCallback } from 'react';
import {Button,Typography } from '@mui/material';
import { analyzeImage } from '../utils/api';
import NutritionResult from '../components/NutritionResult';
import ImagePreview from '../components/ImagePreview';
import './WebcamPage.css';

function WebcamPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [captured, setCaptured] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isStartingCamera, setIsStartingCamera] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  // --- Camera Control Functions ---

  const startCamera = useCallback(async () => {
    if (isCameraActive || captured || streamRef.current || isStartingCamera) {
        console.log('Start camera called but conditions not met:', {isCameraActive, captured, streamRefCurrent: !!streamRef.current, isStartingCamera});
        return;
    }

    setError(null);
    setIsStartingCamera(true);
    console.log('Attempting to start camera...');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;

      if (videoRef.current) {
        console.log('Video ref exists. Setting srcObject.');
        videoRef.current.srcObject = stream;

        await new Promise((resolve, reject) => {
            if (!videoRef.current) {
                reject(new Error("Video ref became null"));
                return;
            }
            videoRef.current.onloadedmetadata = () => {
                console.log('Video metadata loaded.');
                resolve();
            };
            setTimeout(() => reject(new Error("Video metadata load timed out")), 5000);
        });

        if (!streamRef.current) {
            throw new Error("Stream was stopped before metadata loaded.");
        }

        setIsCameraActive(true);
        console.log('Camera started successfully and marked active.');
      } else {
        console.error("Video ref was null when trying to set srcObject.");
        throw new Error("Camera setup failed: video element not available.");
      }
    } catch (err) {
      console.error("Camera Start Error:", err);
      setError(`Unable to access camera. Please ensure permissions are granted. Error: ${err.name} - ${err.message}`);
      if (streamRef.current) {
         streamRef.current.getTracks().forEach((track) => track.stop());
         streamRef.current = null;
      }
      setIsCameraActive(false);
    } finally {
       setIsStartingCamera(false);
    }
  }, [isCameraActive, captured, isStartingCamera]);

  const stopCamera = useCallback(() => {
    console.log('Stopping camera...');
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      console.log('Camera stream stopped.');
    }
    if (videoRef.current) {
        videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  }, []);

  // --- Effect for Cleanup ---

  useEffect(() => {
    return () => {
      console.log("Component unmounting, stopping camera.");
      stopCamera();
    };
  }, [stopCamera]);

  // --- Action Handlers ---

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current && isCameraActive && streamRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      if (canvas.width === 0 || canvas.height === 0) {
        console.error("Capture failed: Video dimensions are zero.");
        setError("Cannot capture: Video feed not ready or invalid dimensions.");
        return;
      }

      const ctx = canvas.getContext('2d');
      if (!ctx) {
          setError("Could not get canvas context.");
          return;
      }
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'capture.jpg', { type: blob.type });
          setSelectedFile(file);
          setCaptured(true);
          stopCamera();
          console.log('Photo captured.');
        } else {
          setError("Could not create blob from canvas.");
        }
      }, 'image/jpeg');
    } else {
        console.warn('Capture failed: Conditions not met.', { video: !!videoRef.current, canvas: !!canvasRef.current, isCameraActive, stream: !!streamRef.current });
        setError("Cannot capture photo. Camera might not be active or ready.");
    }
  };

  const handleRetake = () => {
    console.log('Retaking photo...');
    setSelectedFile(null);
    setCaptured(false);
    setResult(null);
    setError(null);
    setLoading(false);
    stopCamera();
    setTimeout(() => {
        startCamera();
    }, 50);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please capture an image first.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      console.log('Analyzing image...');
      const data = await analyzeImage(selectedFile);
      setResult(data);
      console.log('Analysis successful.');
    } catch (err) {
      console.error("Analysis Error:", err);
      setError(err.message || 'Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  // --- Rendering ---

  return (
    <div className="webcam-container">
      <Typography variant="h5" className="page-title">
        Food Snapshot Analysis
      </Typography>

      {/* Camera View Area */}
      <div className="camera-container">
        {(isStartingCamera || isCameraActive) && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="webcam-video"
          />
        )}
        
        <div className="webcam-overlay"></div>
        
        {/* Camera Status Indicator */}
        {(isStartingCamera || isCameraActive) && (
          <div className="camera-status">
            <div className={`status-indicator ${isCameraActive ? 'active' : ''}`}></div>
            {isStartingCamera ? 'Connecting...' : 'Live'}
          </div>
        )}
        
        {/* Loading Spinner for Camera Start */}
        {isStartingCamera && !isCameraActive && (
          <div className="spinner-container">
            <div className="spinner"></div>
          </div>
        )}
        
        {/* Camera Off Message */}
        {!isStartingCamera && !isCameraActive && !captured && (
          <div className="spinner-container">
            <Typography color="textSecondary">Camera is off</Typography>
          </div>
        )}
        
        {/* Hidden Canvas */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>

      {/* Control Buttons */}
      <div className="controls-container">
        {/* Camera Start/Stop Controls */}
        {!captured && (
          <>
            {!isCameraActive && (
              <Button
                variant="contained"
                className="control-button start-button"
                onClick={startCamera}
                disabled={isStartingCamera}
                aria-label="Start Camera"
              >
                {isStartingCamera ? 'Starting...' : 'Start Camera'}
              </Button>
            )}
            {isCameraActive && (
              <Button 
                variant="contained" 
                className="control-button stop-button"
                onClick={stopCamera} 
                aria-label="Stop Camera"
              >
                Stop Camera
              </Button>
            )}
          </>
        )}

        {/* Capture Button */}
        {!captured && isCameraActive && (
          <Button
            variant="contained"
            className="control-button capture-button"
            onClick={capturePhoto}
            aria-label="Capture photo"
          >
            Capture
          </Button>
        )}

        {/* Image Action Controls */}
        {captured && (
          <>
            <Button
              variant="contained"
              className="control-button analyze-button"
              onClick={handleSubmit}
              disabled={loading || !selectedFile}
              aria-label="Analyze food"
            >
              {loading ? 'Analyzing...' : 'Analyze Food'}
            </Button>
            <Button 
              variant="outlined" 
              className="control-button retake-button"
              onClick={handleRetake} 
              aria-label="Retake photo" 
              disabled={loading}
            >
              Retake Photo
            </Button>
          </>
        )}
      </div>

      {/* Image Preview */}
      {captured && (
        <div className="preview-container">
          <ImagePreview file={selectedFile} />
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Loading Spinner */}
      {loading && (
        <div className="spinner-container">
          <div className="spinner"></div>
          <Typography variant="body1" className="analyzing-text" sx={{ ml: 2 }}>
            Analyzing
          </Typography>
        </div>
      )}

      {/* Nutrition Result */}
      {result && <NutritionResult result={result} />}
    </div>
  );
}

export default WebcamPage;