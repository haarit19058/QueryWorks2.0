import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { useApp } from '../store';
import { Car, ShieldCheck } from 'lucide-react';

export const Login: React.FC = () => {
  const { loginWithGoogle } = useApp();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogle = useGoogleLogin({
    flow: 'auth-code',
    onSuccess: async (tokenResponse) => {
      setLoading(true);
      setError('');
      try {
        // POST /api/auth/google  { token: "..." }
        // Backend verifies with Google, checks Members table by email
        // Returns either:
        //   { isNewUser: false, ...User fields }   → already registered
        //   { isNewUser: true, email, name, picture } → needs signup
        const result = await loginWithGoogle(tokenResponse.code);
        console.log(result);

        if (result.isNewUser) {
          // Pass prefilled data to signup via location state
          navigate('/signup', {
            state: {
              email: result.email,
              fullName: result.name,
              picture: result.picture,
            },
          });
        } else {
          navigate('/rides');
        }
      } catch (e) {
        setError('Login failed. Please try again.');
      } finally {
        setLoading(false);
      }
    },
    onError: () => setError('Google sign-in was cancelled or failed.'),
  });

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-slate-50">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-2xl p-10 border border-slate-100">

        {/* Logo */}
        <div className="text-center mb-10">
          <div className="bg-emerald-500 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/30">
            <Car className="text-white w-9 h-9" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800">IITGN Pool</h1>
          <p className="text-slate-500 mt-2 text-sm">The exclusive student carpool network</p>
        </div>

        {/* Google button */}
        <button
          onClick={() => handleGoogle()}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 py-4 bg-white border-2 border-slate-200 hover:border-slate-300 hover:bg-slate-50 rounded-2xl font-semibold text-slate-700 transition-all shadow-sm active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
          ) : (
            <GoogleIcon />
          )}
          {loading ? 'Signing in…' : 'Continue with Google'}
        </button>

        {/* Error message */}
        {error && (
          <p className="mt-4 text-sm text-red-500 text-center flex items-center justify-center gap-1.5">
            <ShieldCheck className="w-4 h-4" /> {error}
          </p>
        )}

        {/* IITGN-only notice */}
        <div className="mt-8 flex items-start gap-2 bg-emerald-50 border border-emerald-100 rounded-2xl p-4">
          <ShieldCheck className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
          <p className="text-xs text-emerald-700 leading-relaxed">
            Only <strong>@iitgn.ac.in</strong> Google accounts are accepted. Sign in with your institute email.
          </p>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          By signing in, you agree to follow IITGN Community guidelines for safe carpooling.
        </p>
      </div>
    </div>
  );
};

// Inline Google SVG icon — no extra dependency needed
const GoogleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 48 48">
    <path fill="#FFC107" d="M43.6 20H24v8h11.3C33.7 33.1 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.8 1.1 7.9 3l5.7-5.7C34.1 6.5 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20c11 0 19.7-8 19.7-20 0-1.3-.1-2.7-.1-4z"/>
    <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.5 16 19 13 24 13c3 0 5.8 1.1 7.9 3l5.7-5.7C34.1 6.5 29.3 4 24 4c-7.7 0-14.3 4.3-17.7 10.7z"/>
    <path fill="#4CAF50" d="M24 44c5.2 0 9.9-1.9 13.5-5l-6.2-5.2C29.3 35.3 26.8 36 24 36c-5.2 0-9.7-2.9-11.3-7.1l-6.6 5.1C9.8 39.8 16.4 44 24 44z"/>
    <path fill="#1976D2" d="M43.6 20H24v8h11.3c-.8 2.3-2.3 4.2-4.2 5.6l6.2 5.2C41.1 35.4 44 30.1 44 24c0-1.3-.1-2.7-.4-4z"/>
  </svg>
);