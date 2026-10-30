import React from 'react';
import { Activity, ShoppingCart, Eye, ShoppingBag } from 'lucide-react';

export default function RealtimeTelemetry({ customer, onInteract }) {
  if (!customer) return null;

  const browsedCount = customer.recent_browsed?.length || 0;
  const cartCount = customer.cart?.length || 0;
  const purchaseCount = customer.past_purchases?.length || 0;

  return (
    <div className="bg-zinc-950 border-t border-zinc-800/80 px-4 py-2.5 flex items-center justify-between text-xs text-zinc-500">
      <div className="max-w-7xl mx-auto w-full flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-zinc-400" />
          <span className="font-semibold text-zinc-300">Session Telemetry:</span>
          <span className="text-zinc-500 font-mono">
            {customer.name} ({customer.id})
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Eye className="w-3.5 h-3.5 text-zinc-550" />
            <span>Browsed: <strong className="text-zinc-200 font-mono">{browsedCount}</strong></span>
          </div>

          <div className="flex items-center gap-1">
            <ShoppingCart className="w-3.5 h-3.5 text-zinc-550" />
            <span>Cart: <strong className="text-zinc-200 font-mono">{cartCount}</strong></span>
          </div>

          <div className="flex items-center gap-1">
            <ShoppingBag className="w-3.5 h-3.5 text-zinc-550" />
            <span>Purchased: <strong className="text-zinc-200 font-mono">{purchaseCount}</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}
