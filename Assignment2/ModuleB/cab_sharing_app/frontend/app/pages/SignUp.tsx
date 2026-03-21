import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../store';
import { Car, User, Phone, BookOpen, GraduationCap, Calendar, Venus, Mars } from 'lucide-react';

// Fields collected here (Email + FullName + ProfileImageURL come from Google)
interface SignupForm {
  ContactNumber: string;
  Programme: string;
  Branch: string;
  BatchYear: string;
  Gender: 'M' | 'F' | '';
  Age: string;            // optional
}

interface FormErrors {
  ContactNumber?: string;
  Programme?: string;
  Branch?: string;
  BatchYear?: string;
  Gender?: string;
  Age?: string;
}

const PROGRAMMES = ['B.Tech', 'M.Tech', 'M.Sc', 'PhD'];
const BRANCHES = ['CSE', 'EE', 'ME', 'CE', 'Chemical', 'Materials', 'Mathematics', 'Physics', 'Chemistry', 'HSS', 'Other'];

export const Signup: React.FC = () => {
  const { registerUser } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  // Pre-filled from Google via Login page navigate state
  const { email = '', fullName = '', picture = '', google_sub = '' } = (location.state as {
    email: string; fullName: string; picture: string; google_sub: string;  // 👈 add
  }) || {};

  const [form, setForm] = useState<SignupForm>({
    ContactNumber: '',
    Programme: '',
    Branch: '',
    BatchYear: '',
    Gender: '',
    Age: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const set = (field: keyof SignupForm, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: '' }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.ContactNumber.match(/^[6-9]\d{9}$/)) e.ContactNumber = 'Enter a valid 10-digit mobile number';
    if (!form.Programme) e.Programme = 'Required';
    if (!form.BatchYear) e.BatchYear = 'Required';
    if (!form.Gender) e.Gender = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      // POST /api/auth/register
      // Body: all Members fields (MemberID is AUTO_INCREMENT, handled by DB)
      await registerUser({
        google_sub,
        FullName: fullName,
        Email: email,
        ProfileImageURL: picture || 'default_avatar.png',
        Programme: form.Programme,
        Branch: form.Branch || null,
        BatchYear: Number(form.BatchYear),
        ContactNumber: form.ContactNumber,
        Gender: form.Gender as 'M' | 'F',
        Age: form.Age ? Number(form.Age) : null,
      });
      navigate('/rides');
    } catch (err) {
      console.error('Signup failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="max-w-lg w-full bg-white rounded-3xl shadow-2xl p-8 border border-slate-100">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="bg-emerald-500 w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/30">
            <Car className="text-white w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Complete your profile</h1>
          <p className="text-slate-500 mt-1 text-sm">Just a few more details to get you started</p>
        </div>

        {/* Google account preview */}
        <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-100 mb-8">
          <img
            src={picture || `https://picsum.photos/seed/${email}/100`}
            className="w-10 h-10 rounded-full border-2 border-white shadow"
            alt={fullName}
          />
          <div>
            <p className="font-semibold text-slate-800 text-sm">{fullName}</p>
            <p className="text-slate-400 text-xs">{email}</p>
          </div>
          <span className="ml-auto text-[10px] font-bold text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-1 rounded-full">
            Google ✓
          </span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Contact number */}
          <Field label="Mobile Number" icon={<Phone className="w-4 h-4" />} error={errors.ContactNumber}>
            <input
              type="tel"
              placeholder="10-digit mobile number"
              value={form.ContactNumber}
              onChange={e => set('ContactNumber', e.target.value)}
              className={inputCls(!!errors.ContactNumber)}
            />
          </Field>

          {/* Programme + Branch — 2 column */}
          <div className="grid grid-cols-2 gap-4">
            <Field label="Programme" icon={<GraduationCap className="w-4 h-4" />} error={errors.Programme}>
              <select value={form.Programme} onChange={e => set('Programme', e.target.value)} className={inputCls(!!errors.Programme)}>
                <option value="">Select…</option>
                {PROGRAMMES.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </Field>

            <Field label="Branch / Dept" icon={<BookOpen className="w-4 h-4" />}>
              <select value={form.Branch} onChange={e => set('Branch', e.target.value)} className={inputCls(false)}>
                <option value="">Select…</option>
                {BRANCHES.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </Field>
          </div>

          {/* Batch year + Age — 2 column */}
          <div className="grid grid-cols-2 gap-4">
            <Field label="Batch Year" icon={<Calendar className="w-4 h-4" />} error={errors.BatchYear}>
              <input
                type="number"
                placeholder="e.g. 2023"
                min={2000}
                max={2030}
                value={form.BatchYear}
                onChange={e => set('BatchYear', e.target.value)}
                className={inputCls(!!errors.BatchYear)}
              />
            </Field>

            <Field label="Age (optional)" icon={<User className="w-4 h-4" />}>
              <input
                type="number"
                placeholder="e.g. 20"
                min={16}
                max={40}
                value={form.Age}
                onChange={e => set('Age', e.target.value)}
                className={inputCls(false)}
              />
            </Field>
          </div>

          {/* Gender toggle */}
          <div>
            <label className="block text-sm font-semibold text-slate-600 mb-2">Gender</label>
            <div className="grid grid-cols-2 gap-3">
              {([['M', 'Male', <Mars className="w-4 h-4" />], ['F', 'Female', <Venus className="w-4 h-4" />]] as const).map(
                ([val, label, icon]) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => set('Gender', val)}
                    className={`flex items-center justify-center gap-2 py-3 rounded-2xl border-2 font-semibold text-sm transition-all ${form.Gender === val
                      ? val === 'F'
                        ? 'bg-pink-50 border-pink-300 text-pink-600'
                        : 'bg-blue-50 border-blue-300 text-blue-600'
                      : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-slate-300'
                      }`}
                  >
                    {icon} {label}
                  </button>
                )
              )}
            </div>
            {errors.Gender && <p className="text-xs text-red-500 mt-1">{errors.Gender}</p>}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white font-bold rounded-2xl transition-all shadow-xl shadow-slate-900/10 active:scale-[0.98] mt-2"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Creating account…
              </span>
            ) : 'Join IITGN Pool →'}
          </button>
        </form>
      </div>
    </div>
  );
};

// ── Helpers ──────────────────────────────────────────────────────────────────

const inputCls = (hasError: boolean) =>
  `w-full px-4 py-3 bg-slate-50 border rounded-xl text-sm text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all ${hasError ? 'border-red-300 bg-red-50' : 'border-slate-200'
  }`;

const Field: React.FC<{
  label: string;
  icon?: React.ReactNode;
  error?: string;
  children: React.ReactNode;
}> = ({ label, icon, error, children }) => (
  <div>
    <label className="flex items-center gap-1.5 text-sm font-semibold text-slate-600 mb-1.5">
      {icon && <span className="text-slate-400">{icon}</span>}
      {label}
    </label>
    {children}
    {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
  </div>
);