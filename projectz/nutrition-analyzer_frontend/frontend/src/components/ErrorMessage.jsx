// src/components/ErrorMessage.jsx
import React from 'react';
import { Alert } from '@mui/material';

function ErrorMessage({ error }) {
  return error ? <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert> : null;
}

export default ErrorMessage;
