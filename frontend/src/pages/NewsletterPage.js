// frontend/src/pages/NewsletterPage.js (example)
import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Link as MuiLink } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

function NewsletterPage() {
  const [newsletters, setNewsletters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      navigate('/login'); // Redirect if not authenticated
      return;
    }

    const fetchNewsletters = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await axios.get('http://localhost:8000/api/user-newsletters/', {
          headers: { Authorization: `Token ${token}` }
        });
        setNewsletters(response.data);
      } catch (err) {
        console.error('Error fetching newsletters:', err.response ? err.response.data : err.message);
        setError('Failed to load newsletters. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchNewsletters();
  }, [token, navigate]);

  if (loading) return <Typography>Loading newsletters...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;
  if (newsletters.length === 0) return <Typography>No newsletters generated yet.</Typography>;

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>Your Newsletters</Typography>
      {newsletters.map((nl) => (
        <Card key={nl.id} sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Newsletter - {new Date(nl.generation_date).toLocaleDateString()}
            </Typography>
            <ReactMarkdown sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', mb: 2 }}>
              {nl.content}
            </ReactMarkdown>
            {nl.articles_included && nl.articles_included.length > 0 && (
  <Box>
    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
      Articles Included:
    </Typography>
    <ul>
      {nl.articles_included.map((article) => (
        <li key={article.id}>
          <MuiLink href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </MuiLink>
        </li>
      ))}
    </ul>
  </Box>
)}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}

export default NewsletterPage;