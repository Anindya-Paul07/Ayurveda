import { Box, Typography, Grid, Paper, Divider, Chip, useTheme } from '@mui/material';
import { CompareArrows as CompareArrowsIcon } from '@mui/icons-material';

const HerbComparisonView = ({ ragHerbs = [], agenticHerbs = [] }) => {
  const theme = useTheme();

  // Find common herbs
  const commonHerbs = ragHerbs.filter(ragHerb => 
    agenticHerbs.some(agenticHerb => agenticHerb.name === ragHerb.name)
  );

  // Find herbs only in RAG
  const ragUniqueHerbs = ragHerbs.filter(ragHerb => 
    !agenticHerbs.some(agenticHerb => agenticHerb.name === ragHerb.name)
  );

  // Find herbs only in Agentic
  const agenticUniqueHerbs = agenticHerbs.filter(agenticHerb => 
    !ragHerbs.some(ragHerb => ragHerb.name === agenticHerb.name)
  );

  const renderHerbChip = (herb, color = 'default') => (
    <Chip
      key={herb.name}
      label={`${herb.name}${herb.confidence ? ` (${Math.round(herb.confidence * 100)}%)` : ''}`}
      color={color}
      variant="outlined"
      sx={{ m: 0.5 }}
    />
  );

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <CompareArrowsIcon color="action" sx={{ mr: 1 }} />
        <Typography variant="h6">Herb Comparison</Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Common Herbs */}
        {commonHerbs.length > 0 && (
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography variant="subtitle2" gutterBottom>
                Common Recommendations
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Both approaches recommend these herbs:
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {commonHerbs.map(herb => renderHerbChip(herb, 'primary'))}
              </Box>
            </Paper>
          </Grid>
        )}

        {/* RAG Only Herbs */}
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" gutterBottom>
              RAG Only
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Only recommended by the RAG approach:
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {ragUniqueHerbs.length > 0 ? (
                ragUniqueHerbs.map(herb => renderHerbChip(herb, 'secondary'))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No unique RAG recommendations
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Agentic Only Herbs */}
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" gutterBottom>
              Agentic Only
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Only recommended by the Agentic approach:
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {agenticUniqueHerbs.length > 0 ? (
                agenticUniqueHerbs.map(herb => renderHerbChip(herb, 'success'))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No unique Agentic recommendations
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HerbComparisonView;
