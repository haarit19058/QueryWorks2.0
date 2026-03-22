// import { useParams } from 'react-router-dom';
// import { useEffect } from 'react';
// // import api from '../lib/api';

// export const Profile = () => {
//   // Extract the "id" parameter from the URL
//   const { id } = useParams(); 

//   useEffect(() => {
//     // Now you can use this ID to fetch the host's details
//     // api.get(`/users/${id}`).then(...)
//     console.log("Fetching data for user ID:", id);
//   }, [id]);

//   return (
//     <div>
//       <h1>User Profile: {id}</h1>
//       {/* Render profile details here */}
//     </div>
//   );
// };
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Star, 
  Car, 
  Map, 
  GraduationCap, 
  User, 
  Calendar, 
  ArrowLeft, 
  BookOpen, 
  ShieldCheck 
} from 'lucide-react';
import api from '../lib/api';

// ── Types ────────────────────────────────────────────────────────────────────

interface UserProfile {
  MemberID: number;
  FullName: string;
  ProfileImageURL: string;
  Programme: string;
  Branch: string | null;
  BatchYear: number;
  Age: number | null;
  Gender: string | null;
  AverageRating: number;
  TotalRidesTaken: number;
  TotalRidesHosted: number;
  NumberOfRatings: number;
}

// ── Component ────────────────────────────────────────────────────────────────

export const ProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        // Adjust this endpoint to match your actual backend route
        const res = await api.get(`/members/${id}`);
        setProfile(res.data);
      } catch (err) {
        console.error('Failed to load profile:', err);
        setError('Could not find this user.');
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchProfile();
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-500">Loading profile…</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <div className="bg-white rounded-3xl p-10 border border-slate-200 shadow-sm">
          <User className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">User Not Found</h2>
          <p className="text-slate-500 mb-6">{error || "This profile doesn't exist."}</p>
          <button 
            onClick={() => navigate(-1)}
            className="px-6 py-2.5 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-10 py-8">
      
      {/* Back Button */}
      <button 
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-slate-500 hover:text-slate-900 font-semibold mb-6 transition-colors group"
      >
        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" /> 
        Back
      </button>

      {/* Main Profile Card */}
      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-sm overflow-hidden">
        
        {/* Banner Gradient */}
        <div className="h-32 md:h-48 bg-gradient-to-r from-emerald-400 to-teal-600 relative">
          {/* Optional pattern overlay could go here */}
        </div>

        <div className="px-6 md:px-10 pb-10">
          
          {/* Header Section (Avatar + Name) */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 -mt-12 md:-mt-16 mb-8 relative z-10">
            <div className="flex flex-col md:flex-row md:items-end gap-5">
              <img
                src={profile.ProfileImageURL || `https://picsum.photos/seed/${profile.MemberID}/200`}
                alt={profile.FullName}
                className="w-24 h-24 md:w-32 md:h-32 rounded-2xl border-4 border-white shadow-lg object-cover bg-white"
              />
              <div className="mb-2">
                <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 flex items-center gap-2">
                  {profile.FullName}
                  <ShieldCheck className="w-6 h-6 text-emerald-500" />
                </h1>
                <p className="text-slate-500 font-medium mt-1">
                  Member #{profile.MemberID}
                </p>
              </div>
            </div>
            
            {/* Quick Action / Status */}
            <div className="mb-2">
              <span className="inline-flex items-center px-4 py-2 bg-emerald-50 text-emerald-700 font-bold rounded-full text-sm border border-emerald-100">
                Verified Student
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left Column: Academic & Personal Info */}
            <div className="lg:col-span-1 space-y-6">
              
              {/* Academic Details */}
              <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Academic Info</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <GraduationCap className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{profile.Programme}</p>
                      <p className="text-xs text-slate-500">Programme</p>
                    </div>
                  </div>
                  {profile.Branch && (
                    <div className="flex items-start gap-3">
                      <BookOpen className="w-5 h-5 text-slate-400 mt-0.5" />
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{profile.Branch}</p>
                        <p className="text-xs text-slate-500">Branch</p>
                      </div>
                    </div>
                  )}
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-slate-900">Class of {profile.BatchYear}</p>
                      <p className="text-xs text-slate-500">Batch Year</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Personal Details */}
              {(profile.Age || profile.Gender) && (
                <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Personal</h3>
                  <div className="space-y-4">
                    {profile.Gender && (
                      <div className="flex items-center gap-3">
                        <User className="w-5 h-5 text-slate-400" />
                        <span className="text-sm font-semibold text-slate-700">
                          {profile.Gender === 'M' ? 'Male' : profile.Gender === 'F' ? 'Female' : profile.Gender}
                        </span>
                      </div>
                    )}
                    {profile.Age && (
                      <div className="flex items-center gap-3">
                        <div className="w-5 flex justify-center text-slate-400 font-bold text-sm">#</div>
                        <span className="text-sm font-semibold text-slate-700">{profile.Age} years old</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Ride Statistics */}
            <div className="lg:col-span-2">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Ride Activity</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Rating Stat Card */}
                <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4">
                  <div className="w-12 h-12 bg-amber-50 rounded-full flex items-center justify-center border border-amber-100 flex-shrink-0">
                    <Star className="w-6 h-6 text-amber-500 fill-amber-500" />
                  </div>
                  <div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-extrabold text-slate-900">
                        {profile.NumberOfRatings > 0 ? profile.AverageRating.toFixed(1) : 'New'}
                      </span>
                      {profile.NumberOfRatings > 0 && (
                        <span className="text-sm text-slate-500 font-medium">/ 5.0</span>
                      )}
                    </div>
                    <p className="text-sm text-slate-500">
                      {profile.NumberOfRatings === 0 
                        ? 'No ratings yet' 
                        : `Based on ${profile.NumberOfRatings} reviews`}
                    </p>
                  </div>
                </div>

                {/* Rides Hosted Stat Card */}
                <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4">
                  <div className="w-12 h-12 bg-emerald-50 rounded-full flex items-center justify-center border border-emerald-100 flex-shrink-0">
                    <Car className="w-6 h-6 text-emerald-600" />
                  </div>
                  <div>
                    <span className="block text-2xl font-extrabold text-slate-900">
                      {profile.TotalRidesHosted}
                    </span>
                    <p className="text-sm text-slate-500">Rides Hosted</p>
                  </div>
                </div>

                {/* Rides Taken Stat Card */}
                <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center border border-blue-100 flex-shrink-0">
                    <Map className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <span className="block text-2xl font-extrabold text-slate-900">
                      {profile.TotalRidesTaken}
                    </span>
                    <p className="text-sm text-slate-500">Rides Taken</p>
                  </div>
                </div>

              </div>
              
              {/* Extra Empty State for missing data / filler */}
              {profile.TotalRidesHosted === 0 && profile.TotalRidesTaken === 0 && (
                <div className="mt-6 p-6 bg-slate-50 rounded-2xl border border-dashed border-slate-300 text-center">
                  <p className="text-slate-500 font-medium">This user hasn't participated in any rides yet.</p>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </div>
  );
};