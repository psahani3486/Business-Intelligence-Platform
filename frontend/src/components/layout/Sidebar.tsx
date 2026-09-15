"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  TrendingUp, 
  Users, 
  FileText,
  BarChart3,
  X
} from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Sales & Performance', path: '/sales', icon: TrendingUp },
  { name: 'Customer Insights', path: '/customers', icon: Users },
  { name: 'Reports & Export', path: '/reports', icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();

  const closeMobileSidebar = () => {
    if (typeof document !== 'undefined') {
      document.body.classList.remove('sidebar-open');
    }
  };

  return (
    <aside className="app-sidebar" style={{
      width: 'var(--sidebar-width)',
      height: '100vh',
      position: 'fixed',
      left: 0,
      top: 0,
      display: 'flex',
      flexDirection: 'column',
      borderRight: 'var(--glass-border)',
      background: 'rgba(7, 11, 20, 0.98)',
      backdropFilter: 'blur(20px)',
      padding: '24px 16px',
      zIndex: 40,
      transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
    }}>
      {/* Brand Header */}
      <div style={{ padding: '0 8px 24px 8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ 
            width: '36px', 
            height: '36px', 
            borderRadius: '10px', 
            background: 'linear-gradient(135deg, #0284c7, #38bdf8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 800,
            fontSize: '15px',
            boxShadow: '0 0 16px rgba(56, 189, 248, 0.25)'
          }}>
            <BarChart3 size={20} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '6px', margin: 0 }}>
              Pulse BI
            </h1>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Retail Analytics</span>
          </div>
        </div>

        <button 
          onClick={closeMobileSidebar}
          className="mobile-menu-btn"
          aria-label="Close Sidebar"
          style={{ 
            background: 'transparent', 
            border: 'none', 
            color: 'var(--text-secondary)', 
            cursor: 'pointer',
            display: 'none',
            padding: '4px'
          }}
        >
          <X size={22} />
        </button>
      </div>

      {/* Navigation Links */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, paddingRight: '4px' }}>
        <div style={{ 
          fontSize: '0.6875rem', 
          fontWeight: 800, 
          color: 'var(--text-muted)', 
          letterSpacing: '0.1em', 
          padding: '0 12px 4px 12px',
          textTransform: 'uppercase'
        }}>
          MENU
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const isActive = pathname === item.path;
            return (
              <Link href={item.path} key={item.path} onClick={closeMobileSidebar}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 14px',
                  borderRadius: '10px',
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  background: isActive ? 'linear-gradient(90deg, rgba(56, 189, 248, 0.15) 0%, rgba(56, 189, 248, 0.05) 100%)' : 'transparent',
                  borderLeft: isActive ? '3px solid var(--accent-blue)' : '3px solid transparent',
                  transition: 'all 0.2s ease',
                  fontWeight: isActive ? 700 : 500,
                  cursor: 'pointer',
                  position: 'relative'
                }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <item.icon size={18} color={isActive ? 'var(--accent-blue)' : 'currentColor'} />
                    <span style={{ fontSize: '0.875rem' }}>{item.name}</span>
                  </div>

                  {isActive && (
                    <motion.div 
                      layoutId="sidebar-active"
                      style={{ position: 'absolute', right: 8, width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-blue)', boxShadow: '0 0 8px var(--accent-blue)' }}
                    />
                  )}
                </div>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
