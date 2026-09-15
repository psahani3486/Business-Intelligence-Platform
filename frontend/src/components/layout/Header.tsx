"use client";

import { Search, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const toggleSidebar = () => {
    if (typeof document !== 'undefined') {
      document.body.classList.toggle('sidebar-open');
    }
  };

  const handleSearchSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      router.push(`/sales?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header style={{
      height: 'var(--header-height)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      background: 'rgba(7, 11, 20, 0.85)',
      backdropFilter: 'blur(12px)',
      borderBottom: 'var(--glass-border)',
      position: 'sticky',
      top: 0,
      zIndex: 30
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
        <button 
          className="mobile-menu-btn" 
          onClick={toggleSidebar}
          aria-label="Toggle Navigation Menu"
          style={{ 
            background: 'rgba(255, 255, 255, 0.06)', 
            border: '1px solid var(--border-color)', 
            color: '#fff', 
            borderRadius: '8px',
            padding: '6px',
            cursor: 'pointer', 
            display: 'none',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Menu size={22} />
        </button>
        
        <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.05)', borderRadius: '24px', padding: '6px 14px', width: '100%', maxWidth: '340px', border: '1px solid var(--border-color)' }}>
          <Search size={16} color="var(--text-muted)" style={{ marginRight: '8px', flexShrink: 0 }} />
          <input 
            type="text" 
            placeholder="Search metrics, orders, or categories..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleSearchSubmit}
            style={{ 
              background: 'transparent', 
              border: 'none', 
              color: '#fff', 
              outline: 'none',
              width: '100%',
              fontSize: '0.8125rem'
            }} 
          />
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Backend Operational Status Pill */}
        <div className="badge badge-emerald" style={{ padding: '4px 10px', fontSize: '0.6875rem' }}>
          <div className="pulse-dot"></div>
          <span style={{ whiteSpace: 'nowrap' }}>API: Connected</span>
        </div>
      </div>
    </header>
  );
}
