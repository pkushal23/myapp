// frontend/src/pages/LoginPage.js (updated)
import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const handleSubmit = async (event) => {
        event.preventDefault();
        setError(''); // Clear previous errors
    try {
        const response = await axios.post('http://localhost:8000/api/auth/login/', {
            username,
            password,
        });
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user_id', response.data.user_id); // Store user ID for future use
    console.log('Login successful:', response.data);
    navigate('/dashboard'); // Redirect to dashboard
    } catch (err) {
        console.error('Login error:', err.response ? err.response.data : err.message);
        setError('Login failed. Please check your username and password.');
        }
    };
    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3, maxWidth: 400, mx: 'auto' }}>
          <Typography variant="h4" component="h1" gutterBottom>Login</Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Sign In
          </Button>
        </Box>
      );
    };

export default LoginPage;
