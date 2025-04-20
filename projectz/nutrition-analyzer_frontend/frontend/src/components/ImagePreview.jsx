// src/components/ImagePreview.jsx
import React, { useEffect, useState } from 'react';
import { Box } from '@mui/material';

function ImagePreview({ file }) {
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url); // Clean up memory
    }
  }, [file]);

  if (!previewUrl) return null;

  return (
    <Box sx={{ mt: 2 }}>
      <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%', borderRadius: '4px' }} />
    </Box>
  );
}

export default ImagePreview;