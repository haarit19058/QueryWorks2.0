import React from 'react';
import { useApp } from '../store';
import { Clock, Users, History, CheckCircle2, Car } from 'lucide-react';

export const RideHistory: React.FC = () => {
  const { rideHistory, currentUser } = useApp();

  const sorted = [...rideHistory].sort(
    (a, b) => new Date(b.RideDate).getTime() - new Date(a.RideDate).getTime()
  );

  return (
    <div className="max-w-5xl mx-auto p-6 md:p-10 space-y-12">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-12 h-12 rounded-2xl bg-slate-900 flex items-center justify-center shadow-xl shadow-slate-200">
          <History className="text-white w-6 h-6" />
        </div>
        <div>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Ride History</h2>
          <p className="text-slate-500 font-medium">Your past journeys and completed carpools</p>
        </div>
      </div>

      {sorted.length === 0 ? (
        <div className="bg-white rounded-3xl p-16 text-center border border-slate-100 shadow-sm">
          <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <History className="text-slate-300 w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">No history yet</h3>
          <p className="text-slate-500 max-w-xs mx-auto">Completed rides will appear here once they're finished.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {sorted.map(ride => (
            <div
              key={ride.RideID}
              className="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col md:flex-row">

                {/* ── Left: route info ── */}
                <div className="p-6 md:p-8 md:w-2/3 space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-widest">
                      <Clock className="w-3 h-3" />
                      {new Date(ride.RideDate).toLocaleDateString([], { dateStyle: 'medium' })}
                      {' · '}
                      {ride.StartTime.slice(0, 5)}  {/* "HH:MM" from TIME column */}
                    </div>
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-[10px] font-bold uppercase tracking-wider">
                      <CheckCircle2 className="w-3 h-3" /> Completed
                    </div>
                  </div>

                  {/* Route */}
                  <div className="relative pl-6 space-y-6">
                    <div className="absolute left-1.5 top-1.5 bottom-1.5 w-0.5 bg-slate-100" />
                    <div className="relative">
                      <div className="absolute -left-[22px] top-1 w-3 h-3 rounded-full border-2 border-emerald-500 bg-white" />
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-tighter mb-1">From</p>
                      <p className="font-bold text-slate-900">{ride.Source.split(',')[0]}</p>
                    </div>
                    <div className="relative">
                      <div className="absolute -left-[22px] top-1 w-3 h-3 rounded-full border-2 border-slate-900 bg-white" />
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-tighter mb-1">To</p>
                      <p className="font-bold text-slate-900">{ride.Destination.split(',')[0]}</p>
                    </div>
                  </div>

                  {/* Passenger avatars */}
                  {ride.Passengers.length > 0 && (
                    <div>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">
                        Passengers ({ride.Passengers.length})
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {ride.Passengers.map(p => (
                          <div key={p.MemberID} className="flex items-center gap-1.5 bg-slate-50 border border-slate-100 rounded-full px-2.5 py-1">
                            <img
                              src={`https://picsum.photos/seed/${p.MemberID}/40`}
                              className="w-5 h-5 rounded-full object-cover"
                              alt={p.FullName}
                            />
                            <span className="text-xs font-semibold text-slate-700">{p.FullName.split(' ')[0]}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* ── Right: meta ── */}
                <div className="bg-slate-50 p-6 md:p-8 md:w-1/3 flex flex-col justify-center border-t md:border-t-0 md:border-l border-slate-100 space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 font-medium">Your Role</span>
                    <span className={`font-bold ${ride.Role === 'HOST' ? 'text-emerald-600' : 'text-slate-900'}`}>
                      {ride.Role === 'HOST' ? 'Host' : 'Passenger'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 font-medium">Vehicle</span>
                    <div className="flex items-center gap-1.5 font-bold text-slate-900">
                      <Car className="w-3.5 h-3.5 text-slate-400" />
                      {ride.Platform}
                    </div>
                  </div>

                  {ride.Price != null && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500 font-medium">Price</span>
                      <span className="font-bold text-slate-900">₹{ride.Price}</span>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 font-medium">Seats taken</span>
                    <div className="flex items-center gap-1.5 font-bold text-slate-900">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      {ride.Passengers.length}
                    </div>
                  </div>
                </div>

              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};