// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import MyArticlesPage from './pages/MyArticlesPage';
import { Container, AppBar, Toolbar, Typography, Button } from '@mui/material';

function App() {
  return (
    <Router>
      <Header /> {/* Move Header to a separate component so we can use useNavigate */}
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/my-articles" element={<MyArticlesPage />} />
          <Route path="/" element={<DashboardPage />} /> {/* Default route */}
        </Routes>
      </Container>
    </Router>
  );
}

// Separate Header component to use hooks like useNavigate
function Header() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear token and user_id from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    console.log('User logged out');

    // Redirect to login page
    navigate('/login');
  };

  // Optionally, show Logout button only if token exists
  const isLoggedIn = !!localStorage.getItem('token');

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AI Newsletter Agent
        </Typography>
        <Button color="inherit" component={Link} to="/login">Login</Button>
        <Button color="inherit" component={Link} to="/register">Register</Button>
        <Button color="inherit" component={Link} to="/dashboard">Dashboard</Button>
        <Button color="inherit" component={Link} to="/my-articles">My Articles</Button>

        {isLoggedIn && (
          <Button color="inherit" onClick={handleLogout}>Logout</Button>
        )}
      </Toolbar>
    </AppBar>
  );
}

export default App;
