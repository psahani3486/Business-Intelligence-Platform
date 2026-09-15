"use client";

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface KPICardProps {
  title: string;
  value: string;
  trend?: string;
  isPositive?: boolean;
  icon?: ReactNode;
  delay?: number;
}

export default function KPICard({ title, value, trend, isPositive, icon, delay = 0 }: KPICardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="card"
      style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div className="kpi-label">{title}</div>
        {icon && <div style={{ color: 'var(--accent-blue)' }}>{icon}</div>}
      </div>
      
      <div>
        <div className="kpi-value">{value}</div>
        {trend && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px',
            fontSize: '0.875rem',
            fontWeight: 500
          }}>
            <span className={isPositive ? 'trend-up' : 'trend-down'}>
              {isPositive ? '↑' : '↓'} {trend}
            </span>
            <span style={{ color: 'var(--text-muted)' }}>vs last month</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
