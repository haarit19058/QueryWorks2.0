
import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { AvailableRides } from './pages/AvailableRides';
import { AddRide } from './pages/AddRide';
import { YourRides } from './pages/YourRides';
import { RideHistory } from './pages/RideHistory';
import { Login } from './pages/Login';
import { Signup } from './pages/SignUp';
import { AppProvider, useApp } from './store';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { currentUser } = useApp();
  return currentUser ? <>{children}</> : <Navigate to="/login" replace />;
};

const AppContent: React.FC = () => {
  const { currentUser } = useApp();

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="pb-12">
        <Routes>
          <Route path="/login" element={!currentUser ? <Login /> : <Navigate to="/rides" />} />
          <Route path="/signup" element={!currentUser ? <Signup /> : <Navigate to="/rides" />} />
          <Route path="/rides" element={<PrivateRoute><AvailableRides /></PrivateRoute>} />
          <Route path="/add-ride" element={<PrivateRoute><AddRide onSuccess={() => {}} /></PrivateRoute>} />
          <Route path="/your-rides" element={<PrivateRoute><YourRides /></PrivateRoute>} />
          <Route path="/history" element={<PrivateRoute><RideHistory /></PrivateRoute>} />
          <Route path="*" element={<Navigate to={currentUser ? "/rides" : "/login"} replace />} />
        </Routes>
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AppProvider>
  );
};

export default App;
