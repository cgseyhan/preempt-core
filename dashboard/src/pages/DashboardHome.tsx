import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { format } from 'date-fns';

interface ScanResult {
  scan_id: string;
  project_name: string;
  created_at: string;
  q_score: number;
  readiness_label: string;
  targets: any[];
}

export default function DashboardHome() {
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api')
      .then(res => res.json())
      .then(data => {
        setScans(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="loader"></div>;
  }

  // Group by project for charts (we'll just use the first project for now or all)
  const chartData = [...scans].reverse().map(s => ({
    name: format(new Date(s.created_at), 'MMM dd, HH:mm'),
    score: s.q_score,
    project: s.project_name
  }));

  const latestScore = scans.length > 0 ? scans[0].q_score : 0;
  const label = scans.length > 0 ? scans[0].readiness_label : 'N/A';

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>Post-Quantum Readiness</h1>
          <p className="text-muted">Track your cryptographic inventory and migration progress.</p>
        </div>
      </div>

      <div className="grid-3" style={{ marginBottom: '40px' }}>
        <div className="glass-panel stat-card">
          <div className="text-muted" style={{ textTransform: 'uppercase', fontSize: '0.8rem', fontWeight: 600 }}>Total Scans</div>
          <div className="stat-value">{scans.length}</div>
        </div>
        <div className="glass-panel stat-card">
          <div className="text-muted" style={{ textTransform: 'uppercase', fontSize: '0.8rem', fontWeight: 600 }}>Latest Q-Score</div>
          <div className="stat-value" style={{ color: `var(--score-${label.toLowerCase()})` }}>{latestScore}</div>
        </div>
        <div className="glass-panel stat-card">
          <div className="text-muted" style={{ textTransform: 'uppercase', fontSize: '0.8rem', fontWeight: 600 }}>Readiness Label</div>
          <div className="stat-value" style={{ fontSize: '1.8rem', marginTop: '10px' }}>
            <span className={`badge badge-${label.toLowerCase()}`} style={{ fontSize: '1rem', padding: '8px 16px' }}>{label}</span>
          </div>
        </div>
      </div>

      {scans.length > 0 && (
        <div className="glass-panel" style={{ marginBottom: '40px', height: '350px' }}>
          <h3 style={{ marginBottom: '20px' }}>Q-Score Trend</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="rgba(255,255,255,0.4)" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                itemStyle={{ color: '#fff' }}
              />
              <Line type="monotone" dataKey="score" stroke="var(--accent-color)" strokeWidth={3} dot={{ r: 4, fill: 'var(--bg-color)', strokeWidth: 2 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <h2>Scan History</h2>
      <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Project</th>
              <th>Targets</th>
              <th>Q-Score</th>
              <th>Readiness</th>
            </tr>
          </thead>
          <tbody>
            {scans.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: '40px' }} className="text-muted">No scans found.</td></tr>
            ) : (
              scans.map(scan => (
                <tr key={scan.scan_id} onClick={() => window.location.href=`/scan/${scan.scan_id}`}>
                  <td>{format(new Date(scan.created_at), 'MMM dd, yyyy HH:mm')}</td>
                  <td style={{ fontWeight: 600 }}>{scan.project_name}</td>
                  <td>{scan.targets.length} target(s)</td>
                  <td style={{ fontWeight: 'bold' }}>{scan.q_score}</td>
                  <td>
                    <span className={`badge badge-${scan.readiness_label.toLowerCase()}`}>
                      {scan.readiness_label}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
