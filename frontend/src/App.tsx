import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Square, FastForward, Activity, Plane, Users, Flame, ShieldAlert, Cpu, Terminal, CheckCircle2, FileText, Send } from 'lucide-react';

const translateAction = (raw: string) => {
    if (!raw) return "Analyze";
    let str = String(raw);
    str = str.replace(/ACTION1/g, "Navigate Left");
    str = str.replace(/ACTION2/g, "Navigate Right");
    str = str.replace(/ACTION3/g, "Navigate Up");
    str = str.replace(/ACTION4/g, "Navigate Down");
    return str;
};

const toSector = (r: number, c: number) => {
    if (r === undefined || c === undefined) return "X9";
    const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const l = letters[r % 26] || "A";
    return `${l}${c + 1}`;
};

// BFS to find shortest path on grid avoiding obstacles (value 2)
const findShortestPath = (grid: any[][], start: any, end: any) => {
    if (!start || !end || !grid) return [];
    const queue = [[start]];
    const visited = new Set([`${start.r},${start.c}`]);
    const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]]; 
    
    while (queue.length > 0) {
        const path = queue.shift()!;
        const curr = path[path.length - 1];
        
        if (curr.r === end.r && curr.c === end.c) {
            return path;
        }
        
        for (const [dr, dc] of dirs) {
            const nr = curr.r + dr;
            const nc = curr.c + dc;
            
            if (nr >= 0 && nr < grid.length && nc >= 0 && nc < grid[0].length) {
                if (grid[nr][nc] !== 2 && !visited.has(`${nr},${nc}`)) { 
                    visited.add(`${nr},${nc}`);
                    queue.push([...path, {r: nr, c: nc}]);
                }
            }
        }
    }
    return [];
};

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function App() {
  const [currentView, setCurrentView] = useState<'MACRO' | 'MICRO'>('MACRO');
  const [gameState, setGameState] = useState<any>(null);
  const [autoRun, setAutoRun] = useState(false);
  const [loading, setLoading] = useState(false);
  const [eventLog, setEventLog] = useState<{time: string, msg: string, isAlert: boolean}[]>([]);

  // Ask Command AI Chat State
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<{role: 'user'|'ai', msg: string}[]>([
      { role: 'ai', msg: 'Commander, AEGIS is active. Awaiting your queries on resource allocation or predictions.' }
  ]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [chatMessages]);

  const handleChatSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (!chatInput.trim()) return;
      const userMsg = chatInput;
      setChatMessages(prev => [...prev, {role: 'user', msg: userMsg}]);
      setChatInput("");
      
      setTimeout(() => {
          if (userMsg.toLowerCase().includes("why") && userMsg.toLowerCase().includes("alpha")) {
              setChatMessages(prev => [...prev, {role: 'ai', msg: "• Alpha had sufficient fuel for round-trip (76%).\n• Victim severity score was highest (Critical, 12m window).\n• Route collision probability was 0%.\n• Estimated rescue time was lowest."}]);
          } else {
              setChatMessages(prev => [...prev, {role: 'ai', msg: 'System analyzing query... Based on the Digital Twin, current resource allocation is globally optimal.'}]);
          }
      }, 800);
  };

  const fetchState = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/state');
      const data = await res.json();
      setGameState(data);
    } catch (e) {
      console.error(e);
    }
  };

  const initGame = async () => {
    setLoading(true);
    await fetch('http://127.0.0.1:8000/api/init', { method: 'POST' });
    setEventLog([{ time: new Date().toLocaleTimeString('en-US', { hour12: false }), msg: 'AEGIS Rescue System Initialized.', isAlert: false }]);
    await fetchState();
    setLoading(false);
  };

  const stepGame = async (human_action?: string) => {
    if (loading) return;
    setLoading(true);
    try {
      await fetch('http://127.0.0.1:8000/api/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ human_action })
      });
      await fetchState();
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => { fetchState(); }, []);

  useEffect(() => {
    let interval: any;
    if (autoRun && gameState?.status !== "WIN" && gameState?.status !== "GAME_OVER") {
      interval = setInterval(() => stepGame(), 900);
    }
    return () => clearInterval(interval);
  }, [autoRun, gameState?.status]);

  // Dynamic Alerts Simulator
  useEffect(() => {
    if (currentView === 'MACRO' || gameState?.status === "WIN" || gameState?.status === "UNINITIALIZED" || !gameState) return;
    const interval = setInterval(() => {
        const events = [
            "Building Collapse Detected in Sector D4",
            "Fire Spreading rapidly in Sector A1",
            "Drone Bravo routing to Secondary Triage",
            "Planner recomputing allocation queues",
            "Digital Twin updated hazard zones"
        ];
        const evt = events[Math.floor(Math.random() * events.length)];
        const isAlert = evt.includes("Collapse") || evt.includes("Fire");
        setEventLog(prev => [{ time: new Date().toLocaleTimeString('en-US', { hour12: false }), msg: evt, isAlert }, ...prev].slice(0, 15));
    }, 5500);
    return () => clearInterval(interval);
  }, [currentView, gameState?.status]);

  let playerPos: any = null;
  let goalPos: any = null;
  
  if (gameState?.grid) {
    gameState.grid.forEach((row: any[], r: number) => {
      row.forEach((val: any, c: number) => {
        if (val === 10 && !playerPos) playerPos = { r, c };
        if (val === 3 && !goalPos) goalPos = { r, c };
      });
    });
  }

  // Multi-Agent / Multi-Victim Topology Injection
  let droneBravoPos: any = null;
  let droneCharliePos: any = null;
  let victimBPos: any = null;
  let victimCPos: any = null;
  
  if (gameState?.grid) {
      const gr = gameState.grid.length;
      const gc = gameState.grid[0].length;
      droneBravoPos = { r: Math.floor(gr * 0.15), c: Math.floor(gc * 0.8) };
      droneCharliePos = { r: Math.floor(gr * 0.85), c: Math.floor(gc * 0.2) };
      victimBPos = { r: Math.floor(gr * 0.2), c: Math.floor(gc * 0.15) };
      victimCPos = { r: Math.floor(gr * 0.7), c: Math.floor(gc * 0.8) };
  }
  
  let distance: number | null = null;
  if (playerPos && goalPos) {
    distance = Math.abs(playerPos.r - goalPos.r) + Math.abs(playerPos.c - goalPos.c);
  }

  const plannerTrace = gameState?.traces?.find((t: any) => t.agent.includes("PlannerAgent"));
  let selectedAction = "Evaluate";
  if (plannerTrace?.reasoning) {
      const raw = Array.isArray(plannerTrace.reasoning) ? plannerTrace.reasoning.join(" ") : plannerTrace.reasoning;
      if (raw.includes("Selected action:")) {
          selectedAction = translateAction(raw.split("Selected action: ")[1]);
      }
  }

  useEffect(() => {
    if (selectedAction !== "Evaluate" && gameState?.step) {
        setEventLog(prev => [{ time: new Date().toLocaleTimeString('en-US', { hour12: false }), msg: `Alpha executed ${selectedAction.replace("Navigate ", "").toUpperCase()}`, isAlert: false }, ...prev].slice(0, 15));
    }
  }, [selectedAction, gameState?.step]);

  let successProb = 0;
  if (distance !== null) {
      successProb = Math.max(10, Math.min(99, 100 - (distance * 4)));
  }

  const shortestPath = findShortestPath(gameState?.grid, playerPos, goalPos);
  const pathSet = new Set(shortestPath.map(p => `${p.r},${p.c}`));

  // Fire Spread Prediction (Digital Twin logic)
  const isAdjacentToHazard = (r: number, c: number) => {
      if (!gameState?.grid) return false;
      const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [-1, 1], [1, -1], [1, 1]];
      for (const [dr, dc] of dirs) {
          const nr = r + dr;
          const nc = c + dc;
          if (nr >= 0 && nr < gameState.grid.length && nc >= 0 && nc < gameState.grid[0].length) {
              if (gameState.grid[nr][nc] === 2) return true;
          }
      }
      return false;
  };

  const renderGrid = (grid: any[][], size = 15, isPredicted = false) => {
    if (!grid || grid.length === 0) return null;
    
    return (
      <div 
        className="inline-block bg-[#020617]/80 backdrop-blur-md rounded-xl overflow-visible shadow-[0_8px_30px_rgb(0,0,0,0.8)] relative border border-white/10 p-1"
        style={{
            backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)`,
            backgroundSize: `${size}px ${size}px`
        }}
      >
        {grid.map((row, r) => (
          <div key={r} className="flex relative">
            {row.map((val, c) => {
              let isPlayer = !isPredicted && playerPos && r === playerPos.r && c === playerPos.c;
              let isTarget = !isPredicted && goalPos && r === goalPos.r && c === goalPos.c;
              let isObstacle = val === 2;
              let isPath = !isPredicted && pathSet.has(`${r},${c}`) && !isPlayer && !isTarget;
              
              // Injected Multi-Agent Entities
              let isBravo = !isPredicted && droneBravoPos && r === droneBravoPos.r && c === droneBravoPos.c && !isObstacle;
              let isCharlie = !isPredicted && droneCharliePos && r === droneCharliePos.r && c === droneCharliePos.c && !isObstacle;
              let isVictimB = !isPredicted && victimBPos && r === victimBPos.r && c === victimBPos.c && !isObstacle;
              let isVictimC = !isPredicted && victimCPos && r === victimCPos.r && c === victimCPos.c && !isObstacle;
              
              // Digital Twin Spread Prediction
              let isPredictedSpread = !isPredicted && !isPlayer && !isTarget && !isObstacle && !isBravo && !isCharlie && !isVictimB && !isVictimC && isAdjacentToHazard(r, c);
              
              let color = 'transparent';
              if (isObstacle) color = 'rgba(239, 68, 68, 0.15)'; 
              
              let cellClass = "rounded-[3px] m-[1px]";
              let inlineStyle: any = { width: size, height: size, backgroundColor: color };
              
              if (!isPredicted) {
                 if (isPlayer) {
                     cellClass = "animate-pulse z-40 relative scale-[1.3] shadow-[0_0_35px_rgba(6,182,212,0.9)] rounded-md bg-cyan-500/20";
                     inlineStyle.border = "2px solid #22d3ee";
                 }
                 else if (isBravo || isCharlie) {
                     cellClass = "z-30 relative scale-[1.1] rounded-md bg-slate-500/20";
                     inlineStyle.border = "1px solid #94a3b8";
                 }
                 else if (isTarget) {
                     cellClass = "z-10 relative scale-[1.15] shadow-[0_0_25px_rgba(16,185,129,0.6)] rounded-md bg-emerald-500/20";
                     inlineStyle.border = "2px solid #34d399";
                 }
                 else if (isVictimB || isVictimC) {
                     cellClass = "z-10 relative scale-[1.1] shadow-[0_0_15px_rgba(245,158,11,0.3)] rounded-md bg-amber-500/20";
                     inlineStyle.border = "1px solid #fbbf24";
                 }
                 else if (isObstacle) {
                     inlineStyle.border = "1px solid rgba(239, 68, 68, 0.4)";
                 }
                 else if (isPredictedSpread) {
                     inlineStyle.border = "1px dashed rgba(239, 68, 68, 0.5)";
                     inlineStyle.backgroundColor = "rgba(239, 68, 68, 0.05)";
                     cellClass += " animate-pulse";
                 }
                 else {
                     inlineStyle.border = "1px solid rgba(255,255,255,0.02)";
                 }
                 
                 if (isPath) {
                     inlineStyle.backgroundColor = "rgba(56, 189, 248, 0.1)";
                 }
              }
              
              return (
                <div 
                  key={`${r}-${c}`}
                  className={`transition-all duration-500 ${cellClass} flex items-center justify-center`}
                  style={inlineStyle}
                >
                   {isPlayer && <Plane className="text-cyan-200 drop-shadow-[0_0_8px_rgba(34,211,238,1)] z-50 transform -rotate-45" style={{ width: size * 0.75, height: size * 0.75 }} />}
                   {(isBravo || isCharlie) && <Plane className="text-slate-400 drop-shadow-[0_0_5px_rgba(148,163,184,1)] z-30 transform -rotate-45" style={{ width: size * 0.6, height: size * 0.6 }} />}
                   
                   {isTarget && <Users className="text-emerald-300 drop-shadow-[0_0_8px_rgba(16,185,129,1)] z-40" style={{ width: size * 0.7, height: size * 0.7 }} />}
                   {(isVictimB || isVictimC) && <Users className="text-amber-400 drop-shadow-[0_0_5px_rgba(245,158,11,1)] z-10" style={{ width: size * 0.6, height: size * 0.6 }} />}
                   
                   {isObstacle && !isBravo && !isCharlie && !isVictimB && !isVictimC && <Flame className="text-red-500/80 drop-shadow-[0_0_5px_rgba(239,68,68,0.8)]" style={{ width: size * 0.6, height: size * 0.6 }} />}
                   
                   {/* Route Highlight Dot */}
                   {isPath && <div className="w-2 h-2 bg-cyan-400 rounded-full shadow-[0_0_12px_rgba(34,211,238,1)] z-20"></div>}

                   {/* Topographic text label for empty spaces */}
                   {!isPredicted && !isPlayer && !isTarget && !isObstacle && !isBravo && !isCharlie && !isVictimB && !isVictimC && size >= 24 && (r % 7 === 0) && (c % 7 === 0) && (
                       <div className="absolute text-[8px] font-mono text-white/10 pointer-events-none whitespace-nowrap">
                           SECTOR {toSector(r,c)}
                       </div>
                   )}
                </div>
              )
            })}
          </div>
        ))}
      </div>
    );
  };

  // MACRO VIEW (Global Command)
  if (currentView === 'MACRO') {
      return (
        <div className="flex h-screen bg-[#050505] text-slate-200 overflow-hidden relative font-sans">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-900/10 to-black"></div>
          
          {/* Sidebar */}
          <div className="w-[320px] bg-black/80 border-r border-white/10 p-8 flex flex-col z-10 shadow-2xl">
             <ShieldAlert className="w-12 h-12 text-cyan-400 mb-4 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]" />
             <h1 className="text-3xl font-black text-white uppercase tracking-widest">AEGIS</h1>
             <p className="text-[10px] text-cyan-400 font-bold uppercase tracking-widest mb-12">Autonomous Grid Intelligence</p>
             
             <div className="space-y-4">
                 <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-2">Global Situation Report</div>
                 <div className="bg-white/5 p-5 rounded-xl border border-white/10 relative overflow-hidden">
                     <div className="absolute top-0 left-0 w-1 h-full bg-slate-500"></div>
                     <div className="text-4xl font-black text-white mb-1">8</div>
                     <div className="text-[10px] text-slate-400 uppercase tracking-widest">Active Operations</div>
                 </div>
                 <div className="bg-cyan-950/30 p-5 rounded-xl border border-cyan-500/20 relative overflow-hidden">
                     <div className="absolute top-0 left-0 w-1 h-full bg-cyan-400"></div>
                     <div className="text-4xl font-black text-cyan-400 mb-1">23</div>
                     <div className="text-[10px] text-cyan-200 uppercase tracking-widest">Deployed Drones</div>
                 </div>
                 <div className="bg-emerald-950/30 p-5 rounded-xl border border-emerald-500/20 relative overflow-hidden">
                     <div className="absolute top-0 left-0 w-1 h-full bg-emerald-400"></div>
                     <div className="text-4xl font-black text-emerald-400 mb-1">91%</div>
                     <div className="text-[10px] text-emerald-200 uppercase tracking-widest">Predicted Success</div>
                 </div>
             </div>
          </div>
          
          {/* Main Map Area */}
          <div className="flex-1 p-12 flex flex-col z-10 relative overflow-y-auto">
              <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at center, #22d3ee 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
              <h2 className="text-xs font-black text-white uppercase tracking-widest mb-8 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-cyan-400" /> Priority Interventions
              </h2>
              
              <div className="grid grid-cols-2 gap-8 max-w-5xl">
                  {/* Chennai Flood */}
                  <div className="bg-black/60 backdrop-blur-xl border border-red-500/30 p-8 rounded-2xl shadow-[0_0_50px_rgba(239,68,68,0.15)] relative overflow-hidden group hover:border-red-500/50 transition-all">
                      <div className="absolute top-0 left-0 w-full h-1.5 bg-red-500"></div>
                      <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 rounded-full blur-3xl pointer-events-none"></div>
                      <div className="flex justify-between items-start mb-8">
                          <div>
                              <h3 className="text-2xl font-black text-white tracking-wide">Operation Delta</h3>
                              <div className="text-xs text-red-400 font-bold uppercase tracking-widest mt-1">Chennai Flood Event</div>
                          </div>
                          <div className="bg-red-500/20 text-red-400 px-3 py-1.5 rounded text-[10px] font-bold uppercase tracking-widest border border-red-500/50">Critical</div>
                      </div>
                      
                      <div className="flex justify-between mb-10 text-sm font-mono">
                          <div className="flex flex-col"><span className="text-slate-500">Awaiting Rescue</span><span className="text-white text-3xl font-black mt-2">142</span></div>
                          <div className="flex flex-col text-right"><span className="text-slate-500">Hazards Detected</span><span className="text-red-400 text-3xl font-black mt-2">8</span></div>
                      </div>
                      
                      <button 
                          onClick={() => { setCurrentView('MICRO'); initGame(); }}
                          className="w-full py-5 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold tracking-widest uppercase text-xs transition-all shadow-[0_0_30px_rgba(239,68,68,0.4)]"
                      >
                          Deploy AEGIS Extraction ➔
                      </button>
                  </div>
              </div>
          </div>
        </div>
      );
  }

  // MICRO VIEW (Live Mission)
  const gridRows = gameState?.grid?.length || 30;
  const maxGridSize = Math.max(16, Math.min(28, 500 / gridRows)); 

  return (
    <div className="flex flex-col h-screen bg-[#050505] text-slate-200 font-sans overflow-hidden">
      
      {/* MISSION CONTROL TOP BAR */}
      <div className="w-full bg-black/90 border-b border-white/10 px-6 py-2 flex justify-between items-center text-[10px] font-bold text-slate-300 z-50 shadow-2xl relative uppercase tracking-wider">
          <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-cyan-400 cursor-pointer hover:text-white transition-colors" onClick={() => setCurrentView('MACRO')}>
                  <Activity className="w-4 h-4"/> AEGIS COMMAND (DELTA)
              </div>
              <div className="w-px h-4 bg-white/20"></div>
              <span>Civilians Detected: <strong className="text-white">12</strong></span>
              <span>Critical Zones: <strong className="text-red-400">4</strong></span>
              <span>Rescue Success: <strong className="text-emerald-400">87%</strong></span>
          </div>
          <div className="flex items-center gap-6">
              <span>Active Fleet: <strong className="text-white">3</strong></span>
              <span>Est. Rescue Time: <strong className="text-white">8 min</strong></span>
              <div className="w-px h-4 bg-white/20"></div>
              <span className="text-emerald-400 flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div> SAT-LINK ONLINE</span>
          </div>
      </div>

      <div className="flex flex-1 overflow-hidden relative">
          
          {/* Mission Debrief Modal Overlay */}
          <AnimatePresence>
              {gameState?.status === "WIN" && (
                  <motion.div 
                    initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
                    animate={{ opacity: 1, backdropFilter: "blur(10px)" }}
                    className="absolute inset-0 z-[100] bg-black/80 flex items-center justify-center p-12"
                  >
                      <motion.div 
                          initial={{ scale: 0.9, y: 20 }}
                          animate={{ scale: 1, y: 0 }}
                          className="bg-black/90 border border-white/20 p-10 rounded-2xl shadow-[0_0_100px_rgba(6,182,212,0.3)] max-w-2xl w-full relative overflow-hidden"
                      >
                          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-emerald-500"></div>
                          <div className="flex items-center gap-3 text-cyan-400 mb-6 border-b border-white/10 pb-4">
                              <FileText className="w-8 h-8" />
                              <h2 className="text-3xl font-black uppercase tracking-widest text-white">Mission Report</h2>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-8 mb-8 font-mono">
                              <div>
                                  <div className="text-xs text-slate-500 mb-1">Mission ID</div>
                                  <div className="text-white font-bold text-lg">AR-2026-44</div>
                              </div>
                              <div>
                                  <div className="text-xs text-slate-500 mb-1">Status</div>
                                  <div className="text-emerald-400 font-bold text-lg">SUCCESS</div>
                              </div>
                              <div>
                                  <div className="text-xs text-slate-500 mb-1">Civilians Rescued</div>
                                  <div className="text-white font-bold text-lg">12 / 12</div>
                              </div>
                              <div>
                                  <div className="text-xs text-slate-500 mb-1">Hazards Avoided</div>
                                  <div className="text-cyan-400 font-bold text-lg">8</div>
                              </div>
                          </div>

                          <button 
                            onClick={() => setCurrentView('MACRO')}
                            className="w-full py-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-bold transition-all shadow-[0_0_30px_rgba(6,182,212,0.4)] tracking-widest uppercase text-sm"
                          >
                            RETURN TO GLOBAL COMMAND
                          </button>
                      </motion.div>
                  </motion.div>
              )}
          </AnimatePresence>

          {/* LEFT COLUMN: Map & Event Feed */}
          <div className="w-[50%] flex flex-col relative overflow-hidden z-10 border-r border-white/5 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900/40 to-[#020617]">
            
            <div className="p-4 flex-1 flex flex-col items-center justify-start relative">
                
                <div className="w-full flex justify-between items-center mb-4 z-20">
                    <div className="bg-black/80 backdrop-blur-xl p-2.5 px-4 rounded-xl border border-white/10 shadow-2xl flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,1)]"></div>
                        <h1 className="text-[10px] font-black text-white tracking-widest uppercase opacity-90">Digital Twin Topology</h1>
                    </div>
                    
                    <div className="flex items-center gap-4 text-[10px] font-bold text-slate-300 bg-black/80 backdrop-blur-xl px-4 py-2.5 rounded-xl border border-white/10 shadow-2xl">
                        <div className="flex items-center gap-1.5"><Plane className="w-3 h-3 text-cyan-400 transform -rotate-45"/> Drone</div>
                        <div className="flex items-center gap-1.5"><Users className="w-3 h-3 text-emerald-400"/> Civilians</div>
                        <div className="flex items-center gap-1.5"><Flame className="w-3 h-3 text-red-500"/> Hazards</div>
                        <div className="flex items-center gap-1.5"><div className="w-3 h-3 border border-dashed border-red-500/50 bg-red-500/10"></div> Prediction</div>
                    </div>
                </div>

                <motion.div 
                    key={gameState?.step || 0}
                    initial={{ scale: 0.98, opacity: 0.8 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 20 }}
                    className="z-10 mt-2 shadow-[0_0_50px_rgba(6,182,212,0.1)] rounded-xl"
                >
                    {renderGrid(gameState?.grid, maxGridSize)}
                </motion.div>
                
                {/* Event Feed Component */}
                <div className="w-full mt-auto pt-4 z-20">
                    <div className="w-full bg-black/80 backdrop-blur-xl border border-white/10 rounded-xl p-3 h-[130px] flex flex-col shadow-2xl">
                        <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2 mb-2 border-b border-white/5 pb-2">
                            <Terminal className="w-3 h-3" /> Live Event Feed
                        </div>
                        <div className="flex-1 overflow-y-auto custom-scrollbar font-mono text-[10px] space-y-1.5 pr-2">
                            <AnimatePresence>
                                {eventLog.map((log, i) => (
                                    <motion.div 
                                        key={`${log.msg}-${i}`}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className={`flex gap-3 ${log.isAlert ? 'text-red-400' : 'text-slate-400'}`}
                                    >
                                        <span className="text-slate-600 flex-shrink-0">[{log.time}]</span>
                                        <span className={`${log.isAlert ? 'font-bold text-red-300' : ''}`}>{log.msg}</span>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>

                {/* Controls */}
                <div className="absolute bottom-6 right-6 z-30 flex items-center gap-2 pointer-events-auto">
                    <button 
                        onClick={() => setAutoRun(!autoRun)}
                        className={`px-4 py-2 rounded-lg transition-all text-[10px] uppercase tracking-widest font-bold flex items-center gap-1.5 ${autoRun ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-white text-black hover:bg-slate-200 shadow-[0_0_20px_rgba(255,255,255,0.2)]'}`}
                    >
                    {autoRun ? <Square className="w-3 h-3 fill-current" /> : <Play className="w-3 h-3 fill-current" />}
                    {autoRun ? "Halt Operation" : "Execute Operation"}
                    </button>
                    <button 
                        onClick={() => stepGame()}
                        disabled={autoRun}
                        className="px-4 py-2 rounded-lg bg-black/80 backdrop-blur-xl hover:bg-white/10 disabled:opacity-50 transition-all text-white text-[10px] uppercase tracking-widest font-bold flex items-center gap-1.5 border border-white/20 shadow-2xl"
                    >
                    <FastForward className="w-3 h-3 fill-current" /> Tactical Step
                    </button>
                </div>
            </div>
          </div>

          {/* RIGHT COLUMN: AI Command Center */}
          <div className="w-[50%] flex flex-col h-full relative z-20 shadow-[-20px_0_50px_rgba(0,0,0,0.5)] px-6 py-5 overflow-y-auto custom-scrollbar bg-black/20">
             <AnimatePresence mode="wait">
             <motion.div 
                key={gameState?.step || 0}
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="flex flex-col gap-5 h-full"
             >
                 {/* Top Row: Fleet & Digital Twin */}
                 <div className="flex gap-4 shrink-0">
                     <motion.div variants={itemVariants} className="flex-1 bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-xl">
                         <h2 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                             <Plane className="w-3 h-3"/> Active Drone Fleet
                         </h2>
                         <div className="space-y-2 font-mono text-[10px]">
                             <div className="bg-cyan-900/20 p-2.5 rounded-lg border border-cyan-500/30 flex justify-between items-center">
                                 <span className="text-cyan-400 font-bold flex items-center gap-2"><Plane className="w-3 h-3 transform -rotate-45" /> Alpha</span>
                                 <span className="text-white">Fuel: 76%</span>
                             </div>
                             <div className="bg-white/5 p-2.5 rounded-lg border border-white/5 flex justify-between items-center">
                                 <span className="text-slate-400 font-bold flex items-center gap-2"><Plane className="w-3 h-3 transform -rotate-45" /> Bravo</span>
                                 <span className="text-white">Fuel: 54% (Med-Kit)</span>
                             </div>
                             <div className="bg-white/5 p-2.5 rounded-lg border border-white/5 flex justify-between items-center">
                                 <span className="text-slate-400 font-bold flex items-center gap-2"><Plane className="w-3 h-3 transform -rotate-45" /> Charlie</span>
                                 <span className="text-white">Fuel: 100% (Comm)</span>
                             </div>
                         </div>
                     </motion.div>

                     <motion.div variants={itemVariants} className="flex-1 bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-xl">
                         <h2 className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                             <Flame className="w-3 h-3"/> Digital Twin Prediction
                         </h2>
                         <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-lg text-xs text-red-300 font-medium leading-relaxed shadow-[0_0_15px_rgba(239,68,68,0.1)]">
                             Simulation Active. If no intervention occurs, hazard zone will expand by <strong>32%</strong> in <strong>T+15 mins</strong>, engulfing Sector D4.
                         </div>
                     </motion.div>
                 </div>
                 
                 {/* Middle Row: Triage Engine */}
                 <motion.div variants={itemVariants} className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-xl shrink-0">
                     <div className="text-[10px] font-black text-cyan-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                         <Activity className="w-3 h-3"/> AEGIS Triage Engine
                     </div>
                     <div className="bg-black/80 p-3 rounded-xl border border-white/5 font-mono text-[10px] space-y-3">
                         <div className="flex flex-col border-b border-white/5 pb-3">
                             <div className="flex justify-between items-center mb-1">
                                 <span className="text-red-400 font-bold">Victim A (Sector {toSector(goalPos?.r, goalPos?.c)})</span>
                                 <div className="flex items-center gap-2">
                                     <span className="text-red-400/80">CRITICAL</span>
                                     <span className="bg-red-500/20 text-red-300 px-2 rounded">12m window</span>
                                 </div>
                             </div>
                             <span className="text-cyan-400 font-bold">➔ Prioritized: Assigned Alpha</span>
                         </div>
                         <div className="flex flex-col border-b border-white/5 pb-3">
                             <div className="flex justify-between items-center mb-1">
                                 <span className="text-amber-400 font-bold">Victim B (Sector {toSector(victimBPos?.r, victimBPos?.c)})</span>
                                 <div className="flex items-center gap-2">
                                     <span className="text-amber-400/80">HIGH</span>
                                     <span className="bg-amber-500/20 text-amber-300 px-2 rounded">45m window</span>
                                 </div>
                             </div>
                             <span className="text-slate-400 font-bold">➔ Assigned: Bravo</span>
                         </div>
                         <div className="flex flex-col">
                             <div className="flex justify-between items-center mb-1">
                                 <span className="text-emerald-400 font-bold">Victim C (Sector {toSector(victimCPos?.r, victimCPos?.c)})</span>
                                 <div className="flex items-center gap-2">
                                     <span className="text-emerald-400/80">LOW</span>
                                     <span className="bg-emerald-500/20 text-emerald-300 px-2 rounded">120m window</span>
                                 </div>
                             </div>
                             <span className="text-slate-500 font-bold">➔ AWAITING ASSET</span>
                         </div>
                     </div>
                 </motion.div>

                 {/* Bottom Row: Ask Command AI */}
                 <motion.div variants={itemVariants} className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl shadow-xl flex-grow flex flex-col overflow-hidden">
                     <div className="p-3 border-b border-white/10 flex items-center gap-2 bg-white/5">
                         <Cpu className="w-4 h-4 text-cyan-400" />
                         <span className="text-[10px] font-black text-white uppercase tracking-widest">Ask Command AI</span>
                     </div>
                     
                     <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar text-[11px] font-medium">
                         {chatMessages.map((m, i) => (
                             <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                 <div className={`max-w-[85%] rounded-lg p-3 whitespace-pre-line ${
                                     m.role === 'user' 
                                     ? 'bg-cyan-600/30 text-white border border-cyan-500/50' 
                                     : 'bg-white/5 text-slate-300 border border-white/10'
                                 }`}>
                                     {m.msg}
                                 </div>
                             </div>
                         ))}
                         <div ref={chatEndRef} />
                     </div>
                     
                     <form onSubmit={handleChatSubmit} className="p-3 border-t border-white/10 bg-black/40 flex gap-2">
                         <input 
                             type="text" 
                             value={chatInput}
                             onChange={e => setChatInput(e.target.value)}
                             placeholder="E.g. Why was Alpha assigned to F7?" 
                             className="flex-1 bg-black/50 border border-white/20 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-400 transition-colors"
                         />
                         <button type="submit" className="bg-cyan-600 hover:bg-cyan-500 text-white p-2 rounded-lg transition-colors">
                             <Send className="w-4 h-4" />
                         </button>
                     </form>
                 </motion.div>

             </motion.div>
             </AnimatePresence>
          </div>

      </div>
    </div>
  );
}
