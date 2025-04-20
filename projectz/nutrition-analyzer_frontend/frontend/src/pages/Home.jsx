// src/pages/Home.jsx
import React from 'react';
import { Container, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  return (
    <div className="home-container">
      {/* Background shapes */}
      <div className="background-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>
      
      {/* Food icons */}
      <div className="food-icon icon-1">🥗</div>
      <div className="food-icon icon-2">🍎</div>
      <div className="food-icon icon-3">🥑</div>
      
      {/* Logo */}
      <img 
        src="/logo.png" 
        alt="Food Nutrition Analyzer Logo" 
        className="logo"
        onError={(e) => {
          e.target.onerror = null;
          e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 24 24'%3E%3Cpath fill='%234CAF50' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z'/%3E%3C/svg%3E";
        }}
      />
      
      <Typography variant="h4" className="hero-title">
        Food Nutrition Analyzer
      </Typography>
      
      <Typography variant="body1" className="hero-subtitle">
        Instantly analyze the nutritional content of your meals using AI-powered image recognition. 
        Make healthier food choices with accurate, real-time nutrition information.
      </Typography>
      
      <div className="cta-container">
        <Button 
          variant="contained" 
          component={Link} 
          to="/upload"
          className="cta-button upload-button"
        >
          Upload Food Image
        </Button>
        
        <Button 
          variant="outlined" 
          component={Link} 
          to="/webcam"
          className="cta-button webcam-button"
        >
          Use Webcam
        </Button>
        
        <Button 
          variant="outlined" 
          component={Link} 
          to="/chat"
          className="cta-button chat-button"
        >
          Recipe Bot
        </Button>
      </div>
    </div>
  );
}

export default Home;
