import React, { useState, useEffect } from 'react';
import { Box, Container, Tabs, Tab, useTheme, useMediaQuery, Grid } from '@mui/material';
import { 
  Home as HomeIcon, 
  Chat as ChatIcon, 
  Spa as DoshaIcon, 
  LocalHospital as HealthIcon,
  MenuBook as ArticleIcon
} from '@mui/icons-material';

// Import components
import Dashboard from './Dashboard';
import ChatPage from './ChatPage';
import DoshaAnalysis from './DoshaAnalysis';
import HealthRecommendations from './HealthRecommendations';
import ArticlesHub from './ArticlesHub';

// Tab Panel Component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`ayurvedic-hub-tabpanel-${index}`}
      aria-labelledby={`ayurvedic-hub-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: { xs: 1, sm: 2, md: 3 } }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `ayurvedic-hub-tab-${index}`,
    'aria-controls': `ayurvedic-hub-tabpanel-${index}`,
  };
}

const AyurvedicHub = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [value, setValue] = useState(0);
  const [userData, setUserData] = useState(null);

  // Load user data from localStorage or context
  useEffect(() => {
    // TODO: Replace with actual user data fetch
    const storedUser = localStorage.getItem('ayurvedicUser');
    if (storedUser) {
      setUserData(JSON.parse(storedUser));
    }
  }, []);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  // Tab configuration
  const tabs = [
    { 
      label: 'Dashboard', 
      icon: <HomeIcon />, 
      component: <Dashboard userData={userData} /> 
    },
    { 
      label: 'Chat & Predict', 
      icon: <ChatIcon />, 
      component: <ChatPage userData={userData} /> 
    },
    { 
      label: 'Dosha Analysis', 
      icon: <DoshaIcon />, 
      component: <DoshaAnalysis userData={userData} /> 
    },
    { 
      label: 'Health Tools', 
      icon: <HealthIcon />, 
      component: <HealthRecommendations userData={userData} /> 
    },
    { 
      label: 'Ayurveda Articles', 
      icon: <ArticleIcon />, 
      component: <ArticlesHub userData={userData} /> 
    }
  ];

  return (
    <Container maxWidth="xl" disableGutters={isMobile}>
      <Box sx={{ width: '100%', bgcolor: 'background.paper' }}>
        <Tabs
          value={value}
          onChange={handleChange}
          variant={isMobile ? 'scrollable' : 'standard'}
          scrollButtons={isMobile ? 'auto' : false}
          allowScrollButtonsMobile
          aria-label="ayurvedic hub tabs"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTabs-flexContainer': {
              flexWrap: 'wrap',
            },
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              icon={tab.icon}
              label={tab.label}
              iconPosition="start"
              {...a11yProps(index)}
              sx={{
                minHeight: 64,
                '&.Mui-selected': {
                  color: theme.palette.primary.main,
                  fontWeight: 'bold',
                },
              }}
            />
          ))}
        </Tabs>
      </Box>

      {tabs.map((tab, index) => (
        <TabPanel key={index} value={value} index={index}>
          {tab.component}
        </TabPanel>
      ))}
    </Container>
  );
};

export default AyurvedicHub;
