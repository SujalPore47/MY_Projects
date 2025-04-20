import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

// Lazy load pages
const Home = lazy(() => import('./pages/Home'));
const UploadPage = lazy(() => import('./pages/UploadPage'));
const WebcamPage = lazy(() => import('./pages/WebcamPage'));
const ChatPage = lazy(() => import('./pages/ChatPage'));  // <— new

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/webcam" element={<WebcamPage />} />
            <Route path="/chat" element={<ChatPage />} />   {/* <— new */}
          </Routes>
        </Suspense>
      </div>
    </Router>
  );
}

export default App;
