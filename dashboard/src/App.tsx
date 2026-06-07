import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Activity, ShieldCheck } from 'lucide-react';
import DashboardHome from './pages/DashboardHome';
import ScanDetail from './pages/ScanDetail';

function App() {
  return (
    <BrowserRouter>
      <nav className="navbar">
        <Link to="/" className="nav-brand">
          <ShieldCheck size={28} />
          <span>PreemptCore</span>
        </Link>
        <div className="nav-links">
          <Link to="/">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} /> Dashboard
            </div>
          </Link>
        </div>
      </nav>
      <main className="container fade-in">
        <Routes>
          <Route path="/" element={<DashboardHome />} />
          <Route path="/scan/:id" element={<ScanDetail />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
