
// import React from 'react';
// import { Car, Plus, Compass, UserCircle, LogOut, History } from 'lucide-react';
// import { useApp } from '../store';

// interface NavbarProps {
//   currentPage: string;
//   setPage: (p: string) => void;
// }

// export const Navbar: React.FC<NavbarProps> = ({ currentPage, setPage }) => {
//   const { currentUser, logout } = useApp();

//   return (
//     <nav className="glass sticky top-0 z-50 px-6 py-4">
//       <div className="max-w-7xl mx-auto flex justify-between items-center">
//         <div 
//           className="flex items-center gap-2 cursor-pointer group" 
//           onClick={() => setPage('available')}
//         >
//           <div className="bg-emerald-500 p-2 rounded-lg group-hover:bg-emerald-400 transition-colors">
//             <Car className="text-white w-6 h-6" />
//           </div>
//           <span className="text-white font-bold text-xl tracking-tight">IITGN <span className="text-emerald-400">Pool</span></span>
//         </div>

//         {currentUser && (
//           <div className="hidden md:flex items-center gap-8">
//             <button 
//               onClick={() => setPage('add')}
//               className={`flex items-center gap-2 font-medium transition-colors ${currentPage === 'add' ? 'text-emerald-400' : 'text-slate-300 hover:text-white'}`}
//             >
//               <Plus className="w-4 h-4" /> Add Ride
//             </button>
//             <button 
//               onClick={() => setPage('available')}
//               className={`flex items-center gap-2 font-medium transition-colors ${currentPage === 'available' ? 'text-emerald-400' : 'text-slate-300 hover:text-white'}`}
//             >
//               <Compass className="w-4 h-4" /> Available Rides
//             </button>
//             <button 
//               onClick={() => setPage('yours')}
//               className={`flex items-center gap-2 font-medium transition-colors ${currentPage === 'yours' ? 'text-emerald-400' : 'text-slate-300 hover:text-white'}`}
//             >
//               <UserCircle className="w-4 h-4" /> Your Rides
//             </button>
//             <button 
//               onClick={() => setPage('history')}
//               className={`flex items-center gap-2 font-medium transition-colors ${currentPage === 'history' ? 'text-emerald-400' : 'text-slate-300 hover:text-white'}`}
//             >
//               <History className="w-4 h-4" /> History
//             </button>
//           </div>
//         )}

//         <div className="flex items-center gap-4">
//           {currentUser ? (
//             <div className="flex items-center gap-3 pl-4 border-l border-white/10">
//               <img src={currentUser.profilePic} className="w-8 h-8 rounded-full border-2 border-emerald-500" alt="profile" />
//               <button 
//                 onClick={logout}
//                 className="p-2 text-slate-300 hover:text-red-400 transition-colors"
//                 title="Logout"
//               >
//                 <LogOut className="w-5 h-5" />
//               </button>
//             </div>
//           ) : (
//             <div className="flex gap-2">
//               <button onClick={() => setPage('login')} className="px-4 py-2 text-white font-medium hover:text-emerald-400 transition-colors">Login</button>
//               <button onClick={() => setPage('login')} className="px-6 py-2 bg-emerald-500 hover:bg-emerald-400 text-white font-bold rounded-lg transition-all transform active:scale-95 shadow-lg shadow-emerald-500/20">Sign Up</button>
//             </div>
//           )}
//         </div>
//       </div>
//     </nav>
//   );
// };
// import Re from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Car, Plus, Compass, UserCircle, LogOut, History } from 'lucide-react';
import { useApp } from '../store';

export const Navbar: React.FC = () => {
  const { currentUser, logout } = useApp();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinkCls = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2 font-medium transition-colors ${
      isActive ? 'text-emerald-400' : 'text-slate-300 hover:text-white'
    }`;

  return (
    <nav className="glass sticky top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">

        {/* Logo */}
        <NavLink to="/rides" className="flex items-center gap-2 cursor-pointer group">
          <div className="bg-emerald-500 p-2 rounded-lg group-hover:bg-emerald-400 transition-colors">
            <Car className="text-white w-6 h-6" />
          </div>
          <span className="text-white font-bold text-xl tracking-tight">
            IITGN <span className="text-emerald-400">Pool</span>
          </span>
        </NavLink>

        {/* Nav links — only shown when logged in */}
        {currentUser && (
          <div className="hidden md:flex items-center gap-8">
            <NavLink to="/add-ride" className={navLinkCls}>
              <Plus className="w-4 h-4" /> Add Ride
            </NavLink>
            <NavLink to="/rides" className={navLinkCls}>
              <Compass className="w-4 h-4" /> Available Rides
            </NavLink>
            <NavLink to="/your-rides" className={navLinkCls}>
              <UserCircle className="w-4 h-4" /> Your Rides
            </NavLink>
            <NavLink to="/history" className={navLinkCls}>
              <History className="w-4 h-4" /> History
            </NavLink>
          </div>
        )}

        {/* Right side — user avatar or login/signup buttons */}
        <div className="flex items-center gap-4">
          {currentUser ? (
            <div className="flex items-center gap-3 pl-4 border-l border-white/10">
              <img
                // ProfileImageURL from Members table (or Google picture)
                src={currentUser.ProfileImageURL}
                className="w-8 h-8 rounded-full border-2 border-emerald-500 object-cover cursor-pointer"
                alt={currentUser.FullName}
                onClick={() => navigate(`/profile/${currentUser.MemberID}`)}
                title={currentUser.FullName}
              />
              <button
                onClick={handleLogout}
                className="p-2 text-slate-300 hover:text-red-400 transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <NavLink
                to="/login"
                className="px-4 py-2 text-white font-medium hover:text-emerald-400 transition-colors"
              >
                Login
              </NavLink>
              <NavLink
                to="/login"
                className="px-6 py-2 bg-emerald-500 hover:bg-emerald-400 text-white font-bold rounded-lg transition-all active:scale-95 shadow-lg shadow-emerald-500/20"
              >
                Sign Up
              </NavLink>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};