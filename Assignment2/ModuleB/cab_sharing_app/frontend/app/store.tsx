import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// ── Types ────────────────────────────────────────────────────────────────────

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

// Returned by loginWithGoogle when email is not in Members yet
export interface NewUserPayload {
  isNewUser: true;
  email: string;
  name: string;
  picture: string;
}

// ── Context type ─────────────────────────────────────────────────────────────

interface AppContextType {
  currentUser: User | null;
  rides: Ride[];
  requests: BookingRequest[];

  // Auth
  loginWithGoogle: (accessToken: string) => Promise<NewUserPayload | { isNewUser: false }>;
  registerUser: (data: Omit<User, 'MemberID'>) => Promise<void>;
  logout: () => void;

  // Rides
  addRide: (rideData: Omit<Ride, 'RideID' | 'HostName' | 'ProfileImageURL' | 'Passengers'>) => Promise<void>;
  refreshRides: () => Promise<void>;

  // Requests
  requestToJoin: (rideId: string) => Promise<void>;
  updateRequest: (requestId: number, status: 'APPROVED' | 'REJECTED') => Promise<void>;

  // Ride lifecycle
  completeRide: (rideId: string) => Promise<void>;
}

// ── Context ──────────────────────────────────────────────────────────────────

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {

  // Rehydrate user from localStorage on first load
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    try {
      const saved = localStorage.getItem('user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [rides, setRides]       = useState<Ride[]>([]);
  const [requests, setRequests] = useState<BookingRequest[]>([]);

  // ── Persist session ────────────────────────────────────────────────────────
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('user', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('user');
    }
  }, [currentUser]);

  // ── Data fetching ──────────────────────────────────────────────────────────
  const fetchRides = async () => {
    try {
      const res = await fetch('/api/rides');
      if (res.ok) setRides(await res.json());
    } catch (e) { console.error('fetchRides:', e); }
  };

  const fetchRequests = async () => {
    if (!currentUser) return;
    try {
      const res = await fetch(`/api/booking-requests?passengerId=${currentUser.MemberID}`);
      if (res.ok) setRequests(await res.json());
    } catch (e) { console.error('fetchRequests:', e); }
  };

  // Fetch on mount and re-fetch when user logs in/out. Poll every 10s.
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
  }, [currentUser?.MemberID]); // only re-run when actual user identity changes

  // ── Google OAuth login ─────────────────────────────────────────────────────
  // Flow:
  //   1. @react-oauth/google gives us an access_token
  //   2. We send it to POST /api/auth/google { token }
  //   3. Backend calls Google userinfo API to verify and get email/name/picture
  //   4a. Email found in Members → returns { isNewUser: false, ...full User row }
  //   4b. Email not found        → returns { isNewUser: true, email, name, picture }
  //       → caller (Login.tsx) redirects to /signup with that data as router state
  // api.ts (or wherever you define this)
  const loginWithGoogle = async (code: string) => {
    const res = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code }), // Send 'code' to match backend BaseModel
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Google auth failed');
    }

    return await res.json();
  };

  // ── Register new user (called after Signup form) ───────────────────────────
  // POST /api/auth/register → INSERT into Members → returns created row
  const registerUser = async (data: Omit<User, 'MemberID'>) => {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Registration failed');
    const user: User = await res.json();
    setCurrentUser(user);
  };

  // ── Logout ─────────────────────────────────────────────────────────────────
  // Setting currentUser to null triggers the useEffect above to clear localStorage
  // and the data useEffect to clear rides/requests
  const logout = () => setCurrentUser(null);

  // ── Add ride ───────────────────────────────────────────────────────────────
  const addRide = async (rideData: Omit<Ride, 'RideID' | 'HostName' | 'ProfileImageURL' | 'Passengers'>) => {
    try {
      const res = await fetch('/api/rides', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rideData),
      });
      if (!res.ok) throw new Error();
      const newRide: Ride = await res.json();
      setRides(prev => [newRide, ...prev]);
    } catch (e) { console.error('addRide:', e); }
  };

  // ── Request to join ────────────────────────────────────────────────────────
  const requestToJoin = async (rideId: string) => {
    if (!currentUser) return;
    if (requests.find(r => r.RideID === rideId)) return;
    try {
      const res = await fetch('/api/booking-requests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ RideID: rideId, PassengerID: currentUser.MemberID }),
      });
      if (!res.ok) throw new Error();
      const newReq: BookingRequest = await res.json();
      setRequests(prev => [...prev, newReq]);
    } catch (e) { console.error('requestToJoin:', e); }
  };

  // ── Approve / reject a booking request (used by host) ─────────────────────
  const updateRequest = async (requestId: number, status: 'APPROVED' | 'REJECTED') => {
    try {
      await fetch(`/api/booking-requests/${requestId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ RequestStatus: status }),
      });
      await Promise.all([fetchRequests(), fetchRides()]);
    } catch (e) { console.error('updateRequest:', e); }
  };

  // ── Complete ride ──────────────────────────────────────────────────────────
  const completeRide = async (rideId: string) => {
    try {
      await fetch(`/api/rides/${rideId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'COMPLETED' }),
      });
      await fetchRides();
    } catch (e) { console.error('completeRide:', e); }
  };

  return (
    <AppContext.Provider value={{
      currentUser,
      rides,
      requests,
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