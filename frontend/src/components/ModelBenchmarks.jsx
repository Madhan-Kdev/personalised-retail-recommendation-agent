import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Award, Layers, Zap, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function ModelBenchmarks() {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadBenchmarks = async () => {
    setLoading(true);
    try {
      const data = await api.getModelBenchmarks();
      setBenchmarkData(data);
    } catch (err) {
      console.error("Error loading model benchmarks:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBenchmarks();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-zinc-900 rounded p-6 border border-zinc-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="w-5 h-5 text-zinc-400" />
            <h2 className="text-base font-bold uppercase tracking-wider text-zinc-100">Algorithm Benchmarks</h2>
          </div>
          <p className="text-xs text-zinc-400 max-w-2xl">
            Offline evaluation results comparing ranking accuracy (Precision, Recall, MAP, NDCG), exploration quality (Diversity, Novelty), and catalog coverage.
          </p>
        </div>

        <button
          onClick={loadBenchmarks}
          disabled={loading}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-950 font-semibold text-xs transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Run Evaluation</span>
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <RefreshCw className="w-6 h-6 text-zinc-400 animate-spin mb-3" />
          <p className="text-xs text-zinc-400 font-medium">Computing evaluation metrics across all models...</p>
        </div>
      ) : benchmarkData && (
        <div className="space-y-6 animate-fadeIn">
          {/* Highlight Summary Card */}
          <div className="p-4 rounded bg-zinc-900 border border-zinc-800 flex items-start gap-3">
            <Award className="w-5 h-5 text-zinc-400 shrink-0 mt-0.5" />
            <div className="text-xs">
              <strong className="text-zinc-200 font-semibold">Key Architectural Takeaway:</strong>
              <p className="text-zinc-400 mt-0.5 leading-relaxed">{benchmarkData.summary}</p>
            </div>
          </div>

          {/* Benchmark Comparison Table */}
          <div className="bg-zinc-900 rounded overflow-hidden border border-zinc-800 shadow-sm">
            <div className="p-4 bg-zinc-950 border-b border-zinc-800 font-semibold text-xs uppercase tracking-wider text-zinc-200 flex items-center justify-between">
              <span>Comparative Benchmark (K = {benchmarkData.evaluation_metric_k})</span>
              <span className="text-[10px] font-mono text-zinc-450">Ranked by NDCG@5</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-950 text-zinc-400 uppercase text-[9px] tracking-wider border-b border-zinc-800">
                  <tr>
                    <th className="p-4">Algorithm Architecture</th>
                    <th className="p-4">Precision@5</th>
                    <th className="p-4">Recall@5</th>
                    <th className="p-4">MAP@5</th>
                    <th className="p-4">NDCG@5</th>
                    <th className="p-4">Diversity</th>
                    <th className="p-4">Novelty (bits)</th>
                    <th className="p-4">Coverage</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-850 text-zinc-300 font-medium">
                  {Object.entries(benchmarkData.models).map(([name, m], idx) => {
                    const isHybrid = name.includes('Hybrid');
                    return (
                      <tr
                        key={idx}
                        className={`transition-colors ${
                          isHybrid
                            ? 'bg-zinc-950 font-bold text-zinc-150 border-l-2 border-l-zinc-200'
                            : 'hover:bg-zinc-850/30'
                        }`}
                      >
                        <td className="p-4 flex items-center gap-2">
                          {isHybrid && <Award className="w-4 h-4 text-zinc-400" />}
                          <span className={isHybrid ? 'text-zinc-200 font-semibold' : 'text-zinc-450'}>{name}</span>
                        </td>
                        <td className="p-4 font-mono">{m.precision_at_5}</td>
                        <td className="p-4 font-mono">{m.recall_at_5}</td>
                        <td className="p-4 font-mono text-zinc-300">{m.map_at_5}</td>
                        <td className="p-4 font-mono text-zinc-100 font-bold">{m.ndcg_at_5}</td>
                        <td className="p-4 font-mono text-zinc-400">{m.diversity}</td>
                        <td className="p-4 font-mono text-zinc-400">{m.novelty_bits}</td>
                        <td className="p-4 font-mono text-zinc-300">
                          <span className="px-2 py-0.5 rounded bg-zinc-950 border border-zinc-800">
                            {m.catalog_coverage_pct}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Metric Descriptions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="bg-zinc-900 rounded p-4 border border-zinc-800">
              <div className="flex items-center gap-2 mb-2 text-zinc-300 font-semibold">
                <TrendingUp className="w-4 h-4" />
                <span>Ranking Quality (NDCG & MAP)</span>
              </div>
              <p className="text-zinc-500 leading-relaxed">
                Normalized Discounted Cumulative Gain penalizes relevant items that appear low in the list.
              </p>
            </div>

            <div className="bg-zinc-900 rounded p-4 border border-zinc-800">
              <div className="flex items-center gap-2 mb-2 text-zinc-300 font-semibold">
                <Layers className="w-4 h-4" />
                <span>Intra-List Diversity</span>
              </div>
              <p className="text-zinc-500 leading-relaxed">
                Measures pairwise TF-IDF distance among suggestions to prevent repetitive items.
              </p>
            </div>

            <div className="bg-zinc-900 rounded p-4 border border-zinc-800">
              <div className="flex items-center gap-2 mb-2 text-zinc-300 font-semibold">
                <Zap className="w-4 h-4" />
                <span>Novelty & Coverage</span>
              </div>
              <p className="text-zinc-500 leading-relaxed">
                Quantifies long-tail item exposure to prevent cold-start bottlenecks.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
