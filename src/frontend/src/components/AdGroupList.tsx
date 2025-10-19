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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { deleteAdGroup } from '../store/slices/adGroupSlice';
import AdGroupFormDialog from './AdGroupFormDialog';

interface AdGroupListProps {
  campaignId: number;
}

function AdGroupList({ campaignId }: AdGroupListProps) {
  const dispatch = useDispatch<AppDispatch>();
  const { adGroups, loading, error } = useSelector((state: RootState) => state.adGroups);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAdGroupId, setEditingAdGroupId] = useState<number | null>(null);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this ad group?')) {
      await dispatch(deleteAdGroup(id));
    }
  };

  const handleEdit = (id: number) => {
    setEditingAdGroupId(id);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingAdGroupId(null);
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Add Ad Group
        </Button>
      </Box>

      {adGroups.length === 0 ? (
        <Alert severity="info">
          No ad groups yet. Create your first ad group to organize your keywords.
        </Alert>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Default Bid</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {adGroups.map((adGroup) => (
                <TableRow key={adGroup.id}>
                  <TableCell>{adGroup.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={adGroup.status}
                      color={getStatusColor(adGroup.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    ${Number(adGroup.defaultBid).toFixed(2)}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => handleEdit(adGroup.id)}
                      color="primary"
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(adGroup.id)}
                      color="error"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <AdGroupFormDialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        campaignId={campaignId}
        adGroupId={editingAdGroupId}
      />
    </Box>
  );
}

export default AdGroupList;
