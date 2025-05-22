import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  Chip,
  Button,
  IconButton,
  Tooltip,
  useTheme,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Collapse,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const HerbRecommendationView = ({
  herbs = [],
  title = 'Herb Recommendations',
  mode = 'rag',
  onToggleFavorite = () => {},
  favoriteHerbs = new Set(),
}) => {
  const theme = useTheme();
  const [expandedHerb, setExpandedHerb] = useState(null);
  const [showAll, setShowAll] = useState(false);

  const handleExpandClick = (herbName) => {
    setExpandedHerb(expandedHerb === herbName ? null : herbName);
  };

  const displayedHerbs = showAll ? herbs : herbs.slice(0, 3);

  return (
    <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">{title}</Typography>
        <Box display="flex" alignItems="center">
          <Tooltip title="Learn more about these recommendations">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {herbs.length === 0 ? (
        <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
          No herb recommendations available
        </Typography>
      ) : (
        <List>
          {displayedHerbs.map((herb, index) => (
            <div key={`${herb.name}-${index}`}>
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
                    {herb.confidence && (
                      <Chip
                        label={`${Math.round(herb.confidence * 100)}%`}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 1 }}
                      />
                    )}
                    <IconButton
                      edge="end"
                      aria-label="add to favorites"
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggleFavorite(herb);
                      }}
                      sx={{
                        color: favoriteHerbs.has(herb.name) 
                          ? theme.palette.error.main 
                          : 'inherit',
                      }}
                    >
                      {favoriteHerbs.has(herb.name) ? (
                        <FavoriteIcon />
                      ) : (
                        <FavoriteBorderIcon />
                      )}
                    </IconButton>
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
                  {herb.description && (
                    <Typography variant="body2" paragraph>
                      {herb.description}
                    </Typography>
                  )}
                  
                  {herb.benefits && herb.benefits.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        Benefits:
                      </Typography>
                      <List dense disablePadding>
                        {herb.benefits.map((benefit, i) => (
                          <ListItem key={i} disableGutters>
                            <Typography variant="body2" component="span">
                              • {benefit}
                            </Typography>
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                  
                  {herb.usage && (
                    <Box mb={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        Usage:
                      </Typography>
                      <Typography variant="body2">
                        {herb.usage}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Collapse>
              
              {index < displayedHerbs.length - 1 && <Divider component="li" />}
            </div>
          ))}
        </List>
      )}
      
      {herbs.length > 3 && !showAll && (
        <Box textAlign="center" mt={2}>
          <Button 
            variant="text" 
            size="small"
            onClick={() => setShowAll(true)}
          >
            Show All ({herbs.length} herbs)
          </Button>
        </Box>
      )}
    </Paper>
  );
};

export default HerbRecommendationView;
