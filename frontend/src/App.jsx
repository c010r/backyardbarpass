import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import EventDetail from './pages/EventDetail';
import MyTickets from './pages/MyTickets';
import Scanner from './pages/Scanner';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Register />} />
        <Route path="/evento/:id" element={<EventDetail />} />
        <Route path="/mis-entradas" element={<MyTickets />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/dashboard" element={<Dashboard />} />
        {/* Rutas de retorno de Mercado Pago (pueden ser la misma página de éxito) */}
        <Route path="/compra/exito" element={<MyTickets />} />
      </Routes>
    </Router>
  );
}

export default App;
