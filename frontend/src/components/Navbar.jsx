import React, { useState } from 'react';
import { ShoppingBag, ShieldCheck, BarChart3, Bot, ChevronDown, Activity, Sparkles } from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  customers,
  activeCustomer,
  onSelectCustomer,
  showConcierge,
  setShowConcierge
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const navItems = [
    { id: 'storefront', label: 'Feed', icon: ShoppingBag },
    { id: 'governance', label: 'Governance', icon: ShieldCheck },
    { id: 'benchmarks', label: 'Benchmarks', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-900 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-zinc-900 border border-zinc-800 flex items-center justify-center">
            <ShoppingBag className="w-4 h-4 text-zinc-100" />
          </div>
          <div>
            <h1 className="text-xs font-bold tracking-wider text-zinc-150 uppercase font-mono">
              Recommendation.ai
            </h1>
            <p className="text-[10px] text-zinc-550 font-medium">Core Engine v2.0</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 p-1 bg-zinc-900/60 rounded border border-zinc-900">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-zinc-100 text-zinc-950 font-semibold'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Controls: Customer Dropdown + AI Dock Toggle */}
        <div className="flex items-center gap-3">
          {/* AI Dock Toggle */}
          <button
            onClick={() => setShowConcierge(!showConcierge)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold transition-all border ${
              showConcierge
                ? 'bg-zinc-100 border-zinc-200 text-zinc-950'
                : 'bg-zinc-900 border-zinc-850 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Bot className="w-3.5 h-3.5" />
            <span>AI Concierge</span>
          </button>

          {/* Customer Dropdown switcher */}
          {activeCustomer && (
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded bg-zinc-900 border border-zinc-850 text-xs font-semibold text-zinc-350 hover:bg-zinc-800 transition-colors"
              >
                <img src={activeCustomer.avatar} alt="" className="w-4 h-4 rounded-full object-cover" />
                <span className="max-w-[80px] truncate">{activeCustomer.name.split(' ')[0]}</span>
                <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 rounded bg-zinc-900 border border-zinc-850 shadow-2xl py-1 z-50">
                  <div className="px-3 py-1.5 border-b border-zinc-850 text-[10px] uppercase font-bold text-zinc-550">
                    Switch Shopper Profile
                  </div>
                  {customers.map((c) => {
                    const isSel = activeCustomer.id === c.id;
                    return (
                      <button
                        key={c.id}
                        onClick={() => {
                          onSelectCustomer(c);
                          setDropdownOpen(false);
                        }}
                        className={`w-full flex items-center gap-2 px-3 py-2 text-left text-xs transition-colors ${
                          isSel
                            ? 'bg-zinc-950 text-zinc-100 font-semibold'
                            : 'text-zinc-400 hover:bg-zinc-950 hover:text-zinc-200'
                        }`}
                      >
                        <img src={c.avatar} alt="" className="w-5 h-5 rounded-full object-cover" />
                        <div className="truncate">
                          <div className="font-semibold">{c.name}</div>
                          <div className="text-[10px] text-zinc-500 truncate">{c.persona_title}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
