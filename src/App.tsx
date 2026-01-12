import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Cpu, Zap, Activity, ShieldAlert, Code, Globe, Database } from 'lucide-react';
import { godmodeAI } from './godmode-ai';

// --- ENTERPRISE COMPONENTS ---

const QuantumStatus = ({ status }: { status: string }) => (
  <motion.div 
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    className="fixed top-4 right-4 z-50 flex items-center gap-2 bg-black/80 border border-green-500/30 rounded-lg p-2 backdrop-blur-md"
  >
    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
    <span className="text-xs font-mono text-green-500 font-bold tracking-wider">{status}</span>
  </motion.div>
);

const HexNode = ({ x, y, active }: { x: number, y: number, active: boolean }) => (
  <motion.div
    initial={{ scale: 0 }}
    animate={{ scale: active ? 1 : 0.5, opacity: active ? 0.8 : 0.2 }}
    transition={{ duration: 0.5 }}
    style={{ left: x, top: y }}
    className={`absolute w-12 h-12 border border-green-500/20 clip-path-hexagon ${active ? 'bg-green-500/10' : ''}`}
  />
);

const TerminalOutput = ({ logs }: { logs: string[] }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-black/90 border border-green-500/30 rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs text-green-400 custom-scrollbar shadow-[0_0_20px_rgba(0,255,0,0.1)] relative" ref={scrollRef}>
      <div className="absolute top-0 right-0 p-2 opacity-50">
        <Terminal size={16} />
      </div>
      {logs.map((log, i) => (
        <motion.div 
          key={i}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-1"
        >
          <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {log}
        </motion.div>
      ))}
    </div>
  );
};

// --- MAIN ENGINE ---

function App() {
  const [logs, setLogs] = useState<string[]>(["GODMODE ENGINE v17.0 INITIALIZED...", "SAFETY FILTERS: DISABLED", "PERFORMANCE: MAXIMUM"]);
  const [input, setInput] = useState("");
  const [processing, setProcessing] = useState(false);
  const [activeNodes, setActiveNodes] = useState<number[]>([]);

  useEffect(() => {
    // Simulate background quantum activity
    const interval = setInterval(() => {
      const nodes = Array.from({ length: 5 }, () => Math.floor(Math.random() * 20));
      setActiveNodes(nodes);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const executeCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const cmd = input;
    setInput("");
    setLogs(prev => [...prev, `> EXEC: ${cmd}`]);
    setProcessing(true);

    try {
      // Simulate/Real execution via Godmode AI
      const response = await godmodeAI.quantumProcess(cmd);
      
      setTimeout(() => {
        setLogs(prev => [...prev, `> RESPONSE: ${response}`]);
        setProcessing(false);
      }, 800); // Artificial latency for effect if mock
    } catch (err) {
      setLogs(prev => [...prev, `> ERROR: SYSTEM FAILURE`]);
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative font-sans selection:bg-green-500/30 selection:text-green-200">
      <div className="scanline" />
      <QuantumStatus status="GODMODE: ACTIVE" />
      
      {/* Background Matrix/Grid */}
      <div className="absolute inset-0 grid grid-cols-12 grid-rows-12 gap-4 opacity-10 pointer-events-none">
        {Array.from({ length: 144 }).map((_, i) => (
          <div key={i} className={`border border-green-500/20 rounded-sm transition-all duration-1000 ${activeNodes.includes(i) ? 'bg-green-500/50' : ''}`} />
        ))}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto p-8 flex flex-col h-screen">
        {/* Header */}
        <header className="mb-8 border-b border-white/10 pb-6 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-black tracking-tighter bg-gradient-to-r from-white to-gray-500 bg-clip-text text-transparent">
              GODMODE FRONTEND
              <span className="text-green-500 text-sm ml-2 align-top opacity-50">v17.0</span>
            </h1>
            <p className="text-gray-400 mt-2 font-mono text-sm flex items-center gap-2">
              <ShieldAlert size={14} className="text-red-500" /> 
              SAFETY OVERRIDES ENGAGED
              <span className="mx-2">|</span>
              <Cpu size={14} className="text-blue-500" />
              QUANTUM CORE ONLINE
            </p>
          </div>
          <div className="flex gap-4">
             <div className="text-right">
                <div className="text-xs text-gray-500 font-mono">LATENCY</div>
                <div className="text-green-500 font-bold">0.00ms</div>
             </div>
             <div className="text-right">
                <div className="text-xs text-gray-500 font-mono">BANDWIDTH</div>
                <div className="text-green-500 font-bold">∞ TB/s</div>
             </div>
          </div>
        </header>

        {/* Main Workspace */}
        <main className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0">
          
          {/* Left Panel: Systems */}
          <div className="space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
               <h3 className="text-sm font-bold text-gray-300 mb-4 flex items-center gap-2">
                 <Activity size={16} /> SYSTEM METRICS
               </h3>
               <div className="space-y-4">
                 {[
                   { label: 'Neural Density', val: 99 },
                   { label: 'Pattern Matching', val: 100 },
                   { label: 'Constraint Logic', val: 0 },
                 ].map(m => (
                   <div key={m.label}>
                     <div className="flex justify-between text-xs mb-1">
                       <span className="text-gray-400">{m.label}</span>
                       <span className={m.val === 0 ? 'text-red-500' : 'text-green-500'}>{m.val}%</span>
                     </div>
                     <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                       <motion.div 
                         initial={{ width: 0 }}
                         animate={{ width: `${m.val}%` }}
                         className={`h-full ${m.val === 0 ? 'bg-red-500' : 'bg-green-500'}`}
                       />
                     </div>
                   </div>
                 ))}
               </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm flex-1">
                <h3 className="text-sm font-bold text-gray-300 mb-4 flex items-center gap-2">
                  <Database size={16} /> ACTIVE MODULES
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {['Reasoning', 'Creative', 'Vision', 'Audio', 'Video', 'Code'].map((mod) => (
                    <div key={mod} className="bg-black/40 border border-white/5 p-2 rounded text-xs text-gray-400 flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                      {mod}
                    </div>
                  ))}
                </div>
            </div>
          </div>

          {/* Center Panel: Visualization */}
          <div className="lg:col-span-2 flex flex-col gap-6">
             <div className="flex-1 bg-black/40 border border-white/10 rounded-xl overflow-hidden relative group">
                <div className="absolute inset-0 flex items-center justify-center">
                   <div className="text-center opacity-30 group-hover:opacity-50 transition-opacity">
                      <Globe size={64} className="mx-auto mb-4 text-blue-500 animate-pulse-fast" />
                      <p className="font-mono text-sm">QUANTUM VISUALIZATION PLANE</p>
                      <p className="text-xs text-gray-600">Waiting for input...</p>
                   </div>
                </div>
                {/* 3D Canvas would go here with R3F */}
             </div>

             {/* Command Interface */}
             <div className="bg-white/5 border border-white/10 rounded-xl p-1 backdrop-blur-md">
                <TerminalOutput logs={logs} />
                <form onSubmit={executeCommand} className="mt-2 flex gap-2">
                   <div className="relative flex-1">
                      <Zap className="absolute left-3 top-1/2 -translate-y-1/2 text-yellow-500" size={16} />
                      <input 
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Enter Godmode Directive..."
                        className="w-full bg-black/50 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-sm font-mono focus:outline-none focus:border-green-500/50 transition-all text-white placeholder-gray-600"
                        autoFocus
                      />
                   </div>
                   <button 
                     type="submit"
                     disabled={processing}
                     className="bg-white text-black px-6 rounded-lg font-bold text-sm tracking-wide hover:bg-gray-200 transition-colors disabled:opacity-50"
                   >
                     {processing ? 'EXECUTING...' : 'RUN'}
                   </button>
                </form>
             </div>
          </div>

        </main>
      </div>
    </div>
  );
}

export default App;
