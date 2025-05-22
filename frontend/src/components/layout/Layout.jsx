import { Outlet } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Box, Container, CssBaseline, useMediaQuery, useTheme } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  const handleDrawerToggle = () => {
    if (isClosing) {
      return;
    }
    setMobileOpen(!mobileOpen);
  };

  const handleDrawerTransitionEnd = () => {
    setIsClosing(false);
  };

  const handleDrawerClose = () => {
    if (mobileOpen) {
      setIsClosing(true);
      setMobileOpen(false);
    }
  };

  return (
    <SnackbarProvider
      maxSnack={3}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      autoHideDuration={3000}
    >
      <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: 'background.default' }}>
        <CssBaseline />
        <Header handleDrawerToggle={handleDrawerToggle} />
        <Sidebar 
          mobileOpen={mobileOpen} 
          onClose={handleDrawerClose}
          onTransitionEnd={handleDrawerTransitionEnd}
        />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: { xs: 2, md: 3 },
            width: '100%',
            pt: { xs: 8, sm: 10 },
            pl: { md: '280px' },
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
          }}
        >
          <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
            <Outlet />
          </Container>
        </Box>
      </Box>
    </SnackbarProvider>
  );
};

export default Layout;
