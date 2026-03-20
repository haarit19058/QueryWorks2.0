// import { useState, useEffect, useRef } from 'react';
// import { X, Send } from 'lucide-react';
// import { useApp } from '../store';

// // ── Types ────────────────────────────────────────────────────────────────────

// interface Ride {
//   RideID: string;
//   Source: string;
//   Destination: string;
// }

// interface Message {
//   MessageID: number;
//   RideID: string;
//   SenderID: number;
//   SenderName: string;
//   SenderAvatar?: string;
//   MessageText: string;
//   Timestamp: string;
//   IsRead: boolean;
//   _optimistic?: boolean; // temp flag for optimistic messages
// }

// interface ChatDrawerProps {
//   ride: Ride;
//   onClose: () => void;
// }

// // ── Component ────────────────────────────────────────────────────────────────

// export const ChatDrawer: React.FC<ChatDrawerProps> = ({ ride, onClose }) => {
//   const { currentUser } = useApp();
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [msg, setMsg]           = useState('');
//   const [loading, setLoading]   = useState(true);
//   const [sending, setSending]   = useState(false);
//   const bottomRef               = useRef<HTMLDivElement>(null);

//   // ── Fetch message history for this ride ─────────────────────────────────
//   // GET /api/messages?rideId=X
//   // Returns MessageHistory JOIN Members → { MessageID, SenderID, SenderName, SenderAvatar, MessageText, Timestamp }
//   useEffect(() => {
//     const fetchMessages = async () => {
//       try {
//         const res = await fetch(`/messages?rideId=${ride.RideID}`);
//         const data: Message[] = await res.json();
//         setMessages(data);
//       } catch (err) {
//         console.error('Failed to load messages:', err);
//       } finally {
//         setLoading(false);
//       }
//     };
//     fetchMessages();
//   }, [ride.RideID]);

//   // ── Auto-scroll on new messages ─────────────────────────────────────────
//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
//   }, [messages]);

//   // ── Send message → INSERT INTO MessageHistory ────────────────────────────
//   // POST /api/messages  body: { RideID, SenderID, MessageText }
//   // Returns the saved row: { MessageID, SenderID, SenderName, SenderAvatar, MessageText, Timestamp, IsRead }
//   const handleSend = async (e: React.FormEvent) => {
//     e.preventDefault();
//     if (!msg.trim() || sending || !currentUser) return;

//     // Optimistic update — show immediately, dimmed until confirmed
//     const tempId = Date.now();
//     const optimistic: Message = {
//       MessageID: tempId,
//       RideID: ride.RideID,
//       SenderID: currentUser.MemberID,
//       SenderName: currentUser.FullName,
//       SenderAvatar: currentUser.ProfileImageURL,
//       MessageText: msg.trim(),
//       Timestamp: new Date().toISOString(),
//       IsRead: false,
//       _optimistic: true,
//     };
//     setMessages(prev => [...prev, optimistic]);
//     setMsg('');
//     setSending(true);

//     try {
//       const res = await fetch('/api/messages', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           RideID: ride.RideID,
//           SenderID: currentUser.MemberID,
//           MessageText: optimistic.MessageText,
//         }),
//       });
//       if (!res.ok) throw new Error('Send failed');

//       // Replace the temp message with the real DB row
//       const saved: Message = await res.json();
//       setMessages(prev => prev.map(m => m.MessageID === tempId ? saved : m));
//     } catch {
//       // Rollback on failure
//       setMessages(prev => prev.filter(m => m.MessageID !== tempId));
//     } finally {
//       setSending(false);
//     }
//   };

//   const formatTime = (ts: string) =>
//     new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

//   // ── Render ────────────────────────────────────────────────────────────────
//   return (
//     // Backdrop
//     <div
//       className="fixed inset-0 z-[100]"
//       onClick={onClose}
//     >
//       {/* Drawer panel */}
//       <div
//         className="fixed inset-y-0 right-0 w-full sm:w-96 bg-white shadow-2xl flex flex-col"
//         onClick={e => e.stopPropagation()}
//       >
//         {/* Header */}
//         <div className="p-4 bg-[#0F172A] text-white flex justify-between items-center flex-shrink-0">
//           <div>
//             <h3 className="font-semibold text-lg leading-tight">Ride Chat</h3>
//             <p className="text-xs text-slate-400 truncate w-60">
//               {ride.Source} → {ride.Destination}
//             </p>
//           </div>
//           <button
//             onClick={onClose}
//             className="p-1.5 hover:bg-slate-700 rounded-full transition-colors"
//           >
//             <X className="w-5 h-5" />
//           </button>
//         </div>

//         {/* Message list */}
//         <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
//           {loading ? (
//             <div className="flex justify-center items-center h-full">
//               <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
//             </div>
//           ) : messages.length === 0 ? (
//             <div className="flex items-center justify-center h-full">
//               <p className="text-slate-400 italic text-sm text-center px-6">
//                 No messages yet. Ask about pickup points or luggage!
//               </p>
//             </div>
//           ) : (
//             messages.map(m => {
//               const isMe = m.SenderID === currentUser?.MemberID;
//               return (
//                 <div
//                   key={m.MessageID}
//                   className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
//                 >
//                   <div className="flex items-center gap-2 mb-1">
//                     <span className="text-[10px] font-semibold text-slate-500">{m.SenderName}</span>
//                     <span className="text-[10px] text-slate-400">{formatTime(m.Timestamp)}</span>
//                   </div>
//                   <div
//                     className={`max-w-[85%] px-4 py-2 rounded-2xl text-sm transition-opacity ${
//                       m._optimistic ? 'opacity-60' : 'opacity-100'
//                     } ${
//                       isMe
//                         ? 'bg-emerald-500 text-white rounded-tr-none'
//                         : 'bg-white text-slate-700 shadow-sm rounded-tl-none border border-slate-100'
//                     }`}
//                   >
//                     {m.MessageText}
//                   </div>
//                 </div>
//               );
//             })
//           )}
//           <div ref={bottomRef} />
//         </div>

//         {/* Input bar */}
//         <form
//           onSubmit={handleSend}
//           className="p-4 border-t border-slate-200 bg-white flex gap-2 items-center flex-shrink-0"
//         >
//           <input
//             type="text"
//             value={msg}
//             onChange={e => setMsg(e.target.value)}
//             placeholder="Type a message…"
//             className="flex-1 px-4 py-2.5 bg-slate-100 rounded-full text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none border-none"
//           />
//           <button
//             type="submit"
//             disabled={sending}
//             className="p-2.5 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-200 text-white rounded-full transition-colors"
//           >
//             <Send className="w-4 h-4" />
//           </button>
//         </form>
//       </div>
//     </div>
//   );
// };
import { useState, useEffect, useRef } from 'react';
import { X, Send } from 'lucide-react';
import { useApp } from '../store';
import api from '../lib/api'; // <-- Using your Axios instance

// ── Types ────────────────────────────────────────────────────────────────────

interface Ride {
  RideID: string;
  Source: string;
  Destination: string;
}

interface Message {
  MessageID: number;
  RideID: string;
  SenderID: number;
  SenderName: string;
  SenderAvatar?: string;
  MessageText: string;
  Timestamp: string;
  IsRead: boolean;
  _optimistic?: boolean; 
}

interface ChatDrawerProps {
  ride: Ride;
  onClose: () => void;
}

// ── Component ────────────────────────────────────────────────────────────────

export const ChatDrawer: React.FC<ChatDrawerProps> = ({ ride, onClose }) => {
  const { currentUser } = useApp();
  const [messages, setMessages] = useState<Message[]>([]);
  const [msg, setMsg]           = useState('');
  const [loading, setLoading]   = useState(true);
  const [sending, setSending]   = useState(false);
  const bottomRef               = useRef<HTMLDivElement>(null);

  // ── Fetch message history ───────────────────────────────────────────────
  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const res = await api.get('/messages', { 
          params: { rideId: ride.RideID } 
        });
        setMessages(res.data);
      } catch (err) {
        console.error('Failed to load messages:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMessages();
  }, [ride.RideID]);

  // ── Auto-scroll to bottom ───────────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ── Send message ────────────────────────────────────────────────────────
  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!msg.trim() || sending || !currentUser) return;

    const messageText = msg.trim();
    setMsg(''); // Clear input immediately for better UX
    setSending(true);

    // 1. Optimistic update
    const tempId = Date.now();
    const optimisticMsg: Message = {
      MessageID: tempId,
      RideID: ride.RideID,
      SenderID: currentUser.MemberID,
      SenderName: currentUser.FullName,
      SenderAvatar: currentUser.ProfileImageURL,
      MessageText: messageText,
      Timestamp: new Date().toISOString(),
      IsRead: false,
      _optimistic: true,
    };
    
    setMessages(prev => [...prev, optimisticMsg]);

    // 2. Network Request
    try {
      // Backend infers SenderID from get_current_user token
      const res = await api.post('/messages', {
        RideID: ride.RideID,
        SenderID: currentUser.MemberID,
        MessageText: messageText,
      });

      // 3. Replace optimistic message with confirmed DB row
      const savedMsg: Message = res.data;
      setMessages(prev => prev.map(m => m.MessageID === tempId ? savedMsg : m));
    } catch (err) {
      console.error('Failed to send message', err);
      // Rollback on failure
      setMessages(prev => prev.filter(m => m.MessageID !== tempId));
    } finally {
      setSending(false);
    }
  };

  const formatTime = (ts: string) => {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="fixed inset-0 z-[100] bg-slate-900/40 backdrop-blur-sm" onClick={onClose}>
      {/* Drawer Panel */}
      <div
        className="fixed inset-y-0 right-0 w-full sm:w-[400px] bg-[#F8FAFC] shadow-2xl flex flex-col transform transition-transform duration-300"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 bg-white border-b border-slate-200 flex justify-between items-center flex-shrink-0 z-10">
          <div>
            <h3 className="font-bold text-slate-800 text-lg">Group Chat</h3>
            <p className="text-xs text-slate-500 font-medium truncate w-64 mt-0.5">
              {ride.Source} → {ride.Destination}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Area */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {loading ? (
            <div className="flex justify-center items-center h-full">
              <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full opacity-60">
              <div className="w-16 h-16 bg-slate-200 rounded-full flex items-center justify-center mb-3">
                <Send className="w-6 h-6 text-slate-400 ml-1" />
              </div>
              <p className="text-slate-500 font-medium text-sm text-center px-6">
                Start the conversation.<br/> Coordinate your pickup point!
              </p>
            </div>
          ) : (
            messages.map((m, index) => {
              const isMe = m.SenderID === currentUser?.MemberID;
              
              // Determine if we need to show the sender's name (only if the previous message wasn't from them)
              const showName = !isMe && (index === 0 || messages[index - 1].SenderID !== m.SenderID);

              return (
                <div key={m.MessageID} className={`flex w-full ${isMe ? 'justify-end' : 'justify-start'}`}>
                  
                  {/* Avatar for others */}
                  {!isMe && (
                    <img
                      src={m.SenderAvatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(m.SenderName)}&background=e2e8f0&color=475569`}
                      alt={m.SenderName}
                      className="w-8 h-8 rounded-full object-cover mr-2 flex-shrink-0 self-end mb-5"
                    />
                  )}

                  <div className={`flex flex-col ${isMe ? 'items-end' : 'items-start'} max-w-[75%]`}>
                    {/* Sender Name (Only for others, grouped) */}
                    {showName && (
                      <span className="text-[11px] font-bold text-slate-400 mb-1 ml-1">
                        {m.SenderName}
                      </span>
                    )}

                    {/* Chat Bubble */}
                    <div
                      className={`px-4 py-2.5 shadow-sm text-[15px] leading-relaxed transition-all ${
                        m._optimistic ? 'opacity-50' : 'opacity-100'
                      } ${
                        isMe
                          ? 'bg-emerald-500 text-white rounded-2xl rounded-br-sm'
                          : 'bg-white border border-slate-100 text-slate-800 rounded-2xl rounded-bl-sm'
                      }`}
                    >
                      {m.MessageText}
                    </div>

                    {/* Timestamp */}
                    <span className={`text-[10px] text-slate-400 mt-1 ${isMe ? 'mr-1' : 'ml-1'}`}>
                      {formatTime(m.Timestamp)}
                      {m._optimistic && ' • Sending...'}
                    </span>
                  </div>
                </div>
              );
            })
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-slate-200 flex-shrink-0">
          <form
            onSubmit={handleSend}
            className="flex gap-2 items-center bg-slate-100 rounded-full p-1 pr-1.5"
          >
            <input
              type="text"
              value={msg}
              onChange={e => setMsg(e.target.value)}
              placeholder="Message the group..."
              className="flex-1 bg-transparent px-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none"
            />
            <button
              type="submit"
              disabled={sending || !msg.trim()}
              className="p-2.5 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-300 disabled:text-slate-500 text-white rounded-full transition-colors flex items-center justify-center flex-shrink-0"
            >
              <Send className="w-4 h-4 ml-0.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};