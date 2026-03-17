import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store';
import { ChatDrawer } from '../components/ChatDrawer';
import { MapPin, Clock, MessageSquare, ChevronRight, Search, Filter, Car, ChevronDown, ChevronUp } from 'lucide-react';

// ── Types ────────────────────────────────────────────────────────────────────

interface Passenger {
  MemberID: number;
  FullName: string;
}

interface Ride {
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
  Passengers: Passenger[];
}

// ── RideCard ─────────────────────────────────────────────────────────────────

interface RideCardProps {
  ride: Ride;
  requestStatus: string | null;
  currentUserGender: string | null;
  onRequestJoin: (rideId: string) => void;
  onOpenChat: (ride: Ride) => void;
}

const RideCard: React.FC<RideCardProps> = ({
  ride,
  requestStatus,
  currentUserGender,
  onRequestJoin,
  onOpenChat,
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const navigate = useNavigate();

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const dayMonth = date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
    return { time, dayMonth };
  };

  const { time, dayMonth } = formatTime(ride.StartTime);

  const renderRequestButton = () => {
    if (requestStatus === 'PENDING') {
      return (
        <div className="flex items-center justify-center py-4 bg-orange-50 text-orange-500 font-bold rounded-2xl border border-orange-100 text-sm">
          Pending…
        </div>
      );
    }
    if (requestStatus === 'APPROVED') {
      return (
        <div className="flex items-center justify-center py-4 bg-emerald-50 text-emerald-600 font-bold rounded-2xl border border-emerald-100 text-sm">
          ✓ Joined
        </div>
      );
    }
    return (
      <button
        onClick={() => onRequestJoin(ride.RideID)}
        disabled={ride.AvailableSeats === 0}
        className="flex items-center justify-center gap-1 py-4 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-200 disabled:text-slate-400 text-white font-bold rounded-2xl transition-all text-sm active:scale-95"
      >
        Request <ChevronRight className="w-4 h-4" />
      </button>
    );
  };

  return (
    <div className="bg-white rounded-[2rem] p-6 border border-slate-100 shadow-sm hover:shadow-xl hover:border-emerald-100 transition-all flex flex-col">

      {/* Header: host info + seats badge */}
      <div className="flex justify-between items-start mb-5">
        <div className="flex items-center gap-3">
          <img
            src={ride.ProfileImageURL || `https://picsum.photos/seed/${ride.AdminID}/100`}
            className="w-11 h-11 rounded-xl border-2 border-slate-100 object-cover cursor-pointer hover:opacity-80 transition-opacity"
            alt={ride.HostName}
            onClick={() => navigate(`/profile/${ride.AdminID}`)}
          />
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Host</p>
            <p
              className="font-bold text-slate-800 text-sm cursor-pointer hover:text-emerald-600 transition-colors"
              onClick={() => navigate(`/profile/${ride.AdminID}`)}
            >
              {ride.HostName}
            </p>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1.5">
          <span className="px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs font-bold border border-emerald-100">
            {ride.AvailableSeats} seats left
          </span>
          {/* Female Only badge — only shown to female users */}
          {ride.FemaleOnly && currentUserGender === 'F' && (
            <span className="px-3 py-1 bg-pink-50 text-pink-500 rounded-full text-xs font-bold border border-pink-100">
              ♀ Female Only
            </span>
          )}
        </div>
      </div>

      {/* Route timeline */}
      <div className="flex mb-4 flex-1">
        <div className="flex flex-col items-center mr-3 mt-1">
          <div className="w-3 h-3 rounded-full bg-slate-200 flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
          </div>
          <div className="w-0.5 h-7 bg-slate-100 my-0.5" />
          <div className="w-4 h-4 rounded-full bg-emerald-100 flex items-center justify-center">
            <MapPin className="w-2.5 h-2.5 text-emerald-500" />
          </div>
        </div>
        <div className="flex flex-col justify-between py-0.5">
          <p className="text-sm text-slate-600 font-medium line-clamp-1">{ride.Source}</p>
          <p className="text-sm font-bold text-slate-900 line-clamp-1">{ride.Destination}</p>
        </div>
      </div>

      {/* Time row */}
      <div className="flex items-center gap-2 py-3 border-y border-slate-50 mb-4">
        <Clock className="w-4 h-4 text-slate-400" />
        <span className="text-sm text-slate-600 font-medium">{time}</span>
        <span className="text-xs text-slate-400">({dayMonth})</span>
      </div>

      {/* Action buttons */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <button
          onClick={() => onOpenChat(ride)}
          className="flex items-center justify-center gap-2 py-3.5 bg-slate-50 hover:bg-slate-100 text-slate-700 font-bold rounded-2xl transition-all text-sm"
        >
          <MessageSquare className="w-4 h-4" /> Chat
        </button>
        {renderRequestButton()}
      </div>

      {/* More details toggle */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center justify-center gap-1 text-xs text-slate-400 hover:text-slate-600 transition-colors py-1"
      >
        {showDetails ? (
          <><ChevronUp className="w-3.5 h-3.5" /> Hide details</>
        ) : (
          <><ChevronDown className="w-3.5 h-3.5" /> More details</>
        )}
      </button>

      {/* Collapsible details */}
      {showDetails && (
        <div className="mt-3 p-4 bg-slate-50 rounded-2xl space-y-2.5 text-sm border border-slate-100">
          <div className="flex justify-between">
            <span className="text-slate-500">Vehicle</span>
            <span className="font-semibold text-slate-700">{ride.VehicleType}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Est. Duration</span>
            <span className="font-semibold text-slate-700">{ride.EstimatedTime} mins</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Total Passengers</span>
            <span className="font-semibold text-slate-700">{ride.PassengerCount}</span>
          </div>

          {/* Passenger list with clickable names */}
          {ride.Passengers && ride.Passengers.length > 0 && (
            <div className="pt-2 border-t border-slate-200">
              <p className="text-slate-500 mb-2">Passengers</p>
              <div className="flex flex-wrap gap-1.5">
                {ride.Passengers.map(p => (
                  <span
                    key={p.MemberID}
                    onClick={() => navigate(`/profile/${p.MemberID}`)}
                    className="px-2.5 py-1 bg-white border border-slate-200 rounded-full text-xs font-medium text-slate-700 cursor-pointer hover:border-emerald-300 hover:text-emerald-600 transition-colors"
                  >
                    {p.FullName}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Female only — shown only to female users */}
          {ride.FemaleOnly && currentUserGender === 'F' && (
            <div className="flex justify-between pt-2 border-t border-slate-200">
              <span className="text-pink-500 font-bold">♀ Female Only Ride</span>
              <span className="text-slate-400 text-xs">Safety Policy</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ── AvailableRides Page ───────────────────────────────────────────────────────

export const AvailableRides: React.FC = () => {
  const { currentUser } = useApp();
  const [allRides, setAllRides]         = useState<Ride[]>([]);
  const [loading, setLoading]           = useState(true);
  const [selectedRide, setSelectedRide] = useState<Ride | null>(null);
  const [requestStatuses, setRequestStatuses] = useState<Record<string, string>>({});

  // Filter state (all client-side — no extra DB calls)
  const [filterSource, setFilterSource] = useState('');
  const [filterDest, setFilterDest]     = useState('');
  const [filterTime, setFilterTime]     = useState('');

  // ── Load rides + my request statuses once ───────────────────────────────
  useEffect(() => {
    const load = async () => {
      try {
        const [ridesRes, reqRes] = await Promise.all([
          fetch('/api/rides'),
          fetch(`/api/booking-requests?passengerId=${currentUser?.MemberID}`),
        ]);
        const ridesData: Ride[] = await ridesRes.json();
        const reqData: { RideID: string; RequestStatus: string }[] = await reqRes.json();

        // Exclude rides the current user created
        setAllRides(ridesData.filter(r => r.AdminID !== currentUser?.MemberID));

        // Build lookup map: { RideID → RequestStatus }
        const map: Record<string, string> = {};
        reqData.forEach(r => { map[r.RideID] = r.RequestStatus; });
        setRequestStatuses(map);
      } catch (err) {
        console.error('Failed to load rides:', err);
      } finally {
        setLoading(false);
      }
    };
    if (currentUser?.MemberID) load();
  }, [currentUser]);

  // ── Client-side filtering ────────────────────────────────────────────────
  const filteredRides = allRides.filter(r => {
    const srcMatch  = r.Source.toLowerCase().includes(filterSource.toLowerCase());
    const dstMatch  = r.Destination.toLowerCase().includes(filterDest.toLowerCase());
    const timeMatch = !filterTime || new Date(r.StartTime) >= new Date(filterTime);
    // If the ride is FemaleOnly, only show it to female users
    const genderMatch = !r.FemaleOnly || currentUser?.Gender === 'F';
    return srcMatch && dstMatch && timeMatch && genderMatch;
  });

  // ── Join request → POST /api/booking-requests ────────────────────────────
  const handleRequestJoin = async (rideId: string) => {
    setRequestStatuses(prev => ({ ...prev, [rideId]: 'PENDING' }));
    try {
      const res = await fetch('/api/booking-requests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ RideID: rideId, PassengerID: currentUser?.MemberID }),
      });
      if (!res.ok) throw new Error();
    } catch {
      setRequestStatuses(prev => ({ ...prev, [rideId]: '' }));
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-7xl mx-auto px-4 md:px-10 py-8">

      {/* Page header + filters */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
        <div>
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Available Rides</h1>
          <p className="text-slate-500 mt-1 text-lg">Find students traveling on your route</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Source filter */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="From…"
              value={filterSource}
              onChange={e => setFilterSource(e.target.value)}
              className="pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm w-44 shadow-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            />
          </div>

          {/* Destination filter */}
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="To…"
              value={filterDest}
              onChange={e => setFilterDest(e.target.value)}
              className="pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm w-44 shadow-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            />
          </div>

          {/* Time filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="datetime-local"
              value={filterTime}
              onChange={e => setFilterTime(e.target.value)}
              className="pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm shadow-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            />
          </div>
        </div>
      </div>

      {/* Body */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-500">Loading rides…</p>
        </div>
      ) : filteredRides.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
          <div className="bg-slate-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-5">
            <Car className="w-10 h-10 text-slate-400" />
          </div>
          <h3 className="text-xl font-bold text-slate-800">No rides found</h3>
          <p className="text-slate-500 mt-2 text-sm">Try adjusting your filters or publish your own ride!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRides.map(ride => (
            <RideCard
              key={ride.RideID}
              ride={ride}
              requestStatus={requestStatuses[ride.RideID] ?? null}
              currentUserGender={currentUser?.Gender ?? null}
              onRequestJoin={handleRequestJoin}
              onOpenChat={setSelectedRide}
            />
          ))}
        </div>
      )}

      {selectedRide && (
        <ChatDrawer
          ride={selectedRide}
          onClose={() => setSelectedRide(null)}
        />
      )}
    </div>
  );
};