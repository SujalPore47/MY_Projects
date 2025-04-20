import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, IconButton, Box } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import './Header.css';

function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu when navigating
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location]);

  const isActive = (path) => location.pathname === path ? 'active-link' : '';

  return (
    <>
      <AppBar className={`header ${scrolled ? 'header-scrolled' : ''}`}>
        <Toolbar className="toolbar">
          {/* Logo and title */}
          <Link to="/" className="logo-container">
            <img
              src="/logo.png"
              alt="Food Nutrition Logo"
              className="logo-image"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 24 24'%3E%3Cpath fill='%234CAF50' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z'/%3E%3C/svg%3E";
              }}
            />
            <Typography variant="h6" className="logo-text">
              Food Nutrition Analyzer
            </Typography>
          </Link>

          {/* Desktop navigation */}
          <Box className="nav-links">
            <Button color="inherit" component={Link} to="/" className={`nav-button ${isActive('/')}`}>
              Home
            </Button>
            <Button color="inherit" component={Link} to="/upload" className={`nav-button ${isActive('/upload')}`}>
              Upload
            </Button>
            <Button color="inherit" component={Link} to="/webcam" className={`nav-button ${isActive('/webcam')}`}>
              Webcam
            </Button>
            <Button color="inherit" component={Link} to="/chat" className={`nav-button ${isActive('/chat')}`}>
              Chat
            </Button>  {/* <— new */}
          </Box>

          {/* Mobile menu button */}
          <IconButton
            className="mobile-menu-button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            size="large"
          >
            {mobileMenuOpen ? <CloseIcon /> : <MenuIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Mobile menu */}
      <div className={`mobile-menu ${mobileMenuOpen ? 'mobile-menu-active' : ''}`}>
        <Link to="/" className={`mobile-menu-link ${isActive('/')}`}>
          Home
        </Link>
        <Link to="/upload" className={`mobile-menu-link ${isActive('/upload')}`}>
          Upload Image
        </Link>
        <Link to="/webcam" className={`mobile-menu-link ${isActive('/webcam')}`}>
          Use Webcam
        </Link>
        <Link to="/chat" className={`mobile-menu-link ${isActive('/chat')}`}>
          Chat
        </Link>  {/* <— new */}
      </div>

      {/* Spacer to prevent content from hiding behind the header */}
      <Toolbar />
    </>
  );
}

export default Header;
