import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, Ride } from '../store';
import { Check, X, Clock, MapPin, Users, Car, Star, Send } from 'lucide-react';

// ── Star rating component ─────────────────────────────────────────────────────
const StarRating: React.FC<{ value: number; onChange: (v: number) => void }> = ({ value, onChange }) => (
  <div className="flex gap-1">
    {[1, 2, 3, 4, 5].map(star => (
      <button key={star} type="button" onClick={() => onChange(star)}>
        <Star
          className={`w-5 h-5 transition-colors ${star <= value ? 'text-amber-400 fill-amber-400' : 'text-slate-200'}`}
        />
      </button>
    ))}
  </div>
);

// ── Per-person rating state ───────────────────────────────────────────────────
interface PersonRating {
  memberID: number;
  name: string;
  imageUrl: string;
  rating: number;
  comment: string;
}

// ── Feedback form for a single ride ──────────────────────────────────────────
const FeedbackForm: React.FC<{ ride: Ride; onSubmit: () => void }> = ({ ride, onSubmit }) => {
  const { currentUser, submitFeedback } = useApp();

  const CATEGORIES = ['Safety', 'Comfort', 'Punctuality'] as const;

  const [feedbackText, setFeedbackText] = useState('');
  const [category, setCategory] = useState<typeof CATEGORIES[number]>('Safety');
  const [submitting, setSubmitting] = useState(false);
  // Build the list of people to rate
  const peopleToRate: PersonRating[] = [
    // Include Host ONLY if the current user is not the host
    ...(currentUser?.MemberID !== ride.AdminID
      ? [
        {
          memberID: ride.AdminID,
          name: ride.HostName,
          imageUrl: ride.ProfileImageURL || `https://picsum.photos/seed/${ride.AdminID}/60`,
          rating: 0,
          comment: '',
        },
      ]
      : []),
    // Other passengers (exclude current user)
    ...ride.Passengers.filter((p) => p.MemberID !== currentUser?.MemberID).map((p) => ({
      memberID: p.MemberID,
      name: p.FullName,
      imageUrl: p.ProfileImageUrl || `https://picsum.photos/seed/${p.MemberID}/60`,
      rating: 0,
      comment: '',
    })),
  ];

  const [ratings, setRatings] = useState<PersonRating[]>(peopleToRate);

  const updateRating = (memberID: number, field: 'rating' | 'comment', value: number | string) =>
    setRatings(prev => prev.map(r => r.memberID === memberID ? { ...r, [field]: value } : r));

  const allRated = ratings.every(r => r.rating > 0);

  const handleSubmit = async () => {
    if (!feedbackText.trim() || !allRated) return;
    setSubmitting(true);
    try {
      await submitFeedback(ride.RideID, {
        feedbackText,
        feedbackCategory: category,
        ratings: ratings.map(r => ({
          receiverMemberID: r.memberID,
          rating: r.rating,
          comment: r.comment,
        })),
      });
      onSubmit();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-amber-50 border border-amber-100 rounded-3xl p-6 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-amber-400 flex items-center justify-center">
          <Star className="w-4 h-4 text-white fill-white" />
        </div>
        <div>
          <p className="font-bold text-slate-900">Ride Completed!</p>
          <p className="text-xs text-slate-500">Share your experience before this ride is archived</p>
        </div>
      </div>

      {/* Overall feedback */}
      <div className="space-y-3">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Overall Feedback</p>

        {/* Category tabs */}
        <div className="flex gap-2">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${category === cat
                ? 'bg-slate-900 text-white'
                : 'bg-white text-slate-500 border border-slate-100 hover:border-slate-300'
                }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <textarea
          value={feedbackText}
          onChange={e => setFeedbackText(e.target.value)}
          placeholder="How was the ride overall?"
          rows={3}
          className="w-full bg-white border border-slate-100 rounded-2xl p-4 text-sm text-slate-800 placeholder-slate-300 resize-none focus:outline-none focus:ring-2 focus:ring-amber-300"
        />
      </div>

      {/* Per-person ratings */}
      <div className="space-y-3">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
          Rate Participants ({ratings.length})
        </p>

        <div className="space-y-3">
          {ratings.map(person => (
            <div key={person.memberID} className="bg-white rounded-2xl border border-slate-100 p-4 space-y-3">
              {/* Person info + stars */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <img
                    src={person.imageUrl}
                    className="w-9 h-9 rounded-full object-cover border border-slate-100"
                    alt={person.name}
                  />
                  <div>
                    <p className="font-bold text-sm text-slate-800">{person.name}</p>
                    <p className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
                      {person.memberID === ride.AdminID ? 'Host' : 'Passenger'}
                    </p>
                  </div>
                </div>
                <StarRating
                  value={person.rating}
                  onChange={v => updateRating(person.memberID, 'rating', v)}
                />
              </div>

              {/* Comment — only show after they've starred */}
              {person.rating > 0 && (
                <input
                  type="text"
                  value={person.comment}
                  onChange={e => updateRating(person.memberID, 'comment', e.target.value)}
                  placeholder="Leave a comment (optional)"
                  className="w-full bg-slate-50 border border-slate-100 rounded-xl px-3 py-2 text-sm text-slate-700 placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-300"
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!feedbackText.trim() || !allRated || submitting}
        className="w-full flex items-center justify-center gap-2 py-3 bg-slate-900 text-white font-bold rounded-2xl hover:bg-slate-800 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Send className="w-4 h-4" />
        {submitting ? 'Submitting…' : 'Submit Feedback'}
      </button>
    </div>
  );
};

// ── Main component ────────────────────────────────────────────────────────────
export const YourRides: React.FC = () => {
  const { rides, myRequests, pendingRequests, currentUser, updateRequest, completeRide } = useApp();
  const navigate = useNavigate();

  // Track which rides the user has already submitted feedback for this session
  const [feedbackDone, setFeedbackDone] = useState<Set<string>>(new Set());

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
              const ridePassengers = ride.Passengers ?? [];
              const isCompleting = ride.Status === 'COMPLETING';

              return (
                <div key={ride.RideID} className="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm">

                  {/* Card header */}
                  <div className={`p-6 md:p-8 text-white flex flex-col md:flex-row justify-between gap-4 ${isCompleting ? 'bg-amber-500' : 'bg-slate-900'}`}>
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

                    {isCompleting ? (
                      <div className="px-4 py-2 bg-amber-400 text-slate-900 text-xs font-bold rounded-xl self-start md:self-center">
                        ⏳ Needs Your Feedback
                      </div>
                    ) : (
                      <button
                        onClick={() => completeRide(ride.RideID)}
                        className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-emerald-500/20 self-start md:self-center"
                      >
                        Mark as Completed
                      </button>
                    )}
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
                    
                    {isCompleting && !feedbackDone.has(ride.RideID) && (
                      <div className="pt-4 mt-8 border-t border-slate-100">
                        <FeedbackForm
                          ride={ride}
                          onSubmit={() => setFeedbackDone((prev) => new Set(prev).add(ride.RideID))}
                        />
                      </div>
                    )}
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

              const needsFeedback =
                ride.Status === 'COMPLETING' &&
                req.RequestStatus === 'APPROVED' &&
                !feedbackDone.has(ride.RideID);

              return (
                <div key={req.RequestID} className="flex flex-col gap-3">

                  {/* Ride card */}
                  <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col justify-between gap-4">
                    <div className="flex justify-between items-start">
                      <span className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase border ${needsFeedback
                        ? 'bg-amber-50 text-amber-600 border-amber-100'
                        : statusStyle(req.RequestStatus)
                        }`}>
                        {needsFeedback ? '⏳ Feedback Required' : req.RequestStatus}
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

                  {/* Feedback form — shown inline below the card when COMPLETING */}
                  {needsFeedback && (
                    <FeedbackForm
                      ride={ride}
                      onSubmit={() => setFeedbackDone(prev => new Set(prev).add(ride.RideID))}
                    />
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>

    </div>
  );
};