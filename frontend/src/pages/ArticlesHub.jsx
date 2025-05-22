import React, { useState, useEffect, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia, 
  Typography, 
  Button, 
  Chip, 
  TextField, 
  InputAdornment, 
  IconButton,
  Pagination,
  useTheme,
  CircularProgress,
  Tabs,
  Tab,
  Paper,
  Snackbar,
  Alert,
  Skeleton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import { 
  Search as SearchIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  Share as ShareIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  FilterList as FilterIcon,
  Close as CloseIcon,
  NewReleases as NewIcon,
  Whatshot as PopularIcon,
  AccessTime as RecentIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Category as CategoryIcon
} from '@mui/icons-material';
import { format, parseISO } from 'date-fns';
import api from '../services/api';

const ArticleCard = ({ article, onBookmark, onLike, onShare }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);
  const { user } = useContext(AuthContext);

  const handleClick = () => {
    navigate(`/articles/${article.id}`);
  };

  const handleBookmarkClick = async (e) => {
    e.stopPropagation();
    if (!user) {
      navigate('/login', { state: { from: `/articles/${article.id}` } });
      return;
    }
    try {
      await onBookmark(article.id, !article.isBookmarked);
    } catch (error) {
      console.error('Error updating bookmark:', error);
    }
  };

  const handleLikeClick = async (e) => {
    e.stopPropagation();
    if (!user) {
      navigate('/login', { state: { from: `/articles/${article.id}` } });
      return;
    }
    try {
      await onLike(article.id, !article.isLiked);
    } catch (error) {
      console.error('Error updating like:', error);
    }
  };

  const handleShareClick = async (e) => {
    e.stopPropagation();
    try {
      await onShare(article);
    } catch (error) {
      console.error('Error sharing article:', error);
    }
  };

  return (
    <Card 
      elevation={isHovered ? 4 : 1}
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
        },
      }}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {article.imageUrl ? (
        <CardMedia
          component="img"
          height="180"
          image={article.imageUrl}
          alt={article.title}
          sx={{
            transition: 'opacity 0.3s ease-in-out',
            opacity: isHovered ? 0.9 : 1,
          }}
        />
      ) : (
        <Box 
          height={180} 
          bgcolor="grey.100"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography color="textSecondary">No Image</Typography>
        </Box>
      )}
      
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box display="flex" alignItems="center" mb={1} flexWrap="wrap">
          {article.categories?.map((category, index) => (
            <Chip 
              key={index}
              label={category} 
              size="small" 
              color="primary" 
              variant="outlined"
              sx={{ mr: 1, mb: 1, fontSize: '0.7rem' }}
            />
          ))}
          <Typography 
            variant="caption" 
            color="text.secondary" 
            sx={{ ml: 'auto', fontSize: '0.75rem' }}
          >
            {format(parseISO(article.publishedAt), 'MMM d, yyyy')}
            {article.readingTime && ` • ${article.readingTime} min read`}
          </Typography>
        </Box>
        
        <Typography 
          gutterBottom 
          variant="h6" 
          component="h3"
          sx={{
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            mb: 1.5,
            fontWeight: 600,
            lineHeight: 1.3,
          }}
        >
          {article.title}
        </Typography>
        
        <Typography 
          variant="body2" 
          color="text.secondary" 
          paragraph 
          sx={{
            flexGrow: 1,
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            mb: 2,
            fontSize: '0.9rem',
            lineHeight: 1.6,
          }}
        >
          {article.summary}
        </Typography>
        
        <Box 
          display="flex" 
          justifyContent="space-between" 
          alignItems="center"
          sx={{ mt: 'auto', pt: 1, borderTop: '1px solid', borderColor: 'divider' }}
        >
          <Box display="flex" alignItems="center">
            <Tooltip title={article.isLiked ? 'Unlike' : 'Like'} arrow>
              <IconButton 
                size="small" 
                onClick={(e) => {
                  e.stopPropagation();
                  handleLikeClick(e);
                }}
                color={article.isLiked ? 'error' : 'default'}
                sx={{
                  '&:hover': {
                    color: 'error.main',
                    backgroundColor: 'rgba(244, 67, 54, 0.08)'
                  }
                }}
              >
                {article.isLiked ? (
                  <FavoriteIcon fontSize="small" />
                ) : (
                  <FavoriteBorderIcon fontSize="small" />
                )}
              </IconButton>
            </Tooltip>
            <Typography variant="caption" color="text.secondary" component="span">
              {article.likeCount || 0}
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center">
            <Tooltip title={article.isBookmarked ? 'Remove bookmark' : 'Save for later'} arrow>
              <IconButton 
                size="small" 
                onClick={(e) => {
                  e.stopPropagation();
                  handleBookmarkClick(e);
                }}
                color={article.isBookmarked ? 'primary' : 'default'}
                sx={{
                  '&:hover': {
                    color: 'primary.main',
                    backgroundColor: 'rgba(25, 118, 210, 0.08)'
                  }
                }}
              >
                {article.isBookmarked ? (
                  <BookmarkIcon fontSize="small" />
                ) : (
                  <BookmarkBorderIcon fontSize="small" />
                )}
              </IconButton>
            </Tooltip>
            <Tooltip title="Share" arrow>
              <IconButton 
                size="small" 
                onClick={(e) => {
                  e.stopPropagation();
                  handleShareClick(e);
                }}
                sx={{
                  '&:hover': {
                    color: 'primary.main',
                    backgroundColor: 'rgba(0, 0, 0, 0.04)'
                  }
                }}
              >
                <ShareIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const ArticlesHub = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('all');
  const [categories, setCategories] = useState(['all']);
  const [sortBy, setSortBy] = useState('newest');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const theme = useTheme();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  // Fetch articles
  const fetchArticles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        offset: (page - 1) * itemsPerPage,
        query: searchQuery,
        category: category === 'all' ? undefined : category,
        sort: sortBy === 'popular' ? 'view_count' : 'published_at',
        order: 'desc'
      };
      
      // Fetch articles from the API
      const response = await articleService.getArticles(params);
      const { data: articles, pagination } = response.data;
      
      // Transform articles to match the expected format
      const formattedArticles = articles.map(article => ({
        id: article.id,
        title: article.title,
        summary: article.summary || article.description || '',
        imageUrl: article.image_url,
        categories: article.tags ? article.tags.map(tag => tag.name) : [],
        publishedAt: article.published_at || article.created_at,
        readingTime: Math.ceil((article.content || '').split(' ').length / 200) || 5, // 200 words per minute
        isBookmarked: article.is_bookmarked || false,
        isLiked: article.is_liked || false,
        likeCount: article.like_count || 0,
        viewCount: article.view_count || 0,
        author: article.author,
        source: article.source
      }));
      
      setArticles(formattedArticles);
      setTotalPages(Math.ceil((pagination?.total || 1) / itemsPerPage));
      
      // If it's the first load, also fetch categories if not already loaded
      if (page === 1 && categories.length === 1) {
        fetchCategories();
      }
    } catch (err) {
      console.error('Error fetching articles:', err);
      const errorMessage = err.response?.data?.message || 'Failed to load articles. Please try again later.';
      setError(errorMessage);
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
      setArticles([]);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [page, searchQuery, category, sortBy, categories.length]);

  // Fetch categories
  const fetchCategories = async () => {
    try {
      const response = await articleService.getCategories();
      // The API returns an array of categories, with 'all' already added in the service
      setCategories(response.data);
    } catch (err) {
      console.error('Error fetching categories:', err);
      // Fallback to default categories if API fails
      setCategories([
        'all',
        'Ayurveda',
        'Diet',
        'Yoga',
        'Herbs',
        'Lifestyle',
        'Wellness'
      ]);
    }
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page on new search
    fetchArticles();
  };

  // Handle page change
  const handlePageChange = (event, value) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Handle category change
  const handleCategoryChange = (event, newValue) => {
    setCategory(newValue);
    setPage(1); // Reset to first page on category change
  };

  // Handle sort menu
  const handleSortMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleSortMenuClose = () => {
    setAnchorEl(null);
  };

  const handleSortSelect = (value) => {
    setSortBy(value);
    setPage(1); // Reset to first page on sort change
    handleSortMenuClose();
  };

  // Handle refresh
  const handleRefresh = () => {
    setIsRefreshing(true);
  };

  // Initial load
  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);

  // Sort options
  const sortOptions = [
    { value: 'newest', label: 'Newest', icon: <NewIcon /> },
    { value: 'popular', label: 'Most Popular', icon: <PopularIcon /> },
    { value: 'recent', label: 'Recently Updated', icon: <RecentIcon /> }
  ];

  // Filter articles based on search query and category
  const filteredArticles = articles.filter(article => {
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        article.summary.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = category === 'all' || article.categories.includes(category);
    return matchesSearch && matchesCategory;
  });

  // Sort articles
  const sortedArticles = [...filteredArticles].sort((a, b) => {
    if (sortBy === 'newest') {
      return new Date(b.publishedAt) - new Date(a.publishedAt);
    } else if (sortBy === 'popular') {
      return (b.likeCount || 0) - (a.likeCount || 0);
    } else {
      return new Date(b.updatedAt || b.publishedAt) - new Date(a.updatedAt || a.publishedAt);
    }
  });

  // Pagination
  const startIndex = (page - 1) * 9;
  const paginatedArticles = sortedArticles.slice(startIndex, startIndex + 9);

  // Handle article click
  const handleArticleClick = async (articleId) => {
    try {
      // Track article view
      await articleService.trackView(articleId);
      navigate(`/articles/${articleId}`);
    } catch (error) {
      console.error('Error tracking article view:', error);
      // Still navigate even if tracking fails
      navigate(`/articles/${articleId}`);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Ayurvedic Articles & Resources
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Discover the wisdom of Ayurveda through our curated collection of articles
        </Typography>
      </Box>

      {/* Search and Filter Bar */}
      <Paper elevation={0} sx={{ p: 2, mb: 3, borderRadius: 2, bgcolor: 'background.paper' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <form onSubmit={handleSearch}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: searchQuery && (
                    <InputAdornment position="end">
                      <IconButton
                        edge="end"
                        onClick={() => setSearchQuery('')}
                        size="small"
                      >
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </form>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={handleSortMenuOpen}
              sx={{ justifyContent: 'flex-start' }}
            >
              Sort: {sortOptions.find(opt => opt.value === sortBy)?.label || 'Newest'}
            </Button>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleSortMenuClose}
            >
              {sortOptions.map((option) => (
                <MenuItem 
                  key={option.value} 
                  onClick={() => handleSortSelect(option.value)}
                  selected={sortBy === option.value}
                >
                  <ListItemIcon>
                    {option.icon}
                  </ListItemIcon>
                  <ListItemText>{option.label}</ListItemText>
                </MenuItem>
              ))}
            </Menu>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
          </Grid>
        </Grid>

        {/* Categories */}
        <Box sx={{ mt: 3, overflowX: 'auto', pb: 1 }}>
          <Tabs
            value={category}
            onChange={handleCategoryChange}
            variant="scrollable"
            scrollButtons="auto"
            allowScrollButtonsMobile
            sx={{
              '& .MuiTabs-indicator': {
                height: 3,
              },
            }}
          >
            {categories.map((cat) => (
              <Tab 
                key={cat} 
                value={cat}
                label={cat.charAt(0).toUpperCase() + cat.slice(1).replace(/-/g, ' ')}
                sx={{
                  minWidth: 'auto',
                  px: 2,
                  textTransform: 'none',
                  '&.Mui-selected': {
                    color: 'primary.main',
                    fontWeight: 'bold',
                  },
                }}
              />
            ))}
          </Tabs>
        </Box>
      </Paper>

      {/* Error Message */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={() => setError(null)}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
        >
          {error}
        </Alert>
      )}

      {/* Loading State */}
      {loading ? (
        <Grid container spacing={3}>
          {Array.from({ length: 6 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <Skeleton variant="rectangular" height={180} />
                <CardContent>
                  <Skeleton width="80%" height={28} />
                  <Skeleton width="60%" height={24} sx={{ mt: 1 }} />
                  <Box sx={{ display: 'flex', mt: 2 }}>
                    <Skeleton width={60} height={24} sx={{ mr: 1 }} />
                    <Skeleton width={80} height={24} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        /* Articles Grid */
        <>
          {paginatedArticles.length > 0 ? (
            <Grid container spacing={3}>
              {paginatedArticles.map((article) => (
                <Grid item xs={12} sm={6} md={4} key={article.id}>
                  <Card 
                    sx={{ 
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: theme.shadows[8],
                      },
                    }}
                    elevation={2}
                  >
                    <Box 
                      sx={{ 
                        position: 'relative',
                        paddingTop: '56.25%', // 16:9 aspect ratio
                        cursor: 'pointer',
                        overflow: 'hidden',
                      }}
                      onClick={() => handleArticleClick(article.id)}
                    >
                      <CardMedia
                        component="img"
                        image={article.imageUrl || '/placeholder-article.jpg'}
                        alt={article.title}
                        sx={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                        }}
                      />
                      <Box 
                        sx={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          zIndex: 1,
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleBookmark(article.id, article.isBookmarked);
                        }}
                      >
                        <IconButton 
                          size="small" 
                          sx={{ 
                            bgcolor: 'background.paper',
                            '&:hover': { bgcolor: 'action.hover' },
                          }}
                        >
                          {article.isBookmarked ? (
                            <BookmarkIcon color="primary" />
                          ) : (
                            <BookmarkBorderIcon />
                          )}
                        </IconButton>
                      </Box>
                    </Box>
                    
                    <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ mb: 1 }}>
                        {article.categories && article.categories.slice(0, 2).map((cat) => (
                          <Chip 
                            key={cat} 
                            label={cat} 
                            size="small" 
                            sx={{ 
                              mr: 1, 
                              mb: 1,
                              fontSize: '0.65rem',
                              fontWeight: 500,
                            }} 
                          />
                        ))}
                        {article.categories && article.categories.length > 2 && (
                          <Chip 
                            label={`+${article.categories.length - 2}`} 
                            size="small"
                            sx={{ 
                              fontSize: '0.65rem',
                              fontWeight: 500,
                            }}
                          />
                        )}
                      </Box>
                      
                      <Typography 
                        variant="h6" 
                        component="h2" 
                        gutterBottom
                        sx={{
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          minHeight: '3.5em',
                          cursor: 'pointer',
                          '&:hover': {
                            color: 'primary.main',
                          },
                        }}
                        onClick={() => handleArticleClick(article.id)}
                      >
                        {article.title}
                      </Typography>
                      
                      <Typography 
                        variant="body2" 
                        color="text.secondary"
                        sx={{
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          mb: 2,
                          flexGrow: 1,
                        }}
                      >
                        {article.summary}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 'auto' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <IconButton 
                            size="small" 
                            onClick={() => handleLike(article.id, article.isLiked)}
                            color={article.isLiked ? 'error' : 'default'}
                            sx={{ mr: 0.5 }}
                          >
                            {article.isLiked ? <FavoriteIcon /> : <FavoriteBorderIcon />}
                          </IconButton>
                          <Typography variant="body2" color="text.secondary">
                            {article.likeCount || 0}
                          </Typography>
                        </Box>
                        
                        <Box>
                          <Tooltip title="Share">
                            <IconButton 
                              size="small" 
                              onClick={() => handleShare(article)}
                              sx={{ ml: 0.5 }}
                            >
                              <ShareIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {article.readingTime} min read
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {format(parseISO(article.publishedAt), 'MMM d, yyyy')}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Box 
              sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center', 
                minHeight: '300px',
                textAlign: 'center',
                p: 4,
              }}
            >
              <ErrorIcon color="disabled" sx={{ fontSize: 60, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No articles found
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ maxWidth: '500px', mb: 3 }}>
                We couldn't find any articles matching your criteria. Try adjusting your search or filters.
              </Typography>
              <Button 
                variant="outlined" 
                startIcon={<RefreshIcon />}
                onClick={() => {
                  setSearchQuery('');
                  setCategory('all');
                  setPage(1);
                }}
              >
                Reset filters
              </Button>
            </Box>
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
              <Pagination 
                count={totalPages} 
                page={page} 
                onChange={handlePageChange}
                color="primary"
                size="large"
                showFirstButton 
                showLastButton
                sx={{
                  '& .MuiPaginationItem-root': {
                    fontSize: '1rem',
                    minWidth: '40px',
                    height: '40px',
                    '&.Mui-selected': {
                      fontWeight: 'bold',
                    },
                  },
                }}
              />
            </Box>
          )}
        </>
      )}
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
          elevation={6}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ArticlesHub;
