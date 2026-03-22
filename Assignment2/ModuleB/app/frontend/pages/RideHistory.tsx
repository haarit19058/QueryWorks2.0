import { useState } from 'react';
import { useApp, RideHistoryEntry } from '../store';
import { Clock, Users, History, CheckCircle2, Car, Star, Send } from 'lucide-react';

const StarRating: React.FC<{ value: number; onChange: (v: number) => void }> = ({ value, onChange }) => (
  <div className="flex gap-1">
    {[1, 2, 3, 4, 5].map(star => (
      <button key={star} type="button" onClick={() => onChange(star)}>
        <Star className={`w-5 h-5 transition-colors ${star <= value ? 'text-amber-400 fill-amber-400' : 'text-slate-200'}`} />
      </button>
    ))}
  </div>
);

const FeedbackForm: React.FC<{ ride: RideHistoryEntry; onSubmit: () => void }> = ({ ride, onSubmit }) => {
  const { currentUser, submitFeedback } = useApp();
  const CATEGORIES = ['Safety', 'Comfort', 'Punctuality'] as const;

  const [feedbackText, setFeedbackText] = useState('');
  const [category, setCategory] = useState<typeof CATEGORIES[number]>('Safety');
  const [submitting, setSubmitting] = useState(false);

  const peopleToRate = [
    ...ride.Passengers
      .filter(p => p.MemberID !== currentUser?.MemberID)
      .map(p => ({
        memberID: p.MemberID,
        name:     p.FullName,
        imageUrl: `https://picsum.photos/seed/${p.MemberID}/60`,
        rating:   0,
        comment:  '',
      })),
  ];

  const [ratings, setRatings] = useState(peopleToRate);
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
        ratings: ratings.map(r => ({ receiverMemberID: r.memberID, rating: r.rating, comment: r.comment })),
      });
      onSubmit();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="border-t border-amber-100 bg-amber-50 p-6 space-y-5">
      <p className="text-xs font-bold text-amber-700 uppercase tracking-widest">Share Your Experience</p>

      {/* Category tabs */}
      <div className="flex gap-2">
        {CATEGORIES.map(cat => (
          <button key={cat} onClick={() => setCategory(cat)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${category === cat ? 'bg-slate-900 text-white' : 'bg-white text-slate-500 border border-slate-100'}`}>
            {cat}
          </button>
        ))}
      </div>

      <textarea
        value={feedbackText}
        onChange={e => setFeedbackText(e.target.value)}
        placeholder="How was the ride overall?"
        rows={2}
        className="w-full bg-white border border-slate-100 rounded-2xl p-4 text-sm text-slate-800 placeholder-slate-300 resize-none focus:outline-none focus:ring-2 focus:ring-amber-300"
      />

      {/* Per-person ratings */}
      <div className="space-y-2">
        {ratings.map(person => (
          <div key={person.memberID} className="bg-white rounded-2xl border border-slate-100 p-3 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <img src={person.imageUrl} className="w-8 h-8 rounded-full object-cover" alt={person.name} />
                <div>
                  <p className="font-bold text-sm text-slate-800">{person.name}</p>
                  <p className="text-[10px] text-slate-400 uppercase tracking-wider">
                    {person.memberID === ride.AdminID ? 'Host' : 'Passenger'}
                  </p>
                </div>
              </div>
              <StarRating value={person.rating} onChange={v => updateRating(person.memberID, 'rating', v)} />
            </div>
            {person.rating > 0 && (
              <input type="text" value={person.comment}
                onChange={e => updateRating(person.memberID, 'comment', e.target.value)}
                placeholder="Leave a comment (optional)"
                className="w-full bg-slate-50 border border-slate-100 rounded-xl px-3 py-2 text-sm text-slate-700 placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-300"
              />
            )}
          </div>
        ))}
      </div>

      <button onClick={handleSubmit} disabled={!feedbackText.trim() || !allRated || submitting}
        className="w-full flex items-center justify-center gap-2 py-3 bg-slate-900 text-white font-bold rounded-2xl hover:bg-slate-800 transition-all disabled:opacity-40 disabled:cursor-not-allowed">
        <Send className="w-4 h-4" />
        {submitting ? 'Submitting…' : 'Submit Feedback'}
      </button>
    </div>
  );
};

export const RideHistory: React.FC = () => {
  const { rideHistory } = useApp();
  const [feedbackDone, setFeedbackDone] = useState<Set<string>>(new Set());

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
          {sorted.map(ride => {
            const needsFeedback = !ride.HasFeedback && !feedbackDone.has(ride.RideID);
            return (
              <div key={ride.RideID} className="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex flex-col md:flex-row">

                  {/* Left: route */}
                  <div className="p-6 md:p-8 md:w-2/3 space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-widest">
                        <Clock className="w-3 h-3" />
                        {new Date(ride.RideDate).toLocaleDateString([], { dateStyle: 'medium' })}
                        {' · '}{ride.StartTime.slice(0, 5)}
                      </div>
                      <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${needsFeedback ? 'bg-amber-50 text-amber-600 border border-amber-100' : 'bg-emerald-50 text-emerald-600'}`}>
                        {needsFeedback ? '⭐ Feedback Pending' : <><CheckCircle2 className="w-3 h-3" /> Completed</>}
                      </div>
                    </div>

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

                    {ride.Passengers.length > 0 && (
                      <div>
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">
                          Passengers ({ride.Passengers.length})
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {ride.Passengers.map(p => (
                            <div key={p.MemberID} className="flex items-center gap-1.5 bg-slate-50 border border-slate-100 rounded-full px-2.5 py-1">
                              <img src={`https://picsum.photos/seed/${p.MemberID}/40`} className="w-5 h-5 rounded-full object-cover" alt={p.FullName} />
                              <span className="text-xs font-semibold text-slate-700">{p.FullName.split(' ')[0]}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Right: meta */}
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
                        <Car className="w-3.5 h-3.5 text-slate-400" />{ride.Platform}
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500 font-medium">Seats taken</span>
                      <div className="flex items-center gap-1.5 font-bold text-slate-900">
                        <Users className="w-3.5 h-3.5 text-slate-400" />{ride.Passengers.length}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Feedback form — shown at bottom of card if not yet submitted */}
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
    </div>
  );
};