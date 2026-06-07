import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Info, Download } from 'lucide-react';
import { format } from 'date-fns';

interface Finding {
  id: string;
  title: string;
  description: string;
  severity: string;
  quantum_relevance: string;
  file_path: string | null;
  line_number: number | null;
  evidence: string | null;
  algorithm: string | null;
  category: string;
  recommendation: string;
}

interface ScanResult {
  scan_id: string;
  project_name: string;
  created_at: string;
  q_score: number;
  readiness_label: string;
  targets: { target_type: string; value: string }[];
  findings: Finding[];
}

export default function ScanDetail() {
  const { id } = useParams();
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/${id}`)
      .then(res => res.json())
      .then(data => {
        setScan(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return <div className="loader"></div>;
  }

  if (!scan) {
    return (
      <div className="fade-in" style={{ textAlign: 'center', marginTop: '100px' }}>
        <AlertTriangle size={48} className="text-muted" style={{ margin: '0 auto 20px' }} />
        <h2>Scan Not Found</h2>
        <Link to="/" className="btn" style={{ marginTop: '20px' }}>Back to Dashboard</Link>
      </div>
    );
  }

  const highCount = scan.findings.filter(f => ['high', 'critical'].includes(f.severity)).length;
  const medCount = scan.findings.filter(f => f.severity === 'medium').length;

  return (
    <div className="fade-in">
      <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', textDecoration: 'none', marginBottom: '24px', fontWeight: 500 }}>
        <ArrowLeft size={18} /> Back to Dashboard
      </Link>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h1>Scan: {scan.project_name}</h1>
          <p className="text-muted" style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <span>{format(new Date(scan.created_at), 'PPP pp')}</span>
            <span>ID: {scan.scan_id}</span>
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '3rem', fontWeight: 800, lineHeight: 1, color: `var(--score-${scan.readiness_label.toLowerCase()})` }}>
            {scan.q_score}
          </div>
          <span className={`badge badge-${scan.readiness_label.toLowerCase()}`}>{scan.readiness_label}</span>
        </div>
      </div>

      <div className="grid-3" style={{ marginBottom: '32px' }}>
        <div className="glass-panel">
          <h3 className="text-muted" style={{ fontSize: '0.8rem', textTransform: 'uppercase' }}>Targets</h3>
          {scan.targets.map((t, i) => (
            <div key={i} style={{ fontWeight: 600, marginTop: '8px' }}>
              <span className="badge badge-info" style={{ marginRight: '8px', background: 'rgba(59,130,246,0.2)', color: '#60a5fa' }}>{t.target_type}</span>
              {t.value}
            </div>
          ))}
        </div>
        <div className="glass-panel stat-card">
          <div className="text-muted" style={{ textTransform: 'uppercase', fontSize: '0.8rem', fontWeight: 600 }}>High / Critical Risks</div>
          <div className="stat-value" style={{ color: highCount > 0 ? 'var(--score-critical)' : 'inherit' }}>{highCount}</div>
        </div>
        <div className="glass-panel stat-card">
          <div className="text-muted" style={{ textTransform: 'uppercase', fontSize: '0.8rem', fontWeight: 600 }}>Medium Risks</div>
          <div className="stat-value" style={{ color: medCount > 0 ? 'var(--score-moderate)' : 'inherit' }}>{medCount}</div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Findings ({scan.findings.length})</h2>
        <button className="btn btn-secondary" onClick={() => alert('PDF export coming soon!')}>
          <Download size={18} /> Export Report
        </button>
      </div>

      {scan.findings.length === 0 ? (
        <div className="glass-panel text-muted" style={{ textAlign: 'center', padding: '40px' }}>
          <Info size={32} style={{ margin: '0 auto 16px' }} />
          No cryptographic usage found in this scan.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {scan.findings.map(f => (
            <div key={f.id} className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <h3 style={{ margin: 0, fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span className={`badge badge-${f.severity}`}>{f.severity}</span>
                  {f.title}
                </h3>
                {f.quantum_relevance !== 'none' && (
                  <span className="badge badge-critical" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                    PQ Relevance: {f.quantum_relevance}
                  </span>
                )}
              </div>
              
              <p style={{ color: 'var(--text-secondary)' }}>{f.description}</p>
              
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px', marginTop: '16px', border: '1px solid var(--border-color)' }}>
                {f.file_path && (
                  <div style={{ marginBottom: '8px', fontFamily: 'monospace', color: '#94a3b8' }}>
                    <strong>File:</strong> {f.file_path}{f.line_number ? `:${f.line_number}` : ''}
                  </div>
                )}
                {f.evidence && (
                  <pre style={{ margin: 0, padding: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', overflowX: 'auto', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <code style={{ color: '#e2e8f0' }}>{f.evidence}</code>
                  </pre>
                )}
              </div>

              <div style={{ marginTop: '20px', paddingLeft: '16px', borderLeft: '3px solid var(--accent-color)' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '0.9rem', color: '#fff', textTransform: 'uppercase' }}>Recommendation</h4>
                <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{f.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
