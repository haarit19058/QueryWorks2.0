// src/pages/AdminPage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store';
import api from '../lib/api';
import { ShieldCheck, Users, Car, MessageSquare, Truck, Trash2, PlusCircle } from 'lucide-react';

// ── Types ─────────────────────────────────────────────────────────────────────

interface AdminMember  { MemberID: number; FullName: string; Email: string; }
interface MemberRow    { MemberID: number; Name: string; Email: string; Programme: string; BatchYear: number; Gender: string; }
interface FeedbackRow  { RideID: string; MemberID: number; Feedback: string; Category: string; SubmittedAt: string; }
interface VehicleRow   { VehicleID: number; Type: string; Capacity: number; }
interface RideRow      { RideID: string; Source: string; Destination: string; AdminID: number; HostName: string; AvailableSeats: number; StartTime: string; }

type Tab = 'admins' | 'members' | 'rides' | 'feedback' | 'vehicles';

// ── Component ─────────────────────────────────────────────────────────────────

export const AdminPage: React.FC = () => {
  const { currentUser } = useApp();
  const navigate = useNavigate();
  const memberId = currentUser?.MemberID;

  const [activeTab, setActiveTab]       = useState<Tab>('admins');
  const [admins, setAdmins]             = useState<AdminMember[]>([]);
  const [members, setMembers]           = useState<MemberRow[]>([]);
  const [rides, setRides]               = useState<RideRow[]>([]);
  const [feedbacks, setFeedbacks]       = useState<FeedbackRow[]>([]);
  const [vehicles, setVehicles]         = useState<VehicleRow[]>([]);
  const [toast, setToast]               = useState('');

  // Add admin form
  const [newAdminEmail, setNewAdminEmail] = useState('');
  // Add vehicle form
  const [vehicleType, setVehicleType]   = useState('');
  const [vehicleCapacity, setVehicleCapacity] = useState('');

  // ── Helpers ────────────────────────────────────────────────────────────────

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  const p = (extra = {}) => ({ params: { member_id: memberId, ...extra } });

  // ── Data fetchers ──────────────────────────────────────────────────────────

  const fetchAdmins   = () => api.get('/admin/current-admins', p()).then(r => setAdmins(r.data));
  const fetchMembers  = () => api.get('/admin/see-member-table', p()).then(r => setMembers(r.data));
  const fetchRides    = () => api.get('/rides', p()).then(r => setRides(r.data));
  const fetchFeedback = () => api.get('/admin/ridefeedback-table', p()).then(r => setFeedbacks(r.data));
  const fetchVehicles = () => api.get('/admin/see-vehicle', p()).then(r => setVehicles(r.data));

  useEffect(() => {
    if (!memberId) return;
    fetchAdmins();
    fetchMembers();
    fetchRides();
    fetchFeedback();
    fetchVehicles();
  }, [memberId]);

  // ── Actions ────────────────────────────────────────────────────────────────

  const handleAddAdmin = async () => {
    try {
      const res = await api.post('/admin/add-admin', null, p({ email: newAdminEmail }));
      showToast(res.data.msg);
      setNewAdminEmail('');
      fetchAdmins();
    } catch (e: any) { showToast(e.response?.data?.detail || 'Error adding admin'); }
  };

  const handleRemoveRide = async (rideId: string) => {
    if (!confirm(`Remove ride ${rideId}?`)) return;
    try {
      await api.post('/admin/remove-ride', null, p({ ride_id: rideId }));
      showToast('Ride removed');
      fetchRides();
    } catch (e: any) { showToast(e.response?.data?.detail || 'Error removing ride'); }
  };

  const handleAddVehicle = async () => {
    try {
      const res = await api.post('/admin/add-vehicle', null, p({
        vehicle_type: vehicleType,
        max_capacity: Number(vehicleCapacity),
      }));
      showToast(res.data.msg);
      setVehicleType('');
      setVehicleCapacity('');
      fetchVehicles();
    } catch (e: any) { showToast(e.response?.data?.detail || 'Error adding vehicle'); }
  };

  // ── Tab config ─────────────────────────────────────────────────────────────

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'admins',   label: 'Admins',    icon: <ShieldCheck className="w-4 h-4" /> },
    { id: 'members',  label: 'Members',   icon: <Users className="w-4 h-4" /> },
    { id: 'rides',    label: 'Rides',     icon: <Car className="w-4 h-4" /> },
    { id: 'feedback', label: 'Feedback',  icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'vehicles', label: 'Vehicles',  icon: <Truck className="w-4 h-4" /> },
  ];

  // ── UI ─────────────────────────────────────────────────────────────────────

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="bg-emerald-500 p-2 rounded-lg">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-black">Admin Panel</h1>
      </div>

      {/* Toast */}
      {toast && (
        <div className="fixed top-6 right-6 z-50 bg-emerald-600 text-white px-5 py-3 rounded-xl shadow-lg animate-fade-in">
          {toast}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 flex-wrap border-b border-slate-700 pb-1">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg font-medium text-sm transition-colors
              ${activeTab === t.id
                ? 'bg-slate-800 text-emerald-400 border border-b-0 border-slate-700'
                : 'text-slate-400 hover:text-black'}`}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* ── Admins Tab ─────────────────────────────────────────────────────── */}
      {activeTab === 'admins' && (
        <div className="space-y-6">
          <div className="glass p-6 rounded-xl">
            <h2 className="text-lg font-semibold text-emerald-400 mb-4">Current Admins</h2>
            <ul className="divide-y divide-slate-700">
              {admins.map(a => (
                <li key={a.MemberID} className="py-3 flex justify-between items-center">
                  <span className="text-white font-medium">{a.FullName}</span>
                  <span className="text-slate-400 text-sm">{a.Email}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="glass p-6 rounded-xl">
            <h2 className="text-lg font-semibold text-emerald-400 mb-4">Add New Admin</h2>
            <div className="flex gap-3">
              <input
                type="email"
                placeholder="member@iitgn.ac.in"
                value={newAdminEmail}
                onChange={e => setNewAdminEmail(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAddAdmin()}
                className="flex-1 bg-slate-800 text-white px-4 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-emerald-500"
              />
              <button
                onClick={handleAddAdmin}
                className="px-6 py-2 bg-emerald-500 hover:bg-emerald-400 text-white font-bold rounded-lg transition-all flex items-center gap-2"
              >
                <PlusCircle className="w-4 h-4" /> Add
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Members Tab ────────────────────────────────────────────────────── */}
      {activeTab === 'members' && (
        <div className="glass p-6 rounded-xl overflow-x-auto">
          <h2 className="text-lg font-semibold text-emerald-400 mb-4">All Members ({members.length})</h2>
          <table className="w-full text-sm text-slate-300">
            <thead>
              <tr className="text-left border-b border-slate-700 text-slate-500 uppercase text-xs tracking-wider">
                <th className="py-3 pr-4">ID</th>
                <th className="py-3 pr-4">Name</th>
                <th className="py-3 pr-4">Email</th>
                <th className="py-3 pr-4">Programme</th>
                <th className="py-3 pr-4">Batch</th>
                <th className="py-3">Gender</th>
              </tr>
            </thead>
            <tbody>
              {members.map(m => (
                <tr
                  key={m.MemberID}
                  onClick={() => navigate(`/profile/${m.MemberID}`)}
                  className="border-b border-slate-800 hover:bg-slate-700/50 cursor-pointer transition-colors"
                >
                  <td className="py-3 pr-4 text-slate-500">{m.MemberID}</td>
                  <td className="py-3 pr-4 text-white font-medium">{m.Name}</td>
                  <td className="py-3 pr-4">{m.Email}</td>
                  <td className="py-3 pr-4">{m.Programme}</td>
                  <td className="py-3 pr-4">{m.BatchYear}</td>
                  <td className="py-3">{m.Gender}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Rides Tab ──────────────────────────────────────────────────────── */}
      {activeTab === 'rides' && (
        <div className="glass p-6 rounded-xl overflow-x-auto">
          <h2 className="text-lg font-semibold text-emerald-400 mb-4">All Rides ({rides.length})</h2>
          <table className="w-full text-sm text-slate-300">
            <thead>
              <tr className="text-left border-b border-slate-700 text-slate-500 uppercase text-xs tracking-wider">
                <th className="py-3 pr-4">Ride ID</th>
                <th className="py-3 pr-4">Host</th>
                <th className="py-3 pr-4">From</th>
                <th className="py-3 pr-4">To</th>
                <th className="py-3 pr-4">Seats Left</th>
                <th className="py-3 pr-4">Start Time</th>
                <th className="py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {rides.map(r => (
                <tr key={r.RideID} className="border-b border-slate-800 hover:bg-slate-800/40">
                  <td className="py-3 pr-4 text-slate-500 font-mono text-xs">{r.RideID.slice(0, 8)}…</td>
                  <td className="py-3 pr-4 text-white">{r.HostName}</td>
                  <td className="py-3 pr-4">{r.Source}</td>
                  <td className="py-3 pr-4">{r.Destination}</td>
                  <td className="py-3 pr-4">{r.AvailableSeats}</td>
                  <td className="py-3 pr-4">{new Date(r.StartTime).toLocaleString()}</td>
                  <td className="py-3">
                    <button
                      onClick={() => handleRemoveRide(r.RideID)}
                      className="flex items-center gap-1 px-3 py-1 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-lg text-xs transition-colors"
                    >
                      <Trash2 className="w-3 h-3" /> Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Feedback Tab ───────────────────────────────────────────────────── */}
      {activeTab === 'feedback' && (
        <div className="glass p-6 rounded-xl overflow-x-auto">
          <h2 className="text-lg font-semibold text-emerald-400 mb-4">Ride Feedback ({feedbacks.length})</h2>
          <table className="w-full text-sm text-slate-300">
            <thead>
              <tr className="text-left border-b border-slate-700 text-slate-500 uppercase text-xs tracking-wider">
                <th className="py-3 pr-4">Ride ID</th>
                <th className="py-3 pr-4">Member ID</th>
                <th className="py-3 pr-4">Category</th>
                <th className="py-3 pr-4">Feedback</th>
                <th className="py-3">Submitted</th>
              </tr>
            </thead>
            <tbody>
              {feedbacks.map((f, i) => (
                <tr key={i} className="border-b border-slate-800 hover:bg-slate-800/40">
                  <td className="py-3 pr-4 font-mono text-xs text-slate-500">{f.RideID.slice(0, 8)}…</td>
                  <td
                    className="py-3 pr-4 text-emerald-400 cursor-pointer hover:underline"
                    onClick={() => navigate(`/profile/${f.MemberID}`)} 
                  >
                    #{f.MemberID}
                  </td>
                  <td className="py-3 pr-4">
                    <span className="px-2 py-0.5 bg-slate-700 rounded-full text-xs">{f.Category}</span>
                  </td>
                  <td className="py-3 pr-4 max-w-xs truncate">{f.Feedback}</td>
                  <td className="py-3 text-slate-500">{new Date(f.SubmittedAt).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Vehicles Tab ───────────────────────────────────────────────────── */}
      {activeTab === 'vehicles' && (
        <div className="space-y-6">
          <div className="glass p-6 rounded-xl overflow-x-auto">
            <h2 className="text-lg font-semibold text-emerald-400 mb-4">Registered Vehicles ({vehicles.length})</h2>
            <table className="w-full text-sm text-slate-300">
              <thead>
                <tr className="text-left border-b border-slate-700 text-slate-500 uppercase text-xs tracking-wider">
                  <th className="py-3 pr-4">ID</th>
                  <th className="py-3 pr-4">Type</th>
                  <th className="py-3">Capacity</th>
                </tr>
              </thead>
              <tbody>
                {vehicles.map(v => (
                  <tr key={v.VehicleID} className="border-b border-slate-800 hover:bg-slate-800/40">
                    <td className="py-3 pr-4 text-slate-500">{v.VehicleID}</td>
                    <td className="py-3 pr-4 text-white font-medium">{v.Type}</td>
                    <td className="py-3">{v.Capacity} seats</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="glass p-6 rounded-xl">
            <h2 className="text-lg font-semibold text-emerald-400 mb-4">Add Vehicle</h2>
            <div className="flex gap-3 flex-wrap">
              <input
                type="text"
                placeholder="Vehicle type (e.g. SUV)"
                value={vehicleType}
                onChange={e => setVehicleType(e.target.value)}
                className="flex-1 min-w-[180px] bg-slate-800 text-white px-4 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-emerald-500"
              />
              <input
                type="number"
                placeholder="Max capacity"
                value={vehicleCapacity}
                onChange={e => setVehicleCapacity(e.target.value)}
                className="w-36 bg-slate-800 text-white px-4 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-emerald-500"
              />
              <button
                onClick={handleAddVehicle}
                disabled={!vehicleType || !vehicleCapacity}
                className="px-6 py-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold rounded-lg transition-all flex items-center gap-2"
              >
                <PlusCircle className="w-4 h-4" /> Add
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};