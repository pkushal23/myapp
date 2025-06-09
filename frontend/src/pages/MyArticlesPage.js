// frontend/src/pages/MyArticlesPage.js
import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, CircularProgress, Alert } from '@mui/material';
import axios from 'axios';

function MyArticlesPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchArticles = async () => {
      setLoading(true);
      try {
        const response = await axios.get('http://localhost:8000/api/articles/');
        setArticles(response.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load articles');
      } finally {
        setLoading(false);
      }
    };

    fetchArticles(); // Always fetch without checking token
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Your Saved Articles</Typography>
      {articles.length === 0 ? (
        <Typography>No articles found.</Typography>
      ) : (
        articles.map((article, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6">{article.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {article.source} — {new Date(article.published_date).toLocaleString()}
              </Typography>
              <Typography>{article.summary}</Typography>
              <a href={article.url} target="_blank" rel="noopener noreferrer">Read more</a>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
}

export default MyArticlesPage;
