import React from 'react';
import { 
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Cell,
  ComposedChart, Bar
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f43f5e', '#8b5cf6', '#f59e0b'];

export const CohortScatterPlot = ({ data = [] }: { data?: any[] }) => {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return <div style={{ color: 'var(--text-muted)', padding: '20px', textAlign: 'center' }}>Loading cohort clusters...</div>;
  }
  
  const clusters = Array.from(new Set(data.map(d => d.cluster)));
  
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis type="number" dataKey="x" name="Recency" unit=" days" stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)' }} />
          <YAxis type="number" dataKey="y" name="Monetary" unit="$" stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)' }} />
          <ZAxis type="number" dataKey="z" range={[50, 400]} name="Frequency" />
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }} 
            contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
            itemStyle={{ color: '#fff' }}
          />
          {clusters.map((cName, i) => (
            <Scatter key={cName} name={cName} data={data.filter(d => d.cluster === cName)} fill={COLORS[i % COLORS.length]} opacity={0.8} />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export const CategoryRadarChart = ({ data = [] }: { data?: any[] }) => {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return <div style={{ color: 'var(--text-muted)', padding: '20px', textAlign: 'center' }}>Loading radar analysis...</div>;
  }

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ResponsiveContainer>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar name="Category Perf" dataKey="A" stroke="var(--accent-blue)" fill="var(--accent-blue)" fillOpacity={0.4} />
          <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid var(--border-color)', borderRadius: '8px' }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export const RevenueWaterfallChart = ({ data = [] }: { data?: any[] }) => {
  const chartData = Array.isArray(data) && data.length > 0 ? data : [
    { name: "Gross Rev", base: 0, value: 16008872.0, isTotal: true },
    { name: "Returns", base: 15448561.48, value: -560310.52, isTotal: false },
    { name: "Discounts", base: 15112375.17, value: -336186.31, isTotal: false },
    { name: "Shipping", base: 15112375.17, value: 2273259.82, isTotal: false },
    { name: "Net Rev", base: 0, value: 17385634.99, isTotal: true }
  ];

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ResponsiveContainer>
        <ComposedChart margin={{ top: 20, right: 30, left: 20, bottom: 5 }} data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="name" stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
          <YAxis stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} tickFormatter={(val) => `$${val/1000}k`} />
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
            itemStyle={{ color: '#fff' }}
            formatter={(value: any) => `$${Number(value).toLocaleString()}`}
          />
          <Bar dataKey="base" stackId="a" fill="transparent" />
          <Bar dataKey="value" stackId="a" fill="var(--accent-emerald)">
            {
              chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.isTotal ? 'var(--accent-blue)' : (entry.value < 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)')} />
              ))
            }
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export const ActivityHeatmap = ({ data = [] }: { data?: number[][] }) => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  
  const heatmapData = Array.isArray(data) && data.length > 0 ? data : Array.from({ length: 7 }, () => Array.from({ length: 24 }, () => Math.floor(Math.random() * 80)));

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {heatmapData.map((dayData, dayIdx) => (
        <div key={dayIdx} style={{ display: 'flex', alignItems: 'center', gap: '4px', flex: 1 }}>
          <div style={{ width: '30px', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'right' }}>{days[dayIdx]}</div>
          <div style={{ display: 'flex', flex: 1, gap: '2px', height: '100%' }}>
            {Array.isArray(dayData) && dayData.map((val, hrIdx) => {
              const opacity = Math.max(0.1, val / 100);
              return (
                <div 
                  key={hrIdx} 
                  title={`Hour: ${hrIdx}, Activity: ${val}`}
                  style={{ 
                    flex: 1, 
                    backgroundColor: `rgba(59, 130, 246, ${opacity})`, 
                    borderRadius: '2px',
                    transition: 'all 0.2s',
                    cursor: 'pointer'
                  }} 
                  className="hover:scale-110"
                />
              );
            })}
          </div>
        </div>
      ))}
      <div style={{ display: 'flex', marginLeft: '34px', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
        <span>12 AM</span>
        <span>12 PM</span>
        <span>11 PM</span>
      </div>
    </div>
  );
};
