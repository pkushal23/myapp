// frontend/src/pages/RegisterPage.js
import React, { useState } from 'react';
import { TextField, Button, Typography, Alert, Box } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    setError('');
    setMessage('');
    try {
      const response = await axios.post('http://localhost:8000/api/auth/register/', {
        username,
        password,
        email
      });
      console.log(response);
      setMessage('Registration successful! You can now login.');
      setUsername('');
      setPassword('');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    }
  };

  return (
    <Box sx={{ mt: 4, maxWidth: 400, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>Register</Typography>

      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TextField
        label="Username"
        fullWidth
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        sx={{ mb: 2 }}
      />
      <TextField
  label="Email"
  fullWidth
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  sx={{ mb: 2 }}
/>

      <TextField
        label="Password"
        type="password"
        fullWidth
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        sx={{ mb: 2 }}
      />
      <Button variant="contained" onClick={handleRegister} fullWidth>
        Register
      </Button>
    </Box>
  );
}

export default RegisterPage;
