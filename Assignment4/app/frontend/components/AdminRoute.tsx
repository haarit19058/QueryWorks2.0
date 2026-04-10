// src/components/AdminRoute.tsx
import { Navigate } from 'react-router-dom';
import { useApp } from '../store';

export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentUser, isAdmin, loading } = useApp();

  if (loading) return null;

  // Not logged in → send to login
  if (!currentUser) return <Navigate to="/login" replace />;

  // Logged in but not admin → send to rides (or a 403 page)
  if (!isAdmin) return <Navigate to="/rides" replace />;

  return <>{children}</>;
};