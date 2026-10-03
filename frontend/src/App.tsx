import { useState } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-red-600 font-medium p-4 bg-red-50 rounded-lg shadow">Configuration Error: Missing VITE_GOOGLE_CLIENT_ID in production environment.</div>
        </div>
      );
    }
    return (
      <GoogleOAuthProvider clientId={clientId}>
        <Login onLogin={(t) => setToken(t)} />
      </GoogleOAuthProvider>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold text-primary-600">OrderGuard AI</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">Merchant Dashboard</span>
              <button
                onClick={handleLogout}
                className="cursor-pointer text-sm font-medium text-gray-700 px-3 py-1.5 rounded-md hover:text-red-600 hover:bg-red-50 transition-all active:scale-95"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1">
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
