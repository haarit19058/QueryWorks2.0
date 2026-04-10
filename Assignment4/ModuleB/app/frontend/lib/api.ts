import axios from 'axios';

const api = axios.create({
  baseURL: process.env.VITE_API_URL,
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const is401 = error.response?.status === 401;
    const isAuthMe = error.config?.url?.includes('/auth/me');
    const onLoginPage = window.location.pathname === '/login';

    // Only force-redirect if:
    // - it's a 401
    // - it's NOT the session check (/auth/me)
    // - user is not already on login page
    if (is401 && !isAuthMe && !onLoginPage) {
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export default api;