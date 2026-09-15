"use client";

import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface ChartProps {
  title: string;
  data: any[];
  delay?: number;
}

export function RevenueChart({ title, data, delay = 0 }: ChartProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="card col-span-8"
      style={{ height: '400px' }}
    >
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '24px' }}>{title}</h3>
      <div style={{ width: '100%', height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--accent-blue)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="var(--accent-blue)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
            <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis 
              stroke="var(--text-muted)" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false}
              tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`}
            />
            <Tooltip 
              contentStyle={{ background: 'var(--bg-secondary)', border: 'var(--glass-border)', borderRadius: '8px', color: '#fff' }}
              itemStyle={{ color: 'var(--accent-blue)' }}
              formatter={(value: any) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
            />
            <Area type="monotone" dataKey="value" stroke="var(--accent-blue)" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export function CustomerGrowthChart({ title, data, delay = 0, modelType = 'xgboost' }: ChartProps & { modelType?: 'xgboost' | 'prophet' }) {
  // data is expected to be an array of { ds, new_customers, returning_customers, mau, growth_rate }
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="card col-span-8"
      style={{ height: '400px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{title} ({modelType.toUpperCase()})</h3>
        <div style={{ display: 'flex', gap: '12px', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'var(--accent-purple)' }}></div>
            <span>New</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'var(--accent-emerald)' }}></div>
            <span>Returning</span>
          </div>
        </div>
      </div>
      <div style={{ width: '100%', height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorNew" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--accent-purple)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="var(--accent-purple)" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorReturning" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--accent-emerald)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="var(--accent-emerald)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
            <XAxis 
              dataKey="ds" 
              stroke="var(--text-muted)" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false} 
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth()+1}/${date.getDate()}`;
              }}
            />
            <YAxis 
              stroke="var(--text-muted)" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false}
              tickFormatter={(value) => `${(value).toFixed(0)}`}
            />
            <Tooltip 
              contentStyle={{ background: 'var(--bg-secondary)', border: 'var(--glass-border)', borderRadius: '8px', color: '#fff' }}
              itemStyle={{ color: '#fff' }}
              labelFormatter={(label) => new Date(label as string).toLocaleDateString()}
            />
            <Area type="monotone" dataKey="returning_customers" name="Returning" stackId="1" stroke="var(--accent-emerald)" strokeWidth={2} fillOpacity={1} fill="url(#colorReturning)" />
            <Area type="monotone" dataKey="new_customers" name="New" stackId="1" stroke="var(--accent-purple)" strokeWidth={2} fillOpacity={1} fill="url(#colorNew)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
