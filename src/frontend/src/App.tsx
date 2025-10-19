import { Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import CampaignListPage from './pages/CampaignListPage';
import CampaignDetailsPage from './pages/CampaignDetailsPage';
import HomePage from './pages/HomePage';

function App() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/campaigns" element={<CampaignListPage />} />
          <Route path="/campaigns/:campaignId" element={<CampaignDetailsPage />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;
