import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { deleteKeyword } from '../store/slices/keywordSlice';
import KeywordFormDialog from './KeywordFormDialog';
import { MatchType } from '../types/keyword';

interface KeywordListProps {
  campaignId: number;
}

function KeywordList({ campaignId }: KeywordListProps) {
  const dispatch = useDispatch<AppDispatch>();
  const { keywords, loading, error } = useSelector((state: RootState) => state.keywords);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingKeywordId, setEditingKeywordId] = useState<number | null>(null);
  const [filterAdGroup, setFilterAdGroup] = useState<number | 'all'>('all');
  const [filterMatchType, setFilterMatchType] = useState<MatchType | 'all'>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const { adGroups } = useSelector((state: RootState) => state.adGroups);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this keyword?')) {
      await dispatch(deleteKeyword(id));
    }
  };

  const handleEdit = (id: number) => {
    setEditingKeywordId(id);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingKeywordId(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'PAUSED':
        return 'warning';
      case 'ARCHIVED':
        return 'default';
      default:
        return 'default';
    }
  };

  const getMatchTypeColor = (matchType: MatchType) => {
    switch (matchType) {
      case 'EXACT':
        return 'error';
      case 'PHRASE':
        return 'warning';
      case 'BROAD':
        return 'info';
      default:
        return 'default';
    }
  };

  // Filter keywords
  const filteredKeywords = keywords.filter((keyword) => {
    if (filterAdGroup !== 'all' && keyword.adGroupId !== filterAdGroup) return false;
    if (filterMatchType !== 'all' && keyword.matchType !== filterMatchType) return false;
    if (filterStatus !== 'all' && keyword.status !== filterStatus) return false;
    if (searchTerm && !keyword.keywordText.toLowerCase().includes(searchTerm.toLowerCase()))
      return false;
    return true;
  });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      {/* Filters */}
      <Box display="flex" gap={2} mb={2} flexWrap="wrap" alignItems="center">
        <TextField
          size="small"
          placeholder="Search keywords..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ minWidth: 200 }}
        />

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Ad Group</InputLabel>
          <Select
            value={filterAdGroup}
            label="Ad Group"
            onChange={(e) => setFilterAdGroup(e.target.value as number | 'all')}
          >
            <MenuItem value="all">All Ad Groups</MenuItem>
            {adGroups.map((ag) => (
              <MenuItem key={ag.id} value={ag.id}>
                {ag.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Match Type</InputLabel>
          <Select
            value={filterMatchType}
            label="Match Type"
            onChange={(e) => setFilterMatchType(e.target.value as MatchType | 'all')}
          >
            <MenuItem value="all">All Types</MenuItem>
            <MenuItem value="EXACT">Exact</MenuItem>
            <MenuItem value="PHRASE">Phrase</MenuItem>
            <MenuItem value="BROAD">Broad</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={filterStatus}
            label="Status"
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="ACTIVE">Active</MenuItem>
            <MenuItem value="PAUSED">Paused</MenuItem>
            <MenuItem value="ARCHIVED">Archived</MenuItem>
          </Select>
        </FormControl>

        <Box flex={1} />

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Add Keyword
        </Button>
      </Box>

      {filteredKeywords.length === 0 ? (
        <Alert severity="info">
          {keywords.length === 0
            ? 'No keywords yet. Add your first keyword to start targeting.'
            : 'No keywords match your filters.'}
        </Alert>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Keyword</TableCell>
                <TableCell>Ad Group</TableCell>
                <TableCell>Match Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Bid</TableCell>
                <TableCell align="center">Negative</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredKeywords.map((keyword) => {
                const adGroup = adGroups.find((ag) => ag.id === keyword.adGroupId);
                return (
                  <TableRow key={keyword.id}>
                    <TableCell>{keyword.keywordText}</TableCell>
                    <TableCell>{adGroup?.name || 'Unknown'}</TableCell>
                    <TableCell>
                      <Chip
                        label={keyword.matchType}
                        color={getMatchTypeColor(keyword.matchType)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={keyword.status}
                        color={getStatusColor(keyword.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">${Number(keyword.bid).toFixed(2)}</TableCell>
                    <TableCell align="center">
                      {keyword.isNegative ? (
                        <Chip label="Yes" color="error" size="small" />
                      ) : (
                        '—'
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(keyword.id)}
                        color="primary"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(keyword.id)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <KeywordFormDialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        campaignId={campaignId}
        keywordId={editingKeywordId}
      />
    </Box>
  );
}

export default KeywordList;
