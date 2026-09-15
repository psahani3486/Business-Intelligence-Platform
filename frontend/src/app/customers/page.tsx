"use client";

import { PageHeader } from '@/components/ui/PageHeader';
import KPICard from '@/components/dashboard/KPICard';
import { UserMinus, ShieldAlert, Award, Search, Send, Filter } from 'lucide-react';
import { useEffect, useState } from 'react';
import api from '@/lib/api';

export default function CustomersPage() {
  const [churnPredictions, setChurnPredictions] = useState<any[]>([]);
  const [clvSegments, setClvSegments] = useState<any>({ "High Value": 0, "Medium Value": 0, "Low Value": 0 });
  const [loading, setLoading] = useState(true);
  const [filterRisk, setFilterRisk] = useState<'ALL' | 'HIGH' | 'MEDIUM'>('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/churn/predictions'),
      api.get('/clv/segments')
    ]).then(([churnRes, clvRes]) => {
      setChurnPredictions(churnRes.data);
      setClvSegments(clvRes.data);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const totalHighValue = clvSegments["High Value"] || 0;
  const highRiskCount = churnPredictions.filter(p => p.prediction === 'High Risk').length;

  const filteredPredictions = churnPredictions.filter(pred => {
    const matchesRisk = 
      filterRisk === 'ALL' ? true :
      filterRisk === 'HIGH' ? pred.prediction === 'High Risk' :
      pred.prediction === 'Medium Risk';
    const matchesSearch = pred.customer_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesRisk && matchesSearch;
  });

  const handleRetentionOffer = (customerId: string) => {
    alert(`Targeted 15% retention offer dispatched to Customer ${customerId}`);
  };

  return (
    <main className="page-container">
      <PageHeader 
        title="Customer Intelligence & Churn Prevention" 
        subtitle="XGBoost Churn Risk Scoring, SHAP Factor Explanations, and CLV Segments" 
      />
      
      <div className="dashboard-grid">
        <div className="col-span-4">
          <KPICard title="High Churn Risk" value={highRiskCount.toString()} trend="Requires Action" isPositive={false} icon={<UserMinus />} delay={0.1} />
        </div>
        <div className="col-span-4">
          <KPICard title="High Value Customers" value={totalHighValue.toLocaleString()} trend="Predicted by XGBoost" isPositive={true} icon={<Award />} delay={0.2} />
        </div>
        <div className="col-span-4">
          <KPICard title="Total Customers Evaluated" value={churnPredictions.length.toString()} trend="Active Scoring" isPositive={true} icon={<ShieldAlert />} delay={0.3} />
        </div>
        
        <div className="card col-span-12" style={{ marginTop: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>At-Risk Customers (SHAP Risk Explanations)</h3>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '6px 12px' }}>
                <Search size={16} color="var(--text-muted)" style={{ marginRight: '8px' }} />
                <input 
                  type="text" 
                  placeholder="Search customer ID..." 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#fff', outline: 'none', fontSize: '0.875rem' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '6px', background: 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                {(['ALL', 'HIGH', 'MEDIUM'] as const).map((r) => (
                  <button
                    key={r}
                    onClick={() => setFilterRisk(r)}
                    style={{
                      background: filterRisk === r ? 'var(--accent-blue)' : 'transparent',
                      color: filterRisk === r ? '#fff' : 'var(--text-secondary)',
                      border: 'none',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', minWidth: '850px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.8125rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <th style={{ padding: '14px' }}>Customer ID</th>
                  <th style={{ padding: '14px' }}>Risk Score</th>
                  <th style={{ padding: '14px' }}>Prediction</th>
                  <th style={{ padding: '14px' }}>Top SHAP Risk Factors</th>
                  <th style={{ padding: '14px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredPredictions.map((pred) => (
                  <tr key={pred.customer_id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.2s ease' }}>
                    <td style={{ padding: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>{pred.customer_id}</td>
                    <td style={{ padding: '14px', fontWeight: 700, color: pred.risk_score > 0.7 ? 'var(--accent-rose)' : 'var(--accent-amber)' }}>
                      {(pred.risk_score * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: '14px' }}>
                      <span className={pred.risk_score > 0.7 ? "badge badge-rose" : "badge badge-amber"}>
                        {pred.prediction}
                      </span>
                    </td>
                    <td style={{ padding: '14px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                      {pred.top_factors.map((f: any) => `${f.name}: ${f.value}`).join(' • ')}
                    </td>
                    <td style={{ padding: '14px' }}>
                      <button 
                        onClick={() => handleRetentionOffer(pred.customer_id)}
                        className="btn-secondary"
                        style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                      >
                        <Send size={12} /> Send Offer
                      </button>
                    </td>
                  </tr>
                ))}
                {!loading && filteredPredictions.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No customer risk records match search criteria.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
