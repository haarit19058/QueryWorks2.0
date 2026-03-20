import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from './lib/api'; 

// ── Types (unchanged) ────────────────────────────────────────────────────────

export interface User {
  MemberID: number;
  FullName: string;
  Email: string;
  ProfileImageURL: string;
  Gender: string;
  Programme: string;
  Branch: string;
  BatchYear: number;
  ContactNumber: string;
  Age: number;
}

export interface Ride {
  RideID: string;
  AdminID: number;
  HostName: string;
  ProfileImageURL: string;
  AvailableSeats: number;
  PassengerCount: number;
  Source: string;
  Destination: string;
  VehicleType: string;
  StartTime: string;
  EstimatedTime: number;
  FemaleOnly: boolean;
  Passengers: { MemberID: number; FullName: string }[];
}

export interface BookingRequest {
  RequestID: number;
  RideID: string;
  PassengerID: number;
  RequestStatus: 'PENDING' | 'APPROVED' | 'REJECTED';
  RequestedAt: string;
}

export interface NewUserPayload {
  isNewUser: true;
  email: string;
  name: string;
  picture: string;
  google_sub: string;
}

// ── Context type ─────────────────────────────────────────────────────────────

interface AppContextType {
  currentUser: User | null;
  rides: Ride[];
  requests: BookingRequest[];
  loading: boolean;

  loginWithGoogle: (code: string) => Promise<NewUserPayload | { isNewUser: false }>;
  registerUser: (data: any) => Promise<void>;
  logout: () => Promise<void>;

  addRide: (rideData: Omit<Ride, 'RideID' | 'HostName' | 'ProfileImageURL' | 'Passengers'>) => Promise<void>;
  refreshRides: () => Promise<void>;

  requestToJoin: (rideId: string) => Promise<void>;
  updateRequest: (requestId: number, status: 'APPROVED' | 'REJECTED') => Promise<void>;

  completeRide: (rideId: string) => Promise<void>;
}

// ── Context ──────────────────────────────────────────────────────────────────

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {

  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [rides, setRides]             = useState<Ride[]>([]);
  const [requests, setRequests]       = useState<BookingRequest[]>([]);
  const [loading, setLoading]         = useState(true);  // blocks routes until /me resolves

  // ── Restore session on app load ───────────────────────────────────────────
  // Cookie is sent automatically — just ask backend who's logged in
  useEffect(() => {
    api.get('/auth/me')
      .then(res => setCurrentUser(res.data))
      .catch(() => setCurrentUser(null))   // 401 = no valid session
      .finally(() => setLoading(false));
  }, []);

  // ── Fetch rides + requests whenever user changes ──────────────────────────
  const fetchRides = async () => {
    try {
      const { data } = await api.get('/rides');
      setRides(data);
    } catch (e) { console.error('fetchRides:', e); }
  };

  const fetchRequests = async () => {
    try {
      const { data } = await api.get('/booking-requests');  // backend gets user from cookie
      setRequests(data);
    } catch (e) { console.error('fetchRequests:', e); }
  };

  useEffect(() => {
    if (!currentUser) {
      setRides([]);
      setRequests([]);
      return;
    }
    fetchRides();
    fetchRequests();
    const interval = setInterval(() => {
      fetchRides();
      fetchRequests();
    }, 10000);
    return () => clearInterval(interval);
  }, [currentUser?.MemberID]);

  // ── Auth ──────────────────────────────────────────────────────────────────

  const loginWithGoogle = async (code: string) => {
    const { data } = await api.post('/auth/login', { code });
    if (!data.isNewUser) {
      setCurrentUser(data.user);  // cookie already set by backend
    }
    return data;
  };

  const registerUser = async (formData: any) => {
    const { data } = await api.post('/auth/signup', formData);
    setCurrentUser(data.user);   // cookie already set by backend
  };

  const logout = async () => {
    await api.post('/auth/logout');  // backend clears the cookie
    setCurrentUser(null);
  };

  // ── Rides ─────────────────────────────────────────────────────────────────

  const addRide = async (rideData: Omit<Ride, 'RideID' | 'HostName' | 'ProfileImageURL' | 'Passengers'>) => {
    try {
      const { data } = await api.post('/rides', rideData);
      setRides(prev => [data, ...prev]);
    } catch (e) { console.error('addRide:', e); }
  };

  const requestToJoin = async (rideId: string) => {
    if (requests.find(r => r.RideID === rideId)) return;
    try {
      const { data } = await api.post('/booking-requests', { RideID: rideId });
      // No need to pass PassengerID — backend gets it from cookie
      setRequests(prev => [...prev, data]);
    } catch (e) { console.error('requestToJoin:', e); }
  };

  const updateRequest = async (requestId: number, status: 'APPROVED' | 'REJECTED') => {
    try {
      await api.patch(`/booking-requests/${requestId}`, { RequestStatus: status });
      await Promise.all([fetchRequests(), fetchRides()]);
    } catch (e) { console.error('updateRequest:', e); }
  };

  const completeRide = async (rideId: string) => {
    try {
      await api.patch(`/rides/${rideId}/status`, { status: 'COMPLETED' });
      await fetchRides();
    } catch (e) { console.error('completeRide:', e); }
  };

  // ── Block render until session check completes ────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <AppContext.Provider value={{
      currentUser,
      rides,
      requests,
      loading,
      loginWithGoogle,
      registerUser,
      logout,
      addRide,
      refreshRides: fetchRides,
      requestToJoin,
      updateRequest,
      completeRide,
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
};