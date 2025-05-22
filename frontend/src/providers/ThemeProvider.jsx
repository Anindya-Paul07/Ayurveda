import { createContext, useState, useMemo, useContext, useEffect } from 'react';
import { ThemeProvider as MuiThemeProvider, CssBaseline } from '@mui/material';
import { theme, darkTheme } from '../theme';

const ThemeContext = createContext({
  mode: 'light',
  toggleColorMode: () => {},
});

export const useThemeContext = () => useContext(ThemeContext);

export const AppThemeProvider = ({ children }) => {
  const [mode, setMode] = useState('light');

  // Load theme preference from localStorage on initial render
  useEffect(() => {
    const savedMode = localStorage.getItem('themeMode') || 'light';
    setMode(savedMode);
  }, []);

  const colorMode = useMemo(
    () => ({
      mode,
      toggleColorMode: () => {
        setMode((prevMode) => {
          const newMode = prevMode === 'light' ? 'dark' : 'light';
          localStorage.setItem('themeMode', newMode);
          return newMode;
        });
      },
    }),
    [mode]
  );

  const currentTheme = useMemo(() => 
    mode === 'dark' ? darkTheme : theme,
    [mode]
  );

  return (
    <ThemeContext.Provider value={colorMode}>
      <MuiThemeProvider theme={currentTheme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export default AppThemeProvider;
