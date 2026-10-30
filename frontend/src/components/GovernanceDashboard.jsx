import React, { useState, useEffect } from 'react';
import { ShieldCheck, Scale, AlertTriangle, CheckCircle, XCircle, FileText, Search, RefreshCw, Cpu } from 'lucide-react';
import { api } from '../services/api';

export default function GovernanceDashboard() {
  const [fairnessData, setFairnessData] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [hitlQueue, setHitlQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState('fairness'); // 'fairness', 'hitl', 'audit'
  const [logSearch, setLogSearch] = useState('');
  const [actionMessage, setActionMessage] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [fairnessRes, logsRes, hitlRes] = await Promise.all([
        api.getFairnessAudit(),
        api.getAuditLogs(50),
        api.getHITLQueue()
      ]);
      setFairnessData(fairnessRes);
      setAuditLogs(logsRes);
      setHitlQueue(hitlRes);
    } catch (err) {
      console.error("Error loading governance data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleHITLAction = async (entryId, decision) => {
    try {
      await api.takeHITLAction(entryId, decision);
      setActionMessage(`Item ${entryId} has been ${decision}!`);
      setTimeout(() => setActionMessage(null), 3000);
      loadData();
    } catch (err) {
      console.error("Error updating HITL item:", err);
    }
  };

  const filteredLogs = auditLogs.filter((log) => {
    if (!logSearch) return true;
    const s = logSearch.toLowerCase();
    return (
      log.customer_id.toLowerCase().includes(s) ||
      log.model_used.toLowerCase().includes(s) ||
      log.explanation.toLowerCase().includes(s) ||
      (log.citations && log.citations.some(c => c.toLowerCase().includes(s)))
    );
  });

  return (
    <div className="space-y-6">
      {/* Header Notification */}
      {actionMessage && (
        <div className="p-3 rounded bg-zinc-100 text-zinc-950 font-semibold text-xs flex items-center gap-2 border border-zinc-200 animate-fadeIn">
          <CheckCircle className="w-4 h-4" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Governance Studio Header */}
      <div className="bg-zinc-900 rounded p-6 border border-zinc-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldCheck className="w-5 h-5 text-zinc-400" />
            <h2 className="text-base font-bold uppercase tracking-wider text-zinc-100">Responsible AI & Governance</h2>
          </div>
          <p className="text-xs text-zinc-400">
            Monitoring demographic fairness, US EEOC compliant bias checks, and manual moderation queues.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded bg-zinc-950 hover:bg-zinc-800 text-zinc-300 border border-zinc-850 text-xs font-medium transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit Logs</span>
        </button>
      </div>

      {/* Sub-Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
        <button
          onClick={() => setActiveSubTab('fairness')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-semibold transition-all ${
            activeSubTab === 'fairness'
              ? 'bg-zinc-100 text-zinc-950 shadow-sm'
              : 'text-zinc-400 hover:text-zinc-200 bg-zinc-900'
          }`}
        >
          <Scale className="w-4 h-4" />
          <span>Demographic Parity</span>
        </button>

        <button
          onClick={() => setActiveSubTab('hitl')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-semibold transition-all ${
            activeSubTab === 'hitl'
              ? 'bg-zinc-100 text-zinc-950 shadow-sm'
              : 'text-zinc-400 hover:text-zinc-200 bg-zinc-900'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>HITL Moderation ({hitlQueue.filter(h => h.status === 'PENDING').length})</span>
        </button>

        <button
          onClick={() => setActiveSubTab('audit')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-semibold transition-all ${
            activeSubTab === 'audit'
              ? 'bg-zinc-100 text-zinc-950 shadow-sm'
              : 'text-zinc-400 hover:text-zinc-200 bg-zinc-900'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Immutable Audit Trail ({auditLogs.length})</span>
        </button>
      </div>

      {/* TAB 1: Fairness & Demographic Parity */}
      {activeSubTab === 'fairness' && fairnessData && (
        <div className="space-y-6 animate-fadeIn">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-zinc-900 rounded p-4 border border-zinc-800">
              <span className="text-[10px] uppercase font-semibold text-zinc-500 block mb-1">Fairness Score</span>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-bold text-zinc-100">{fairnessData.overall_fairness_score}</span>
                <span className="text-xs text-zinc-500">/ 1.00</span>
              </div>
              <span className="text-[10px] text-zinc-400 mt-1 block font-medium">Optimal Cohort Alignment</span>
            </div>

            <div className="bg-zinc-900 rounded p-4 border border-zinc-800">
              <span className="text-[10px] uppercase font-semibold text-zinc-500 block mb-1">Parity Status</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className="text-xs font-semibold text-zinc-100">{fairnessData.demographic_parity_status}</span>
              </div>
              <span className="text-[10px] text-zinc-400 mt-1 block">EEOC 4/5ths Rule Checked</span>
            </div>

            <div className="bg-zinc-900 rounded p-4 border border-zinc-800">
              <span className="text-[10px] uppercase font-semibold text-zinc-500 block mb-1">Price Parity (F/M)</span>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-bold text-zinc-100">{fairnessData.price_parity_ratio}</span>
                <span className="text-[10px] text-zinc-500 font-medium">(Target: &ge;0.80)</span>
              </div>
              <span className="text-[10px] text-zinc-400 mt-1 block">No Unintended Skew</span>
            </div>

            <div className="bg-zinc-900 rounded p-4 border border-zinc-800">
              <span className="text-[10px] uppercase font-semibold text-zinc-500 block mb-1">Audited Runs</span>
              <div className="text-xl font-bold text-zinc-100">{fairnessData.total_recommendations_audited}</div>
              <span className="text-[10px] text-zinc-400 mt-1 block font-medium">Continuous Telemetry Audit</span>
            </div>
          </div>

          {/* Segment Analysis Table */}
          <div className="bg-zinc-900 rounded overflow-hidden border border-zinc-800">
            <div className="p-4 bg-zinc-950 border-b border-zinc-800 font-semibold text-xs uppercase tracking-wider text-zinc-200">
              Demographic Exposure & Basket Allocation
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-950 text-zinc-400 uppercase text-[9px] tracking-wider border-b border-zinc-800">
                  <tr>
                    <th className="p-3.5">Segment</th>
                    <th className="p-3.5">Profiles Count</th>
                    <th className="p-3.5">Avg Price</th>
                    <th className="p-3.5">Median Price</th>
                    <th className="p-3.5">Primary Category</th>
                    <th className="p-3.5">Parity Health</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-850 text-zinc-300 font-medium">
                  {fairnessData.segments?.map((seg, idx) => (
                    <tr key={idx} className="hover:bg-zinc-850/30 transition-colors">
                      <td className="p-3.5 font-semibold text-zinc-100">{seg.segment_name}</td>
                      <td className="p-3.5">{seg.sample_size}</td>
                      <td className="p-3.5 font-mono text-zinc-300">${seg.avg_recommended_price.toFixed(2)}</td>
                      <td className="p-3.5 font-mono text-zinc-500">${seg.median_price.toFixed(2)}</td>
                      <td className="p-3.5">{seg.top_category}</td>
                      <td className="p-3.5">
                        <span className="px-2 py-0.5 rounded bg-zinc-950 text-zinc-300 text-[10px] font-semibold border border-zinc-800">
                          OPTIMAL
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Guardrail Rules Checklist */}
          <div className="bg-zinc-900 rounded p-5 border border-zinc-800">
            <h3 className="font-semibold text-xs uppercase tracking-wider text-zinc-250 mb-3">
              Guardrail Rules & Threshold Compliance
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              {fairnessData.guardrail_checks?.map((rule, idx) => (
                <div key={idx} className="p-3 rounded bg-zinc-950 border border-zinc-850 flex items-center justify-between">
                  <span className="text-zinc-300 font-medium">{rule.rule}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-zinc-300 font-bold">{rule.score}</span>
                    <span className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 font-semibold text-[10px] border border-zinc-800">
                      {rule.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Human-In-The-Loop (HITL) Queue */}
      {activeSubTab === 'hitl' && (
        <div className="space-y-4 animate-fadeIn">
          <div className="p-4 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-zinc-500 shrink-0 mt-0.5" />
            <div>
              <strong>Queue System:</strong> Recommendations flagged with items over $500, low-confidence scores, or specific metadata parameters require moderation approval before customer dispatch.
            </div>
          </div>

          <div className="bg-zinc-900 rounded overflow-hidden border border-zinc-800">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-950 text-zinc-400 uppercase text-[9px] tracking-wider border-b border-zinc-800">
                  <tr>
                    <th className="p-3.5">ID</th>
                    <th className="p-3.5">Customer</th>
                    <th className="p-3.5">Product</th>
                    <th className="p-3.5">Price</th>
                    <th className="p-3.5">Reason</th>
                    <th className="p-3.5">Status</th>
                    <th className="p-3.5 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-850 text-zinc-300 font-medium">
                  {hitlQueue.length > 0 ? (
                    hitlQueue.map((item) => (
                      <tr key={item.id} className="hover:bg-zinc-850/30 transition-colors">
                        <td className="p-3.5 font-mono text-[10px] text-zinc-500">{item.id}</td>
                        <td className="p-3.5 font-semibold text-zinc-200">{item.customer_name} ({item.customer_id})</td>
                        <td className="p-3.5 text-zinc-300">{item.product_title}</td>
                        <td className="p-3.5 font-mono font-semibold text-zinc-200">${item.product_price?.toFixed(2)}</td>
                        <td className="p-3.5 text-zinc-400 font-medium">{item.reason}</td>
                        <td className="p-3.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                            item.status === 'APPROVED' ? 'bg-zinc-950 text-zinc-400 border-zinc-800' :
                            item.status === 'REJECTED' ? 'bg-zinc-950 text-zinc-500 border-zinc-800' :
                            'bg-zinc-800 text-zinc-200 border-zinc-700'
                          }`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="p-3.5 text-right">
                          {item.status === 'PENDING' ? (
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={() => handleHITLAction(item.id, 'APPROVED')}
                                className="px-2.5 py-1 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-950 font-semibold text-[10px] transition-colors"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleHITLAction(item.id, 'REJECTED')}
                                className="px-2.5 py-1 rounded bg-zinc-950 hover:bg-zinc-800 text-zinc-350 font-semibold text-[10px] transition-colors border border-zinc-850"
                              >
                                Reject
                              </button>
                            </div>
                          ) : (
                            <span className="text-[10px] text-zinc-500">Moderated ({item.reviewed_by || 'system'})</span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="p-8 text-center text-zinc-500">
                        No pending items in moderation queue.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Immutable Audit Trail */}
      {activeSubTab === 'audit' && (
        <div className="space-y-4 animate-fadeIn">
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <input
                type="text"
                placeholder="Search audit trail..."
                value={logSearch}
                onChange={(e) => setLogSearch(e.target.value)}
                className="w-full bg-zinc-900 text-zinc-300 text-xs rounded pl-9 pr-3.5 py-2 border border-zinc-800 focus:border-zinc-700 focus:outline-none"
              />
              <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
            </div>
            <span className="text-xs text-zinc-500 font-mono">Records: {filteredLogs.length}</span>
          </div>

          <div className="bg-zinc-900 rounded overflow-hidden border border-zinc-800">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-950 text-zinc-400 uppercase text-[9px] tracking-wider border-b border-zinc-800">
                  <tr>
                    <th className="p-3.5">Log ID</th>
                    <th className="p-3.5">Timestamp</th>
                    <th className="p-3.5">Customer</th>
                    <th className="p-3.5">Model</th>
                    <th className="p-3.5">Latency</th>
                    <th className="p-3.5">Confidence</th>
                    <th className="p-3.5">Data Citations</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-850 text-zinc-300 font-medium">
                  {filteredLogs.slice(0, 25).map((log) => (
                    <tr key={log.id} className="hover:bg-zinc-850/30 transition-colors">
                      <td className="p-3.5 font-mono text-[10px] text-zinc-450">{log.id}</td>
                      <td className="p-3.5 text-zinc-500 text-[10px] whitespace-nowrap">{new Date(log.timestamp).toLocaleTimeString()}</td>
                      <td className="p-3.5 font-semibold text-zinc-200">{log.customer_id}</td>
                      <td className="p-3.5">
                        <span className="px-2 py-0.5 rounded bg-zinc-950 text-zinc-400 border border-zinc-850 text-[10px] font-mono">
                          {log.model_used}
                        </span>
                      </td>
                      <td className="p-3.5 font-mono text-zinc-400">{log.latency_ms}ms</td>
                      <td className="p-3.5 font-mono text-zinc-300">{Math.round(log.confidence * 100)}%</td>
                      <td className="p-3.5 max-w-xs">
                        <div className="space-y-1">
                          {log.citations?.slice(0, 2).map((c, i) => (
                            <span key={i} className="block text-[10px] text-zinc-500 font-mono truncate" title={c}>
                              • {c}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
