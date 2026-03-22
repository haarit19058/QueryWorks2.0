import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store';
import { Check, X, Clock, MapPin, Users, Car } from 'lucide-react';


// ── Main component ────────────────────────────────────────────────────────────
export const YourRides: React.FC = () => {
  const { rides, myRequests, pendingRequests, currentUser, updateRequest, completeRide, cancelRide } = useApp();
  const navigate = useNavigate();
  const [completingRide, setCompletingRide] = useState<string | null>(null);
  const [price, setPrice] = useState('');
  const [platform, setPlatform] = useState('');
  const [cancellingRide, setCancellingRide] = useState<string | null>(null);
  const [cancelReason, setCancelReason] = useState('');

  const myHostedRides = rides.filter(r => r.AdminID === currentUser?.MemberID);
  const myJoinedRequests = myRequests.filter(r => r.PassengerID === currentUser?.MemberID);

  const statusStyle = (status: string) => {
    if (status === 'APPROVED') return 'bg-emerald-50 text-emerald-600 border-emerald-100';
    if (status === 'REJECTED') return 'bg-red-50 text-red-500 border-red-100';
    return 'bg-orange-50 text-orange-500 border-orange-100';
  };

  return (
    <div className="max-w-5xl mx-auto p-6 md:p-10 space-y-16">

      {/* ── Hosting Section ─────────────────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center">
            <Car className="text-white w-5 h-5" />
          </div>
          <h2 className="text-3xl font-extrabold text-slate-900">Rides You're Hosting</h2>
        </div>

        {myHostedRides.length === 0 ? (
          <div className="bg-white rounded-3xl p-12 text-center border border-slate-100">
            <p className="text-slate-500 font-medium">You aren't hosting any rides currently.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {myHostedRides.map(ride => {
              const ridePassengers = ride.Passengers ?? [];;

              return (
                <div key={ride.RideID} className="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm">

                  {/* Card header */}
                  <div className={`p-6 md:p-8 text-white flex flex-col md:flex-row justify-between gap-4 bg-slate-900`}>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-white/60 text-xs font-bold uppercase tracking-widest">
                        <Clock className="w-3 h-3" />
                        {new Date(ride.StartTime).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                      </div>
                      <h3 className="text-xl font-bold flex items-center gap-3">
                        {ride.Source.split(',')[0]}
                        <span className="text-white/40">→</span>
                        {ride.Destination.split(',')[0]}
                      </h3>
                    </div>

                    <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-xl self-start">
                      <Users className="w-4 h-4" />
                      <span className="text-sm font-bold">
                        {ride.PassengerCount} / {ride.AvailableSeats} passengers
                      </span>
                    </div>

                    {completingRide === ride.RideID ? (
                      <div className="flex flex-col gap-2 self-start md:self-center min-w-[200px]">
                        <input
                          type="number"
                          placeholder="Price (₹)"
                          value={price}
                          onChange={e => setPrice(e.target.value)}
                          className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/30"
                        />
                        <input
                          type="text"
                          placeholder="Platform (e.g. Ola, Uber)"
                          value={platform}
                          onChange={e => setPlatform(e.target.value)}
                          className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/30"
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => {
                              setCompletingRide(null);
                              setPrice('');
                              setPlatform('');
                            }}
                            className="flex-1 px-3 py-2 bg-white/10 hover:bg-white/20 text-white text-xs font-bold rounded-xl border border-white/20 transition-all"
                          >
                            Cancel
                          </button>
                          <button
                            disabled={!price || !platform}
                            onClick={async () => {
                              await completeRide(ride.RideID, Number(price), platform);
                              setCompletingRide(null);
                              setPrice('');
                              setPlatform('');
                            }}
                            className="flex-1 px-3 py-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl transition-all"
                          >
                            Confirm
                          </button>
                        </div>
                      </div>
                    ) : cancellingRide === ride.RideID ? (
                      <div className="flex flex-col gap-2 self-start md:self-center min-w-[200px]">
                        <textarea
                          placeholder="Reason for cancellation…"
                          value={cancelReason}
                          onChange={e => setCancelReason(e.target.value)}
                          rows={2}
                          className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-white text-xs placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/30 resize-none"
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => { setCancellingRide(null); setCancelReason(''); }}
                            className="flex-1 px-3 py-2 bg-white/10 hover:bg-white/20 text-white text-xs font-bold rounded-xl border border-white/20 transition-all"
                          >
                            Back
                          </button>
                          <button
                            disabled={!cancelReason.trim()}
                            onClick={async () => {
                              await cancelRide(ride.RideID, cancelReason);
                              setCancellingRide(null);
                              setCancelReason('');
                            }}
                            className="flex-1 px-3 py-2 bg-red-500 hover:bg-red-400 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl transition-all"
                          >
                            Confirm
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex gap-2 self-start md:self-center">
                        <button
                          onClick={() => setCompletingRide(ride.RideID)}
                          className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-emerald-500/20"
                        >
                          Mark as Completed
                        </button>
                        <button
                          onClick={() => setCancellingRide(ride.RideID)}
                          className="px-4 py-2 bg-red-500/80 hover:bg-red-500 text-white text-xs font-bold rounded-xl transition-all"
                        >
                          Cancel Ride
                        </button>
                      </div>
                    )
                    }
                  </div>

                  {/* Passengers + Pending requests (unchanged) */}
                  <div className="p-6 md:p-8 space-y-8">
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
                        Confirmed Passengers ({ridePassengers.length})
                      </h4>
                      {ridePassengers.length === 0 ? (
                        <p className="text-slate-400 text-sm italic">No confirmed passengers yet.</p>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {ridePassengers.map(passenger => (
                            <div
                              key={passenger.MemberID}
                              className="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-100 cursor-pointer"
                              onClick={() => navigate(`/profile/${passenger.MemberID}`)}
                            >
                              <img
                                src={passenger.ProfileImageUrl}
                                className="w-10 h-10 rounded-full bg-white shadow-sm object-cover"
                                alt={passenger.FullName}
                              />
                              <div>
                                <p className="font-bold text-slate-800 hover:text-emerald-600 transition-colors">
                                  {passenger.FullName}
                                </p>
                                <p className="text-[10px] text-emerald-500 font-semibold uppercase tracking-wider">
                                  Confirmed
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {(() => {
                      const ridePendingRequests = pendingRequests.filter(r => r.RideID === ride.RideID);
                      return (
                        <div>
                          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
                            Pending Requests ({ridePendingRequests.length})
                          </h4>
                          {ridePendingRequests.length === 0 ? (
                            <p className="text-slate-400 text-sm italic">No pending requests.</p>
                          ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {ridePendingRequests.map(req => (
                                <div
                                  key={req.RequestID}
                                  className="flex items-center justify-between p-4 bg-orange-50 rounded-2xl border border-orange-100"
                                >
                                  <div
                                    className="flex items-center gap-3 cursor-pointer"
                                    onClick={() => navigate(`/profile/${req.PassengerID}`)}
                                  >
                                    <img
                                      src={`https://picsum.photos/seed/${req.PassengerID}/60`}
                                      className="w-10 h-10 rounded-full bg-white shadow-sm object-cover"
                                      alt={req.PassengerName}
                                    />
                                    <div>
                                      <p className="font-bold text-slate-800 hover:text-emerald-600 transition-colors">
                                        {req.PassengerName ?? `Member #${req.PassengerID}`}
                                      </p>
                                      <p className="text-[10px] text-orange-500 font-semibold uppercase tracking-wider">
                                        Awaiting Approval
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex gap-2">
                                    <button
                                      onClick={() => updateRequest(req.RequestID, 'REJECTED')}
                                      className="p-2 bg-white text-red-500 hover:bg-red-50 rounded-xl transition-colors border border-slate-100"
                                    >
                                      <X className="w-5 h-5" />
                                    </button>
                                    <button
                                      onClick={() => updateRequest(req.RequestID, 'APPROVED')}
                                      className="p-2 bg-emerald-500 text-white hover:bg-emerald-600 rounded-xl transition-all"
                                    >
                                      <Check className="w-5 h-5" />
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* ── Joined Section ──────────────────────────────────────────────── */}
      <section>
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center">
            <Users className="text-white w-5 h-5" />
          </div>
          <h2 className="text-3xl font-extrabold text-slate-900">Rides You've Joined</h2>
        </div>

        {myJoinedRequests.length === 0 ? (
          <div className="bg-white rounded-3xl p-12 text-center border border-slate-100">
            <p className="text-slate-500 font-medium">You haven't requested to join any rides yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {myJoinedRequests.map(req => {
              const ride = rides.find(r => r.RideID === req.RideID);
              if (!ride) return null;

              return (
                <div key={req.RequestID} className="flex flex-col gap-3">

                  {/* Ride card */}
                  <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col justify-between gap-4">
                    <div className="flex justify-between items-start">
                      <span className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase border ${statusStyle(req.RequestStatus)}`}>
                        {req.RequestStatus}
                      </span>
                      <span className="text-[10px] font-bold text-slate-300 uppercase">
                        #{req.RequestID}
                      </span>
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm font-medium text-slate-500">
                        {new Date(ride.StartTime).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                      </p>
                      <h3 className="font-bold text-slate-900 leading-tight">
                        {ride.Source.split(',')[0]}
                        <span className="text-slate-400 mx-2">→</span>
                        {ride.Destination.split(',')[0]}
                      </h3>
                      <div className="flex items-center gap-1.5 text-xs font-medium text-slate-400 pt-1">
                        <MapPin className="w-3 h-3" /> {ride.Source}
                      </div>
                    </div>

                    <div
                      className="flex items-center gap-2 pt-3 border-t border-slate-50 cursor-pointer group"
                      onClick={() => navigate(`/profile/${ride.AdminID}`)}
                    >
                      <img
                        src={ride.ProfileImageURL || `https://picsum.photos/seed/${ride.AdminID}/60`}
                        className="w-7 h-7 rounded-full object-cover border border-slate-100"
                        alt={ride.HostName}
                      />
                      <span className="text-xs text-slate-500 group-hover:text-emerald-600 transition-colors">
                        Hosted by <strong>{ride.HostName}</strong>
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

    </div>
  );
};