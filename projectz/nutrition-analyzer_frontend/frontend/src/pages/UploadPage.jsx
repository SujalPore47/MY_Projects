import React, { useState } from 'react';
import { Container, Button, Input, Typography, Paper, Box, CircularProgress } from '@mui/material';
import { analyzeImage } from '../utils/api';
import { validateImageFile } from '../utils/fileValidation.js';
import NutritionResult from '../components/NutritionResult';
import './UploadPage.css';

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    const validationError = validateImageFile(file);
    if (validationError) {
      setError(validationError);
      setSelectedFile(null);
      setPreviewUrl(null);
    } else {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select an image file.');
      return;
    }

    setLoading(true);
    try {
      const data = await analyzeImage(selectedFile);
      setResult(data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      {/* Background shapes from Home.css will apply if you're using the same styles */}
      
      <Paper className="upload-card" elevation={3}>
        <Typography variant="h5" className="upload-title">
          Upload Food Image
        </Typography>
        
        <Typography variant="body1" className="upload-subtitle">
          Upload a clear image of your food to analyze its nutritional content
        </Typography>
        
        {error && (
          <div className="error-container">
            <Typography variant="body2">{error}</Typography>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="upload-form">
          <label className="file-input-container">
            <Input
              type="file"
              onChange={handleFileChange}
              inputProps={{ accept: 'image/*' }}
              disableUnderline
            />
            <div className="upload-icon">📷</div>
            <Typography variant="body1" className="file-input-text">
              Click or drag an image here
            </Typography>
            <Typography variant="body2" className="file-input-text" style={{ opacity: 0.7 }}>
              Supports JPG, PNG, WEBP (max 10MB)
            </Typography>
          </label>
          
          {previewUrl && (
            <div className="image-preview-container">
              <img src={previewUrl} alt="Food preview" />
            </div>
          )}
          
          <Button 
            type="submit"
            variant="contained"
            className="analyze-button"
            disabled={!selectedFile || loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Analyze Food'}
          </Button>
        </form>
      </Paper>
      
      {loading ? (
        <div className="loading-container">
          <CircularProgress className="loading-spinner" size={60} />
          <Typography variant="h6" className="loading-text">
            Analyzing your food...
          </Typography>
        </div>
      ) : result && (
        <Paper className="results-card" elevation={3}>
          <NutritionResult result={result} />
        </Paper>
      )}
    </div>
  );
}

export default UploadPage;