import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, ShoppingCart, Zap, Star, ShieldAlert, ChevronDown, ChevronUp, Link2, Info, Eye } from 'lucide-react';

export default function RecommendationCard({ rec, onInteract, activeCustomerId, onViewDetails }) {
  const [showXAI, setShowXAI] = useState(false);
  const [userFeedback, setUserFeedback] = useState(null); // 'like', 'dislike', 'cart', 'buy'

  const prod = rec.product;
  const exp = rec.explanation || {};
  const scoreBreakdown = rec.score_breakdown || {};
  const confidencePct = Math.round((rec.confidence || 0.85) * 100);

  const handleAction = async (e, actionType) => {
    e.stopPropagation();
    setUserFeedback(actionType);
    await onInteract(activeCustomerId, prod.id, actionType);
  };

  return (
    <div
      onClick={() => onViewDetails && onViewDetails(prod)}
      className="tactile-card rounded overflow-hidden flex flex-col justify-between group cursor-pointer"
    >
      {/* Product Image & Badges */}
      <div>
        <div className="relative h-48 sm:h-52 w-full overflow-hidden bg-zinc-950">
          <img
            src={prod.image_url}
            alt={prod.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-zinc-950/75 via-transparent to-transparent" />

          {/* AI Match Badge */}
          <div className="absolute top-3 left-3">
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-zinc-950/90 text-zinc-100 border border-zinc-800 shadow-lg">
              {confidencePct}% Match
            </span>
          </div>

          {/* High Value Guardrail Flag */}
          {prod.high_value && (
            <div className="absolute top-3 right-3 flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-900/90 text-zinc-300 border border-zinc-800 text-[9px] font-medium">
              <ShieldAlert className="w-3 h-3 text-zinc-400" />
              <span>High Value</span>
            </div>
          )}

          {/* Price & Rating Overlay */}
          <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
            <span className="text-base font-bold text-zinc-100">
              ${prod.price.toFixed(2)}
            </span>
            <div className="flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-900/95 border border-zinc-850 text-zinc-300 text-xs font-medium">
              <Star className="w-3 h-3 text-zinc-400 fill-zinc-400" />
              <span>{prod.rating}</span>
            </div>
          </div>
        </div>

        {/* Content & Details */}
        <div className="p-4">
          <div className="text-[10px] font-mono text-zinc-550 uppercase mb-1">
            {prod.category} • {rec.primary_driver || 'Hybrid'}
          </div>
          <h3 className="text-xs font-semibold text-zinc-200 line-clamp-1 group-hover:text-zinc-100 transition-colors">
            {prod.title}
          </h3>

          <p className="text-[11px] text-zinc-450 line-clamp-2 mt-1 leading-relaxed">
            {prod.description}
          </p>

          {/* Explanation Hook (Primary Reason) */}
          <div className="mt-3 p-2.5 rounded bg-zinc-950 border border-zinc-850">
            <p className="text-[10px] text-zinc-300 leading-normal font-medium italic">
              "{exp.headline_explanation || 'Tailored to match your active shopping profile.'}"
            </p>
          </div>

          {/* Expand Detailed XAI & Citations Toggle */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowXAI(!showXAI);
            }}
            className="w-full mt-3 flex items-center justify-center gap-1 py-1 rounded text-[10px] font-mono text-zinc-500 hover:text-zinc-300 transition-colors border border-zinc-850"
          >
            <span>{showXAI ? 'Hide Reasoning' : 'Reasoning & Citations'}</span>
            {showXAI ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>

          {/* Expanded XAI Drawer */}
          {showXAI && (
            <div className="mt-3 p-3 rounded bg-zinc-950 border border-zinc-850 text-xs space-y-2.5 animate-fadeIn">
              {/* Supporting Reasons */}
              <div>
                <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-wider block mb-1">
                  Supporting Signals:
                </span>
                <ul className="space-y-1 text-zinc-400 text-[11px]">
                  {exp.key_reasons?.map((r, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-zinc-500">•</span>
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Data Citations */}
              {exp.citations && exp.citations.length > 0 && (
                <div>
                  <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-wider block mb-1 flex items-center gap-1">
                    <Link2 className="w-3 h-3 text-zinc-550" />
                    Citations:
                  </span>
                  <div className="space-y-1">
                    {exp.citations?.map((cite, i) => (
                      <div key={i} className="px-2 py-1 rounded bg-zinc-900 text-[10px] font-mono text-zinc-400 border border-zinc-850 truncate" title={cite}>
                        {cite}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Score Component Breakdown */}
              {scoreBreakdown && (
                <div>
                  <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-wider block mb-1">
                    Attribution Weights:
                  </span>
                  <div className="grid grid-cols-2 gap-1 text-[10px] text-zinc-500 font-mono">
                    <div>Content: <span className="text-zinc-350">{scoreBreakdown.content_based || 0}</span></div>
                    <div>Neural CF: <span className="text-zinc-350">{scoreBreakdown.neural_cf || 0}</span></div>
                    <div>SVD Latent: <span className="text-zinc-350">{scoreBreakdown.svd_factor || 0}</span></div>
                    <div>CF Score: <span className="text-zinc-350">{scoreBreakdown.user_cf || scoreBreakdown.item_cf || 0}</span></div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Interactive Telemetry Action Buttons */}
      <div className="p-4 pt-0 border-t border-zinc-800/60 mt-2">
        <div className="grid grid-cols-4 gap-1.5 pt-3">
          <button
            onClick={(e) => handleAction(e, 'like')}
            title="Like Recommendation"
            className={`flex items-center justify-center gap-1 py-1.5 rounded text-[10px] font-medium transition-all tactile-btn ${
              userFeedback === 'like'
                ? 'bg-zinc-150 text-zinc-950 font-semibold'
                : 'bg-zinc-950 text-zinc-450 hover:bg-zinc-800 border border-zinc-800/60'
            }`}
          >
            <ThumbsUp className="w-3 h-3" />
            <span className="hidden sm:inline">Like</span>
          </button>

          <button
            onClick={(e) => handleAction(e, 'dislike')}
            title="Dislike / Dismiss"
            className={`flex items-center justify-center gap-1 py-1.5 rounded text-[10px] font-medium transition-all tactile-btn ${
              userFeedback === 'dislike'
                ? 'bg-zinc-800 text-zinc-100 font-semibold'
                : 'bg-zinc-950 text-zinc-450 hover:bg-zinc-800 border border-zinc-800/60'
            }`}
          >
            <ThumbsDown className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={(e) => handleAction(e, 'add_to_cart')}
            title="Add to Shopping Cart"
            className={`flex items-center justify-center gap-1 py-1.5 rounded text-[10px] font-medium transition-all tactile-btn ${
              userFeedback === 'add_to_cart'
                ? 'bg-zinc-150 text-zinc-950 font-semibold border border-zinc-300'
                : 'bg-zinc-950 text-zinc-300 hover:bg-zinc-800 border border-zinc-800/60'
            }`}
          >
            <ShoppingCart className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Cart</span>
          </button>

          <button
            onClick={(e) => handleAction(e, 'purchase')}
            title="Simulate Instant Purchase"
            className="flex items-center justify-center gap-1 py-1.5 rounded text-[10px] font-semibold bg-zinc-100 hover:bg-zinc-200 text-zinc-950 transition-all tactile-btn"
          >
            <Zap className="w-3 h-3" />
            <span>Buy</span>
          </button>
        </div>
      </div>
    </div>
  );
}
