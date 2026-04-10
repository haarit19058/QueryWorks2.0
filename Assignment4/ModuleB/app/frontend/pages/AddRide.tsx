import { useState, useRef } from 'react';
import { Autocomplete } from '../components/Autocomplete';
import { MapComponent } from '../components/MapComponent';
import { useApp } from '../store';
import { GeoLocation } from '../types';
import { Users, Clock, ArrowRight, CheckCircle, Calendar } from 'lucide-react';
import api from '../lib/api'; // <-- IMPORT AXIOS INSTANCE

interface AddRideProps {
  onSuccess: () => void;
}

export const AddRide: React.FC<AddRideProps> = ({ onSuccess }) => {
  const { addRide, currentUser } = useApp();
  const [source, setSource] = useState<GeoLocation | null>(null);
  const [destination, setDestination] = useState<GeoLocation | null>(null);
  const [time, setTime] = useState('');
  const [seats, setSeats] = useState(3);
  const [femaleOnly, setFemaleOnly] = useState(false);
  const [estimatedTime, setEstimatedTime] = useState('');
  const [vehicleType, setVehicleType] = useState('Car');
  const [published, setPublished] = useState(false);
  const timeInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser || !source || !destination || !time || !estimatedTime) return;

    try {
      // <-- USE API.POST INSTEAD OF FETCH
      await api.post('/rides', {
        AdminID: currentUser.MemberID,
        Source: source.display_name,
        Destination: destination.display_name,
        StartTime: time,
        AvailableSeats: seats,
        VehicleType: vehicleType,
        FemaleOnly: femaleOnly,
        EstimatedTime: Number(estimatedTime),
      });

      setPublished(true);
      setTimeout(onSuccess, 2000);
    } catch (error) {
      console.error("Failed to publish ride", error);
    }
  };

  const handleTimeClick = () => {
    if (timeInputRef.current) {
      try {
        (timeInputRef.current as any).showPicker?.();
      } catch (err) {
        timeInputRef.current.focus();
      }
    }
  };

  if (published) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-80px)] text-center p-6">
        <div className="bg-emerald-100 p-6 rounded-full mb-6">
          <CheckCircle className="w-20 h-20 text-emerald-500" />
        </div>
        <h2 className="text-3xl font-bold text-slate-800">Ride Published!</h2>
        <p className="text-slate-500 mt-2 max-w-sm">Students can now see your ride and request to join. Redirecting you to available rides...</p>
      </div>
    );
  }

  console.log(currentUser.Gender);

  return (
    <div className="flex flex-col md:flex-row h-[calc(100vh-80px)] overflow-hidden">
      {/* Form Sidebar */}
      <div className="w-full md:w-[450px] bg-white border-r border-slate-200 overflow-y-auto shadow-2xl z-10">
        <div className="p-8">
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Publish a Ride</h2>
          <p className="text-slate-500 text-sm mb-8">Share your commute and split the fare!</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <label className="block text-sm font-semibold text-slate-700">Route Details</label>
              <Autocomplete
                placeholder="Pickup location..."
                onSelect={setSource}
              />
              <div className="flex justify-center -my-2 relative z-0">
                <div className="w-px h-6 bg-slate-200" />
              </div>
              <Autocomplete
                placeholder="Dropoff location..."
                onSelect={setDestination}
              />
            </div>

            <div className="grid grid-cols-7 gap-4">
              <div className="col-span-4 space-y-2">
                <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-emerald-500" /> Select Date & Time
                </label>
                <div
                  onClick={handleTimeClick}
                  className="relative group cursor-pointer"
                >
                  <input
                    ref={timeInputRef}
                    type="datetime-local"
                    required
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    className="w-full px-4 py-3 pr-10 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-sm text-slate-900 font-medium cursor-pointer transition-all hover:border-emerald-300 [&::-webkit-calendar-picker-indicator]:opacity-0 [&::-webkit-calendar-picker-indicator]:absolute [&::-webkit-calendar-picker-indicator]:right-0 [&::-webkit-calendar-picker-indicator]:w-10 [&::-webkit-calendar-picker-indicator]:h-full [&::-webkit-calendar-picker-indicator]:cursor-pointer"
                  />
                  <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                    <Clock className="w-4 h-4 text-slate-400 group-hover:text-emerald-500 transition-colors" />
                  </div>
                </div>
              </div>

              {/* Vehicle Type */}
              <div className="col-span-3 space-y-2">
                <label className="block text-sm font-semibold text-slate-700">
                  Vehicle Type
                </label>
                <select
                  value={vehicleType}
                  onChange={(e) => setVehicleType(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-sm text-slate-900"
                >
                  {['Car', 'Auto Rickshaw', 'SUV Cab', 'Bike', 'Bus'].map(v => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Estimated Time */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-400" /> Estimated Time (mins)
                </label>
                <input
                  type="number"
                  min={1}
                  required
                  placeholder="e.g. 45"
                  value={estimatedTime}
                  onChange={(e) => setEstimatedTime(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-sm text-slate-900"
                />
              </div>

              {/* Female Only */}
              {currentUser?.Gender === 'F' && (
                <div
                  onClick={() => setFemaleOnly(!femaleOnly)}
                  className={`flex items-center justify-between px-5 py-4 rounded-2xl border-2 cursor-pointer transition-all select-none ${femaleOnly
                    ? 'bg-pink-50 border-pink-300 text-pink-700'
                    : 'bg-slate-50 border-slate-200 text-slate-500'
                    }`}
                >
                  <div>
                    <p className="font-semibold text-sm">Female Only Ride ♀</p>
                  </div>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${femaleOnly ? 'bg-pink-500 border-pink-500' : 'border-slate-300'
                    }`}>
                    {femaleOnly && <div className="w-2 h-2 rounded-full bg-white" />}
                  </div>
                </div>
              )}

              {/* <div className="space-y-2">
                <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <Users className="w-4 h-4 text-slate-400" /> Seats
                </label>
                <div className="flex items-center bg-slate-50 border border-slate-200 rounded-xl p-1">
                  {[1, 2, 3, 4, 5, 6].map(num => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setSeats(num)}
                      className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-all ${seats === num ? 'bg-white text-emerald-600 shadow-sm border border-slate-100' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div> */}
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={!source || !destination || !time}
                className="w-full py-4 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-100 disabled:text-slate-400 text-white font-bold rounded-2xl transition-all flex items-center justify-center gap-2 shadow-xl shadow-slate-900/10 active:scale-[0.98]"
              >
                Confirm & Publish <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </form>

          <div className="mt-12 bg-emerald-50 rounded-2xl p-6 border border-emerald-100">
            <h4 className="font-bold text-emerald-800 text-sm mb-2">Pro Tip</h4>
            <p className="text-emerald-700 text-xs leading-relaxed">
              Be specific about your pickup point. If you're leaving from Academic Block 1, mention it in the chat after publishing!
            </p>
          </div>
        </div>
      </div>

      {/* Map Content */}
      <div className="flex-1 bg-slate-100 relative">
        <MapComponent
          source={source ? [source.lat, source.lon] : undefined}
          destination={destination ? [destination.lat, destination.lon] : undefined}
        />

        {(!source || !destination) && (
          <div className="absolute top-6 left-1/2 -translate-x-1/2 z-[400] bg-white/90 backdrop-blur px-6 py-2 rounded-full shadow-lg text-sm font-medium text-slate-600 flex items-center gap-2 border border-white">
            <Calendar className="w-4 h-4 text-emerald-500" /> Use the search to mark your route
          </div>
        )}
      </div>
    </div>
  );
};