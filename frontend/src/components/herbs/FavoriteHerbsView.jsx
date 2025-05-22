import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Collapse,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  useTheme,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Add as AddIcon,
} from '@mui/icons-material';

const FavoriteHerbsView = ({
  favoriteHerbs = [],
  onRemoveFavorite = () => {},
  onUpdateNote = () => {},
}) => {
  const theme = useTheme();
  const [expandedHerb, setExpandedHerb] = useState(null);
  const [editingNote, setEditingNote] = useState(null);
  const [noteText, setNoteText] = useState('');
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [newHerb, setNewHerb] = useState({ name: '', note: '' });

  const handleExpandClick = (herbName) => {
    setExpandedHerb(expandedHerb === herbName ? null : herbName);
  };

  const handleEditNote = (herb) => {
    setEditingNote(herb.name);
    setNoteText(herb.note || '');
  };

  const handleSaveNote = (herbName) => {
    onUpdateNote(herbName, noteText);
    setEditingNote(null);
    setNoteText('');
  };

  const handleCancelEdit = () => {
    setEditingNote(null);
    setNoteText('');
  };

  const handleAddHerb = () => {
    if (newHerb.name.trim()) {
      onUpdateNote(newHerb.name, newHerb.note || '');
      setNewHerb({ name: '', note: '' });
      setOpenAddDialog(false);
    }
  };

  // Sort favorites by name
  const sortedFavorites = [...favoriteHerbs].sort((a, b) => 
    a.name.localeCompare(b.name)
  );

  return (
    <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">My Favorite Herbs</Typography>
        <Button
          variant="outlined"
          size="small"
          startIcon={<AddIcon />}
          onClick={() => setOpenAddDialog(true)}
        >
          Add Herb
        </Button>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {sortedFavorites.length === 0 ? (
        <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
          No favorite herbs yet. Add some to track them here!
        </Typography>
      ) : (
        <List>
          {sortedFavorites.map((herb, index) => (
            <div key={herb.name}>
              <ListItem 
                button 
                onClick={() => handleExpandClick(herb.name)}
                sx={{
                  borderRadius: 1,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={herb.name}
                  secondary={herb.scientificName || ''}
                  primaryTypographyProps={{
                    variant: 'subtitle1',
                    fontWeight: 'medium',
                  }}
                />
                <ListItemSecondaryAction>
                  <Box display="flex" alignItems="center">
                    <Tooltip title="Edit note">
                      <IconButton
                        edge="end"
                        aria-label="edit note"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditNote(herb);
                        }}
                        size="small"
                        sx={{ mr: 1 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Remove from favorites">
                      <IconButton
                        edge="end"
                        aria-label="remove from favorites"
                        onClick={(e) => {
                          e.stopPropagation();
                          onRemoveFavorite(herb.name);
                        }}
                        size="small"
                      >
                        <DeleteIcon fontSize="small" color="error" />
                      </IconButton>
                    </Tooltip>
                    {expandedHerb === herb.name ? (
                      <ExpandLessIcon />
                    ) : (
                      <ExpandMoreIcon />
                    )}
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
              
              <Collapse in={expandedHerb === herb.name} timeout="auto" unmountOnExit>
                <Box sx={{ pl: 3, pr: 2, pb: 2 }}>
                  {editingNote === herb.name ? (
                    <Box mb={2}>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        variant="outlined"
                        label="Your notes"
                        value={noteText}
                        onChange={(e) => setNoteText(e.target.value)}
                        size="small"
                      />
                      <Box display="flex" justifyContent="flex-end" mt={1} gap={1}>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<CancelIcon />}
                          onClick={handleCancelEdit}
                        >
                          Cancel
                        </Button>
                        <Button
                          size="small"
                          variant="contained"
                          startIcon={<SaveIcon />}
                          onClick={() => handleSaveNote(herb.name)}
                        >
                          Save
                        </Button>
                      </Box>
                    </Box>
                  ) : (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        Your Notes:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {herb.note || 'No notes added yet. Click the edit button to add some notes.'}
                      </Typography>
                    </Box>
                  )}
                  
                  {herb.benefits && herb.benefits.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        Benefits:
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {herb.benefits.map((benefit, i) => (
                          <Chip
                            key={i}
                            label={benefit}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
              </Collapse>
              
              {index < sortedFavorites.length - 1 && <Divider component="li" />}
            </div>
          ))}
        </List>
      )}

      {/* Add Herb Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Custom Herb</DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <TextField
              fullWidth
              label="Herb Name"
              value={newHerb.name}
              onChange={(e) => setNewHerb({ ...newHerb, name: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Notes (Optional)"
              value={newHerb.note}
              onChange={(e) => setNewHerb({ ...newHerb, note: e.target.value })}
              margin="normal"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddHerb} 
            variant="contained" 
            disabled={!newHerb.name.trim()}
            startIcon={<SaveIcon />}
          >
            Add Herb
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default FavoriteHerbsView;
