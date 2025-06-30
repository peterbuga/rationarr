// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'


// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       {/* <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.tsx</code> and save to test HMRaaa
//         </p>
//       </div> */}
//       {/* <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p> */}
//     </>
//   )
// }

// export default App

import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import { BarChart } from '@mui/x-charts/BarChart';
import { LineChart } from '@mui/x-charts/LineChart';
import {
  LocalizationProvider,
  DatePicker,
} from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
// import { TextField, Button, Stack, Typography } from '@mui/material';
import { Button, Stack, Typography } from '@mui/material';

interface AppProps {
  toggleMode: () => void;
  mode: 'light' | 'dark';
}

const rows = [
  { id: 1, col1: 'Hello', col2: 'World' },
  { id: 2, col1: 'MUI', col2: 'X Rocks' },
];

const columns: GridColDef[] = [
  { field: 'col1', headerName: 'Column 1', width: 150 },
  { field: 'col2', headerName: 'Column 2', width: 150 },
];

export function DifferentLength() {
  return (
    <LineChart
      xAxis={[{ data: [1, 2, 3, 5, 8, 10, 12, 15, 16] }]}
      series={[
        {
          data: [2, 5.5, 2, 8.5, 1.5, 5],
          valueFormatter: (value) => (value == null ? 'NaN' : value.toString()),
        },
        {
          data: [null, null, null, null, 5.5, 2, 8.5, 1.5, 5],
        },
        {
          data: [7, 8, 5, 4, null, null, 2, 5.5, 1],
          valueFormatter: (value) => (value == null ? '?' : value.toString()),
        },
      ]}
      height={200}
      margin={{ bottom: 10 }}
    />
  );
}

const App: React.FC<AppProps> = ({ toggleMode, mode }) => {
  const [date, setDate] = React.useState<Date | null>(null);

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Stack spacing={2} sx={{ p: 4 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5">MUI X Light/Dark Mode</Typography>
          <Button variant="outlined" onClick={toggleMode}>
            Toggle {mode === 'light' ? 'Dark' : 'Light'} Mode
          </Button>
        </Stack>

        <div style={{ height: 300, width: '100%' }}>
          <DataGrid rows={rows} columns={columns} />
        </div>

        <DatePicker
          label="Select date"
          value={date}
          onChange={(newValue) => setDate(newValue)}
          slotProps={{ textField: {} }}
        />
        <BarChart
          xAxis={[
            {
              id: 'barCategories',
              data: ['bar A', 'bar B', 'bar C'],
            },
          ]}
          series={[
            {
              data: [2, 5, 3],
            },
          ]}
          height={300}
        />
        <DifferentLength />
        {/* <LineChart
          series={[{ data: [null, null, 10, 11, 12] }]}
          xAxis={[{ data: [0, 1, 2, 3, 4, 5, 6] }]}
        /> */}
      </Stack>
    </LocalizationProvider>
  );
};

export default App;
