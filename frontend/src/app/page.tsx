"use client";
import { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState('Investigate high latency in KOL-5G-017');
  const [cellId, setCellId] = useState('KOL-5G-017');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleInvestigate = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, cell_id: cellId })
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-200 font-sans selection:bg-cyan-500/30">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-950 p-6 flex flex-col gap-6">
        <div className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)]"></div>
          NetCopilot
        </div>
        <nav className="flex flex-col gap-2">
          {['Overview', 'Investigations', 'Cells', 'Knowledge Base', 'Agents', 'Evaluation'].map((item) => (
            <button key={item} className="text-left px-4 py-2 rounded-lg text-sm hover:bg-slate-800 hover:text-cyan-400 transition-colors">
              {item}
            </button>
          ))}
        </nav>
        <div className="mt-auto px-4 py-2 rounded-lg text-sm bg-slate-900 border border-slate-800 text-green-400 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
          System Health: OK
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Cards */}
        <header className="p-8 pb-4 grid grid-cols-4 gap-4">
          <div className="bg-slate-800/50 border border-slate-700/50 p-4 rounded-xl backdrop-blur-sm">
            <div className="text-slate-400 text-sm mb-1">Active Incidents</div>
            <div className="text-3xl font-light text-white">12</div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 p-4 rounded-xl backdrop-blur-sm">
            <div className="text-slate-400 text-sm mb-1">Monitored Cells</div>
            <div className="text-3xl font-light text-white">4,281</div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 p-4 rounded-xl backdrop-blur-sm">
            <div className="text-slate-400 text-sm mb-1">KPI Anomalies</div>
            <div className="text-3xl font-light text-red-400">7</div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 p-4 rounded-xl backdrop-blur-sm">
            <div className="text-slate-400 text-sm mb-1">Avg Investigation</div>
            <div className="text-3xl font-light text-cyan-400">1.2s</div>
          </div>
        </header>

        {/* Investigation Area */}
        <div className="flex-1 overflow-auto p-8 pt-4">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-slate-950 border border-slate-800 p-6 rounded-2xl shadow-2xl">
              <h2 className="text-lg font-medium text-white mb-4">New Investigation</h2>
              <div className="flex gap-4">
                <input 
                  type="text" 
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all text-white placeholder-slate-500"
                  placeholder="E.g. Investigate high latency in KOL-5G-017"
                />
                <button 
                  onClick={handleInvestigate}
                  disabled={loading}
                  className="bg-cyan-600 hover:bg-cyan-500 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                  ) : "Investigate"}
                </button>
              </div>
            </div>

            {/* Results Area */}
            {result && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="grid grid-cols-2 gap-6">
                  {/* Root Cause & Recommendations */}
                  <div className="space-y-6">
                    <div className="bg-slate-800/30 border border-slate-700 p-6 rounded-2xl">
                      <h3 className="text-cyan-400 font-medium mb-3 flex items-center gap-2">
                        <span className="bg-cyan-400/10 p-1.5 rounded-md">🎯</span> Root Cause
                      </h3>
                      <p className="text-slate-300 leading-relaxed text-sm whitespace-pre-wrap">{result.root_causes}</p>
                    </div>
                    <div className="bg-slate-800/30 border border-slate-700 p-6 rounded-2xl border-t-4 border-t-green-500">
                      <h3 className="text-green-400 font-medium mb-3 flex items-center gap-2">
                        <span className="bg-green-500/10 p-1.5 rounded-md">⚡</span> Recommendations
                      </h3>
                      <p className="text-slate-300 leading-relaxed text-sm whitespace-pre-wrap">{result.recommendations}</p>
                    </div>
                  </div>

                  {/* Evidence & Trace */}
                  <div className="space-y-6">
                    <div className="bg-slate-800/30 border border-slate-700 p-6 rounded-2xl">
                      <h3 className="text-slate-400 font-medium mb-3">Evidence & Anomalies</h3>
                      <div className="text-xs font-mono text-slate-400 bg-slate-950 p-4 rounded-lg overflow-x-auto border border-slate-800">
                        {result.kpi_anomalies}
                      </div>
                    </div>
                    <div className="bg-slate-800/30 border border-slate-700 p-6 rounded-2xl">
                      <h3 className="text-slate-400 font-medium mb-3">Agent Execution Trace</h3>
                      <div className="space-y-3 relative before:absolute before:inset-0 before:ml-2.5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
                        {result.agent_trace.map((step: string, i: number) => (
                          <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                            <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 border-slate-700 bg-slate-900 group-[.is-active]:border-cyan-500 group-[.is-active]:bg-slate-800 text-slate-500 group-[.is-active]:text-cyan-50 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2"></div>
                            <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-slate-950 p-3 rounded border border-slate-800 shadow text-xs text-slate-400">
                              {step}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
