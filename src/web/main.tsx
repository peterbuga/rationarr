// import { StrictMode } from 'react'
// import { createRoot } from 'react-dom/client'
// import './index.css'
// import App from './App.tsx'

// import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// const theme = createTheme({
//   palette: {
//     mode: 'dark', // or 'dark'
//   },
// });


// createRoot(document.getElementById('root')!).render(
//   // <StrictMode>
//   //   <App />
//   // </StrictMode>,

//   <ThemeProvider theme={theme}>
//     <CssBaseline />
//     <App />
//   </ThemeProvider>,
// )




// import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { useState, useMemo } from 'react';

const Root = () => {
  const [mode, setMode] = useState<'light' | 'dark'>('light');

  const theme = useMemo(() =>
    createTheme({
      palette: {
        mode,
      },
    }), [mode]
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App toggleMode={() => setMode(prev => prev === 'light' ? 'dark' : 'light')} mode={mode} />
    </ThemeProvider>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(<Root />);
