import { useState, useEffect } from 'react';
import { 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Divider, 
  Typography, 
  Box, 
  useMediaQuery, 
  useTheme,
  Tooltip,
  IconButton,
  Collapse,
  styled,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Psychology as PsychologyIcon,
  LocalHospital as LocalHospitalIcon,
  Spa as SpaIcon,
  Info as InfoIcon,
  ChatBubbleOutline as ChatIcon,
  Assessment as MetricsIcon,
  Favorite as DoshaIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';
import { Link as RouterLink, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

const menuItems = [
  { 
    text: 'Dashboard', 
    icon: <DashboardIcon />, 
    path: '/',
    subItems: []
  },
  { 
    text: 'Ayurveda Chat', 
    icon: <ChatIcon />, 
    path: '/chat',
    subItems: []
  },
  { 
    text: 'Dosha Analysis', 
    icon: <DoshaIcon />, 
    path: '/dosha-analysis',
    subItems: []
  },
  { 
    text: 'Metrics Dashboard', 
    icon: <MetricsIcon />, 
    path: '/metrics',
    subItems: []
  },
  { 
    text: 'Tools', 
    icon: <PsychologyIcon />, 
    path: null,
    subItems: [
      { text: 'Dosha Comparison', path: '/tools/dosha' },
      { text: 'Symptom Analyzer', path: '/tools/symptoms' },
      { text: 'Herb Recommender', path: '/tools/herbs' },
      { text: 'Disease Predictor', path: '/tools/disease-predictor' },
    ]
  },
  { 
    text: 'About', 
    icon: <InfoIcon />, 
    path: '/about',
    subItems: []
  },
];

const Sidebar = ({ mobileOpen, onClose, onTransitionEnd }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const [openSubmenu, setOpenSubmenu] = useState({});

  useEffect(() => {
    // Close mobile drawer when route changes
    if (isMobile && mobileOpen) {
      onClose();
    }
  }, [location.pathname, isMobile, mobileOpen, onClose]);

  const handleSubmenuToggle = (text) => {
    setOpenSubmenu(prev => ({
      ...prev,
      [text]: !prev[text]
    }));
  };

  const isActive = (path, subItems = []) => {
    if (path === location.pathname) return true;
    if (subItems.some(item => item.path === location.pathname)) return true;
    return false;
  };

  const drawerContent = (
    <>
      <DrawerHeader>
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, ml: 2 }}>
          Ayurveda AI
        </Typography>
        <IconButton onClick={onClose}>
          {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </DrawerHeader>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <div key={item.text}>
            <ListItem disablePadding>
              <ListItemButton
                component={item.path ? RouterLink : 'div'}
                to={item.path || '#'}
                onClick={item.subItems.length ? () => handleSubmenuToggle(item.text) : undefined}
                selected={isActive(item.path, item.subItems)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'primary.light',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ color: 'inherit' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
                {item.subItems.length > 0 && (
                  openSubmenu[item.text] ? <ExpandLess /> : <ExpandMore />
                )}
              </ListItemButton>
            </ListItem>
            {item.subItems.length > 0 && (
              <Collapse in={openSubmenu[item.text]} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  {item.subItems.map((subItem) => (
                    <ListItemButton
                      key={subItem.path}
                      component={RouterLink}
                      to={subItem.path}
                      selected={location.pathname === subItem.path}
                      sx={{
                        pl: 4,
                        '&.Mui-selected': {
                          backgroundColor: 'primary.light',
                          color: 'primary.contrastText',
                          '&:hover': {
                            backgroundColor: 'primary.dark',
                          },
                        },
                      }}
                    >
                      <ListItemText primary={subItem.text} />
                    </ListItemButton>
                  ))}
                </List>
              </Collapse>
            )}
          </div>
        ))}
      </List>
    </>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      aria-label="sidebar"
    >
      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        onTransitionEnd={onTransitionEnd}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { 
            boxSizing: 'border-box', 
            width: drawerWidth,
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            borderRight: 'none',
            backgroundColor: 'background.paper',
          },
        }}
      >
        {drawerContent}
      </Drawer>
    </Box>
  );
};

export default Sidebar;
