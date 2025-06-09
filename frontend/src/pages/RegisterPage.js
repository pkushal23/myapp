// frontend/src/pages/LoginPage.js
import React from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';

function RegisterPage() {
  const handleSubmit = (event) => {
    event.preventDefault();
    // Implement login logic here later
    console.log('Login attempt');
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3, maxWidth: 400, mx: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom>Login</Typography>
      <TextField
        margin="normal"
        required
        fullWidth
        id="username"
        label="Username"
        name="username"
        autoComplete="username"
        autoFocus
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
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Register
      </Button>
    </Box>
  );
}

export default RegisterPage;