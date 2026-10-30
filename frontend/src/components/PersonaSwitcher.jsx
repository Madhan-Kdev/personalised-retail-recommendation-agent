import React from 'react';
import { Sliders, UserCheck, DollarSign, Tag, Navigation } from 'lucide-react';

export default function PersonaSwitcher({ activeCustomer, personaSynthesis }) {
  if (!personaSynthesis) return null;

  return (
    <div className="bg-zinc-900 border border-zinc-850 rounded p-5 space-y-4">
      {/* Widget Header */}
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
        <Sliders className="w-4 h-4 text-zinc-400" />
        <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">
          AI Persona Synthesis
        </h3>
      </div>

      {/* Narrative Profile */}
      <div className="space-y-1.5">
        <span className="text-[9px] uppercase font-bold text-zinc-550">Dynamic Profile Narrative</span>
        <p className="text-xs text-zinc-400 leading-relaxed font-normal">
          {personaSynthesis.narrative_profile}
        </p>
      </div>

      {/* Target Telemetry Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
        <div className="p-2.5 rounded bg-zinc-950 border border-zinc-850">
          <div className="text-[9px] font-semibold text-zinc-550 uppercase">Income Bracket</div>
          <div className="text-xs font-bold text-zinc-350 mt-0.5 truncate flex items-center gap-1">
            <UserCheck className="w-3.5 h-3.5 text-zinc-500" />
            <span>{personaSynthesis.demographic_summary}</span>
          </div>
        </div>

        <div className="p-2.5 rounded bg-zinc-950 border border-zinc-850">
          <div className="text-[9px] font-semibold text-zinc-550 uppercase">Price Sensitivity</div>
          <div className="text-xs font-bold text-zinc-350 mt-0.5 truncate flex items-center gap-1">
            <DollarSign className="w-3.5 h-3.5 text-zinc-550" />
            <span>{personaSynthesis.price_elasticity}</span>
          </div>
        </div>

        <div className="p-2.5 rounded bg-zinc-950 border border-zinc-850">
          <div className="text-[9px] font-semibold text-zinc-550 uppercase">Predicted Intent</div>
          <div className="text-xs font-bold text-zinc-300 mt-0.5 truncate">
            {personaSynthesis.predicted_immediate_intent}
          </div>
        </div>
      </div>

      {/* Key Buying Motivators */}
      {personaSynthesis.key_buying_motivators && (
        <div className="space-y-1.5 pt-1">
          <span className="text-[9px] uppercase font-bold text-zinc-550">Key Behavioral Motivators</span>
          <div className="flex flex-wrap gap-1.5">
            {personaSynthesis.key_buying_motivators.map((m, idx) => (
              <span
                key={idx}
                className="text-[10px] px-2 py-0.5 rounded bg-zinc-950 text-zinc-350 border border-zinc-850 flex items-center gap-1"
              >
                <Tag className="w-3 h-3 text-zinc-500" />
                <span>{m}</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
