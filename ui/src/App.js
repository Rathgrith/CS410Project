import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Homepage from './components/Homepage';
import { MantineProvider } from '@mantine/core';

function App() {
  return (
    <MantineProvider theme={{}}>
      <Router>
        <Routes>
          <Route path="/" element={<Homepage />} />
          {/* <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} /> */}
        </Routes>
      </Router>
    </MantineProvider>
  );
}

export default App;
