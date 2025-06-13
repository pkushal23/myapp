// frontend/src/pages/DashboardPage.js (updated)
import React, { useState, useEffect } from 'react';
import { Box, Typography, Checkbox, FormControlLabel, Button, Alert } from '@mui/material';
import axios from 'axios';

function DashboardPage() {
  const [availableInterests, setAvailableInterests] = useState([]);
  const [selectedInterestIds, setSelectedInterestIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('user_id'); // If you stored this

  useEffect(() => {
    if (!token) {
      // Handle unauthenticated user (e.g., redirect to login)
     return;
     }

    const fetchInterests = async () => {
      setLoading(true);
      setError('');
      try {
        // Fetch all available interests
        const allInterestsResponse = await axios.get('http://localhost:8000/api/interests/', {
  headers: { Authorization: `Token ${token}` }
});

        setAvailableInterests(allInterestsResponse.data);

        // Fetch user's current interests
       const userInterestsResponse = await axios.get('http://localhost:8000/api/user-interests/', {
  headers: { Authorization: `Token ${token}` }
});

        const currentUserInterestIds = new Set(userInterestsResponse.data.map(ui => ui.interest.id));
        setSelectedInterestIds(currentUserInterestIds);

      } catch (err) {
        console.error('Error fetching interests:', err);
        setError('Failed to load interests. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchInterests();
  }, [token]);

  const handleInterestChange = (interestId, isChecked) => {
    setSelectedInterestIds(prev => {
      const newSet = new Set(prev);
      if (isChecked) {
        newSet.add(interestId);
      } else {
        newSet.delete(interestId);
      }
      return newSet;
    });
  };

  const handleSaveInterests = async () => {
    setError('');
    setMessage('');
    const currentServerInterestIds = new Set((await axios.get('http://localhost:8000/api/user-interests/', { headers: { Authorization: `Token ${token}` } })).data.map(ui => ui.interest.id));

    const addInterests = availableInterests
      .filter(interest => selectedInterestIds.has(interest.id) && !currentServerInterestIds.has(interest.id))
      .map(interest => interest.id);

    const removeInterests = availableInterests
      .filter(interest => !selectedInterestIds.has(interest.id) && currentServerInterestIds.has(interest.id))
      .map(interest => interest.id);

    try {
      const response = await axios.post(
  'http://localhost:8000/api/user-interests/',
  { add_interests: addInterests, remove_interests: removeInterests },
  { headers: { Authorization: `Token ${token}` } }
);
      setMessage(response.data.message);
      // Re-sync selected interests from the backend's response if necessary
      const updatedUserInterestIds = new Set(response.data.current_interests.map(ui => ui.interest.id));
      setSelectedInterestIds(updatedUserInterestIds);

    } catch (err) {
      console.error('Error saving interests:', err.response ? err.response.data : err.message);
      setError('Failed to save interests.');
    }
  };

  if (loading) {
    return <Typography>Loading interests...</Typography>;
  }

  return (
    <Box sx={{ mt: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom>Your Dashboard</Typography>
      <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 4 }}>Manage Your Interests</Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}

      <Box>
        {availableInterests.map(interest => (
          <FormControlLabel
            key={interest.id}
            control={
              <Checkbox
                checked={selectedInterestIds.has(interest.id)}
                onChange={(e) => handleInterestChange(interest.id, e.target.checked)}
              />
            }
            label={interest.name}
          />
        ))}
      </Box>
      <Button variant="contained" sx={{ mt: 2 }} onClick={handleSaveInterests}>
        Save Interests
      </Button>

      <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 4 }}>Your Latest Newsletter (Coming Soon!)</Typography>
      {/* Placeholder for newsletter display */}
      <Typography>Your personalized newsletter will appear here once generated.</Typography>
    </Box>
  );
}

export default DashboardPage;