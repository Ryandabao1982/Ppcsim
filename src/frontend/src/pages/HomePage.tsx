import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Campaign as CampaignIcon } from '@mui/icons-material';

function HomePage() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '70vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h1" gutterBottom color="primary">
          Amazon PPC Simulator
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Train to become a proficient Amazon PPC manager in a risk-free environment
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<CampaignIcon />}
            onClick={() => navigate('/campaigns')}
            sx={{ px: 4, py: 1.5 }}
          >
            View Campaigns
          </Button>
        </Box>
        <Box sx={{ mt: 8 }}>
          <Typography variant="body1" color="text.secondary">
            ✓ Practice without budget risk • ✓ Realistic simulations • ✓ Learn optimization strategies
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}

export default HomePage;
