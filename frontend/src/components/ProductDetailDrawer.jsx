import React from 'react';
import { X, ShoppingCart, ShieldCheck, Star, Sparkles, Layers } from 'lucide-react';

export default function ProductDetailDrawer({ product, customer, onClose, onInteract }) {
  if (!product) return null;

  // Generate dynamic, context-aware AI insights based on the product metadata and customer persona
  const getAIInsights = () => {
    const category = product.category || 'General';
    const insights = {
      suitability: `Ideal for users matching the "${customer?.persona_title || 'General Shopper'}" profile seeking high-reliability gear in the ${category} category.`,
      strengths: product.tags?.slice(0, 3) || ['High Performance', 'Premium Build Quality'],
      limitations: ['Requires initial calibration', 'Premium price point'],
      valueForMoney: product.price > 300 ? 'Premium investment with high longevity' : 'Excellent entry-level value utility',
      alternatives: `Often compared with other top-tier ${category} items. Fits seamlessly into a seasonal ${customer?.location || 'urban'} lifestyle.`
    };

    return insights;
  };

  const insights = getAIInsights();

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-2xl bg-zinc-950 border-l border-zinc-800 shadow-2xl flex flex-col justify-between animate-slideIn">
      {/* Header */}
      <div className="p-4 border-b border-zinc-900 flex items-center justify-between bg-zinc-900/50">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-zinc-400" />
          <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">AI Product Assessment</span>
        </div>
        <button onClick={onClose} className="p-1 rounded hover:bg-zinc-855 text-zinc-450 hover:text-zinc-100 transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
        {/* Product Visual & Basic Info */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div className="h-64 rounded bg-zinc-900 border border-zinc-850 overflow-hidden relative">
            <img src={product.image_url} alt={product.title} className="w-full h-full object-cover" />
            {product.high_value && (
              <span className="absolute top-2 right-2 px-2 py-0.5 rounded bg-zinc-950/80 text-[9px] font-mono text-zinc-350 border border-zinc-800">
                High Value Asset
              </span>
            )}
          </div>

          <div className="flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-mono uppercase text-zinc-550">{product.category}</span>
              <h2 className="text-base font-semibold text-zinc-100 mt-1 leading-tight">{product.title}</h2>
              <div className="flex items-center gap-1.5 mt-2">
                <div className="flex items-center text-zinc-300 text-xs">
                  <Star className="w-3.5 h-3.5 fill-zinc-400 text-zinc-405 mr-1" />
                  <span>{product.rating}</span>
                </div>
                <span className="text-zinc-500 text-[11px]">({product.review_count} reviews)</span>
              </div>
            </div>

            <div className="pt-4 border-t border-zinc-900 mt-4">
              <div className="text-[10px] text-zinc-550">Retail Price</div>
              <div className="text-xl font-bold text-zinc-100 mt-0.5">${product.price.toFixed(2)}</div>
              <button
                onClick={() => {
                  onInteract(customer?.id, product.id, 'add_to_cart');
                }}
                className="w-full mt-3 py-2 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-950 font-semibold text-xs transition-colors flex items-center justify-center gap-1.5"
              >
                <ShoppingCart className="w-4 h-4" />
                <span>Add to Shopping Cart</span>
              </button>
            </div>
          </div>
        </div>

        {/* Product Description */}
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Description</h3>
          <p className="text-xs text-zinc-450 leading-relaxed">{product.description}</p>
        </div>

        {/* AI Insight Section (Premium Editorial Style) */}
        <div className="p-5 rounded bg-zinc-900 border border-zinc-850 space-y-4">
          <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
            <Sparkles className="w-4 h-4 text-zinc-300" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">AI Concierge Insights</h3>
          </div>

          {/* Suitability */}
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-zinc-500">Target Compatibility</span>
            <p className="text-xs text-zinc-350 leading-relaxed">{insights.suitability}</p>
          </div>

          {/* Strengths & Limitations */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="space-y-1.5">
              <span className="text-[9px] uppercase font-bold text-zinc-550">Primary Strengths</span>
              <div className="space-y-1">
                {insights.strengths.map((str, i) => (
                  <span key={i} className="block text-[10px] px-2 py-0.5 rounded bg-zinc-950 text-zinc-350 border border-zinc-850 truncate">
                    + {str}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-1.5">
              <span className="text-[9px] uppercase font-bold text-zinc-550">Known Trade-offs</span>
              <div className="space-y-1">
                {insights.limitations.map((lim, i) => (
                  <span key={i} className="block text-[10px] px-2 py-0.5 rounded bg-zinc-950 text-zinc-450 border border-zinc-850 truncate">
                    • {lim}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Value Analysis */}
          <div className="grid grid-cols-2 gap-4 pt-2 border-t border-zinc-800/60">
            <div className="space-y-1">
              <span className="text-[9px] uppercase font-bold text-zinc-550">Value Proposition</span>
              <p className="text-[11px] text-zinc-300">{insights.valueForMoney}</p>
            </div>

            <div className="space-y-1">
              <span className="text-[9px] uppercase font-bold text-zinc-550">Market Alternatives</span>
              <p className="text-[11px] text-zinc-400">{insights.alternatives}</p>
            </div>
          </div>
        </div>

        {/* Specifications */}
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Specifications</h3>
          <div className="border border-zinc-900 rounded overflow-hidden divide-y divide-zinc-900 text-xs">
            <div className="grid grid-cols-2 p-2.5 bg-zinc-900/20">
              <span className="text-zinc-500 font-medium">Model ID</span>
              <span className="text-zinc-350 font-mono">{product.id}</span>
            </div>
            <div className="grid grid-cols-2 p-2.5">
              <span className="text-zinc-500 font-medium">Product Class</span>
              <span className="text-zinc-350">{product.category}</span>
            </div>
            <div className="grid grid-cols-2 p-2.5 bg-zinc-900/20">
              <span className="text-zinc-500 font-medium">Subcategory Tag</span>
              <span className="text-zinc-350">{product.subcategory || 'Standard'}</span>
            </div>
            <div className="grid grid-cols-2 p-2.5">
              <span className="text-zinc-500 font-medium">Tags</span>
              <span className="text-zinc-350 truncate">{product.tags?.join(', ')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-900 bg-zinc-900/50 flex items-center justify-between text-[11px] text-zinc-500">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-zinc-500" />
          <span>Immutable Session Audit Logged</span>
        </div>
        <span>ID: {product.id}</span>
      </div>
    </div>
  );
}
