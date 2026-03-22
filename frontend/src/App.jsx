import React, { useState, useMemo, useEffect, useRef, Component } from 'react';
import { Shield, Activity, Terminal, ChevronDown, ChevronUp, List, Fingerprint, Clock, Share2, ExternalLink, Zap, FileText, Download, ArrowUp, ShieldAlert, Globe, Check, Menu, X, Settings, EyeOff, Radio, Percent, Database, Unlock, Lock, Cpu, HardDrive, WifiOff, Box, BarChart3, Scan, Leaf, AlertTriangle, FileWarning, Scale, Search, Filter } from 'lucide-react';
import { motion, AnimatePresence, useSpring, useMotionValue, useScroll, useTransform } from 'framer-motion';
import { ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, Radar, RadarChart, PolarGrid, PolarAngleAxis, AreaChart, Area, CartesianGrid } from 'recharts';

// --- Global CSS for Texture, Reset, and PDF Formatting ---
const ScrollStyle = () => (
  <style dangerouslySetInnerHTML={{
    __html: `
      /* Immersive Scroll - Hidden but functional */
      * { -ms-overflow-style: none; scrollbar-width: none; }
      *::-webkit-scrollbar { display: none; }
      
      body { 
        background-color: #030303; 
        margin: 0; 
        padding: 0; 
        overflow-x: hidden; 
        color: white; 
        font-family: 'Inter', system-ui, sans-serif; 
      }
      
      html { scroll-behavior: smooth; }
      
      .grain::after { 
        content: ""; 
        position: fixed; 
        top: -100%; left: -100%; right: -100%; bottom: -100%; 
        background-image: url("https://grainy-gradients.vercel.app/noise.svg"); 
        opacity: 0.05; 
        pointer-events: none; 
        z-index: 1; 
      }
      
      .glass-border { 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-top: 1px solid rgba(255, 255, 255, 0.2); 
        border-left: 1px solid rgba(255, 255, 255, 0.2); 
      }
      
      .scanner-line { 
        height: 2px; 
        background: linear-gradient(90deg, transparent, #3b82f6, transparent); 
        box-shadow: 0 0 15px #3b82f6; 
        width: 100%; 
        position: absolute; 
        z-index: 20; 
      }
      
      /* Filter Dropdown Visibility Fix */
      select option {
        background-color: white !important;
        color: black !important;
      }

      @media print {
        @page { margin: 1.5cm; }
        .no-print { display: none !important; }
        body { background: white !important; color: #1a1a1a !important; overflow: visible !important; }
        .grain::after { display: none !important; }
        #forensic-report { display: block !important; width: 100% !important; margin: 0 !important; padding: 0 !important; }
        
        .metric-container, .sensor-grid, .tool-suite, .chart-row, .search-filter-bar, .timeline-row { display: none !important; }
        
        .print-card { 
            border: 1px solid #e5e7eb !important; 
            break-inside: auto !important; 
            background: white !important; 
            color: #1a1a1a !important; 
            height: auto !important; 
            overflow: visible !important; 
            box-shadow: none !important; 
            margin-bottom: 0 !important; 
            border-radius: 12px !important;
            width: 100% !important;
        }
        
        .ledger-table { color: #1a1a1a !important; width: 100% !important; border-collapse: collapse; }
        .ledger-table th { 
            background: #f9fafb !important; 
            color: #111827 !important; 
            font-weight: 800 !important; 
            text-transform: uppercase !important; 
            font-size: 8px !important; 
            padding: 15px !important;
            border-bottom: 2px solid #e5e7eb !important;
            text-align: left !important;
        }
        .ledger-table td { 
            border-bottom: 1px solid #f3f4f6 !important; 
            padding: 12px 15px !important; 
            color: #1a1a1a !important; 
            font-size: 11px !important; 
        }
        .shadow-fire-text { color: #dc2626 !important; font-weight: bold !important; }
        .normal-text { color: #4b5563 !important; }
        .print-footer { display: block !important; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; font-size: 10px; color: #6b7280; text-align: left; line-height: 1.6; }
      }
      .print-footer { display: none; }
    `
  }} />
);

const SnowyParticles = () => {
  const [particles, setParticles] = useState([]);
  useEffect(() => {
    const p = Array.from({ length: 70 }).map((_, i) => ({
      id: i, startX: Math.random() * 100, duration: 12 + Math.random() * 20,
      delay: Math.random() * -30, size: 1.5 + Math.random() * 3.5,
      opacity: 0.15 + Math.random() * 0.45, drift: (Math.random() - 0.5) * 12
    }));
    setParticles(p);
  }, []);
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0 no-print">
      {particles.map((p) => (
        <motion.div key={p.id} initial={{ y: "-10vh", x: `${p.startX}vw`, opacity: 0 }}
          animate={{ y: "110vh", x: `${p.startX + p.drift}vw`, opacity: [0, p.opacity, p.opacity, 0] }}
          transition={{ duration: p.duration, repeat: Infinity, delay: p.delay, ease: "linear" }}
          style={{ position: 'absolute', width: `${p.size}px`, height: `${p.size}px`, backgroundColor: '#3b82f6', borderRadius: '50%', filter: 'blur(1.5px)', boxShadow: '0 0 15px rgba(59, 130, 246, 0.8)' }} />
      ))}
    </div>
  );
};

class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#030303] flex flex-col items-center justify-center p-10 text-center text-white">
          <ShieldAlert size={40} className="text-red-500 mb-8" />
          <h1 className="text-2xl font-bold mb-4">System Interruption</h1>
          <button onClick={() => window.location.reload()} className="px-8 py-3 bg-white text-black rounded-2xl font-bold text-sm hover:bg-blue-600 hover:text-white transition-all">Restart System</button>
        </div>
      );
    }
    return this.props.children;
  }
}

const BRAND_MAP = {
  'Google': ['google', 'gstatic', 'doubleclick', 'googlesyndication', '2mdn', 'youtube', 'ggpht', 'googleapis'],
  'Meta': ['facebook', 'fbcdn', 'fbevents', 'instagram', 'cdninstagram', 'whatsapp'],
  'Amazon': ['amazon', 'amazonaws', 'media-amazon', 'amazon-adsystem', 'assoc-amazon'],
  'Microsoft': ['microsoft', 'bing', 'clarity', 'azure', 'live.com', 'office', 'skype'],
  'Apple': ['apple', 'mzstatic', 'icloud'],
  'ByteDance': ['tiktok', 'byteoversea', 'ibyteimg', 'musical.ly'],
  'Adobe': ['adobe', 'demdex', 'typekit', 'omtrdc']
};

const AmbientBackground = () => (
  <div className="fixed inset-0 pointer-events-none no-print" style={{ zIndex: 0 }}>
    <div className="absolute inset-0 bg-[#030303]" />
    <div className="absolute inset-0 opacity-[0.4]" style={{ backgroundImage: `linear-gradient(to right, rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.08) 1px, transparent 1px)`, backgroundSize: '60px 60px', maskImage: 'radial-gradient(ellipse at center, black, transparent 90%)' }} />
    <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(15,30,70,0.15)_0%,#030303_100%)]" />
  </div>
);

const ScrollToTop = () => {
  const [visible, setVisible] = useState(false);
  const { scrollY } = useScroll();
  useEffect(() => scrollY.on("change", (latest) => setVisible(latest > 400)), [scrollY]);
  return (
    <AnimatePresence>
      {visible && (
        <motion.button initial={{ opacity: 0, scale: 0.5, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.5, y: 20 }} onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="fixed bottom-10 right-10 z-[100] p-5 rounded-3xl bg-white text-black shadow-2xl hover:bg-blue-600 hover:text-white transition-all group no-print">
          <ArrowUp size={24} className="group-hover:-translate-y-1 transition-transform" />
        </motion.button>
      )}
    </AnimatePresence>
  );
};

function PrivacyApp() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [data, setData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [activeProtections, setActiveProtections] = useState([]);
  const [history, setHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');
  const logEndRef = useRef(null);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  useEffect(() => {
    document.title = "Privacy Detective";
  }, []);

  useEffect(() => {
    const handleMove = (e) => { mouseX.set(e.clientX); mouseY.set(e.clientY); };
    window.addEventListener("mousemove", handleMove);
    return () => window.removeEventListener("mousemove", handleMove);
  }, [mouseX, mouseY]);

  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  const audit = useMemo(() => {
    if (!data) return null;
    try {
      const acceptTrackers = Array.isArray(data.accept_total_trackers) ? data.accept_total_trackers : [];
      const rejectTrackers = Array.isArray(data.reject_total_trackers) ? data.reject_total_trackers : [];
      const perf = data.performance_metrics || {};
      const hasConsentForm = data.banner_found || false;

      const brandCounts = {};
      const riskCategories = { Marketing: 5, Analytics: 5, Functional: 5, Identity: 5, Fingerprinting: 5 };
      let trackerPenalty = 0;
      let shadowFireCount = 0;

      const rejectDomains = new Set(rejectTrackers.map(t => String(t.domain).toLowerCase()));

      const processed = acceptTrackers.map((t, idx) => {
        const domain = String(t?.domain || 'Unknown').toLowerCase();
        let brandName = 'Independent';
        for (const [name, keys] of Object.entries(BRAND_MAP)) {
          if (keys.some(k => domain.includes(k))) { brandName = name; break; }
        }

        let cat = String(t?.category || '').toLowerCase();
        if (cat.includes('essential') || cat.includes('infrastructure')) cat = 'functional';

        const isShadowFire = hasConsentForm && rejectDomains.has(domain);
        if (isShadowFire) shadowFireCount++;

        if (cat.includes('ads') || cat.includes('marketing')) { riskCategories.Marketing += 15; trackerPenalty += 3.5; }
        else if (cat.includes('analytics')) { riskCategories.Analytics += 10; trackerPenalty += 1.5; }
        else if (cat.includes('spyware') || cat.includes('fingerprint')) { riskCategories.Fingerprinting += 20; trackerPenalty += 8.0; }
        else if (cat.includes('social') || cat.includes('identity')) { riskCategories.Identity += 12; trackerPenalty += 4.0; }
        else if (cat.includes('functional')) { riskCategories.Functional += 2; trackerPenalty += 0.5; }
        else { trackerPenalty += 0.5; }

        brandCounts[brandName] = (brandCounts[brandName] || 0) + 1;
        return { ...t, category: cat, brandName, id: idx, isShadowFire };
      });

      const totalEntities = Object.keys(brandCounts).length;
      const baseScore = Math.max(5, 100 - (trackerPenalty + totalEntities * 4));

      const tools = [
        { id: 'blocker', name: "Deploy Ad-Blocking", action: "Install uBlock Origin", link: "https://ublockorigin.com/", desc: "Stops tracking scripts from ever reaching your computer by stripping advertisement code before it executes.", impact: 0.85 },
        { id: 'shield', name: "Enforce Private DNS", action: "Setup NextDNS", link: "https://nextdns.io/", desc: "Blocks tracking requests at the network level. This protects every app on your device.", impact: 0.45 },
        { id: 'isolate', name: "Harden Browser Settings", action: "Switch to Brave/Firefox", link: "https://brave.com/", desc: "Enable 'Strict' protection to hide your hardware signature (Fingerprinting).", impact: 0.25 }
      ];

      let boost = 0;
      activeProtections.forEach(id => {
        const tool = tools.find(t => t.id === id);
        if (tool) boost = Math.min(0.98, boost + tool.impact);
      });

      const checkRisk = (keys) => processed.some(t => keys.some(k => (t.category + t.domain).toLowerCase().includes(k)));

      const leakageTypes = [
        { name: "Public IP Address", unprotected: "Exposed", protected: "Masked (VPN/Proxy)", active: activeProtections.includes('shield'), keys: ['ip', 'geo', 'location'] },
        { name: "Canvas Fingerprint", unprotected: "Unique ID", protected: "Noise Injected", active: activeProtections.includes('isolate'), keys: ['fingerprint', 'canvas', 'hardware'] },
        { name: "Device UUID", unprotected: "Harvested", protected: "Blocked", active: activeProtections.includes('blocker'), keys: ['uuid', 'guid', 'deviceid'] },
        { name: "WebGL Signature", unprotected: "Extracted", protected: "Standardized", active: activeProtections.includes('isolate'), keys: ['webgl', 'gpu', 'graphics'] },
        { name: "Battery Status", unprotected: "Telemetry Leak", protected: "Restricted", active: activeProtections.includes('blocker') || activeProtections.includes('isolate'), keys: ['battery', 'power'] },
        { name: "User Agent", unprotected: "Exact Match", protected: "Spoofed", active: activeProtections.includes('isolate'), keys: ['browser', 'version', 'agent'] },
        { name: "Local Storage", unprotected: "Tracking Cookies", protected: "Cleared", active: activeProtections.includes('blocker'), keys: ['cookie', 'storage', 'pixel'] },
        { name: "ISP Metadata", unprotected: "DNS Leaking", protected: "DoH Encrypted", active: activeProtections.includes('shield'), keys: ['dns', 'isp', 'provider'] }
      ];

      return {
        url: data.target_url || url,
        hasConsentForm,
        safetyScore: Math.round(baseScore),
        optimizedScore: Math.min(100, Math.round(baseScore + ((100 - baseScore) * boost))),
        trackers: processed.length,
        shadowFires: shadowFireCount,
        optimizedTrackers: Math.round(processed.length * (1 - boost)),
        riskData: Object.entries(riskCategories).map(([subject, A]) => ({ subject, A })),
        brandData: Object.entries(brandCounts).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count).slice(0, 6),
        timeline: Array.isArray(data.timeline_data) ? data.timeline_data : [],
        fullList: processed,
        totalEntities,
        tools,
        leaks: leakageTypes.map(l => ({ type: l.name, isSafe: l.active || !checkRisk(l.keys), status: l.active ? l.protected : checkRisk(l.keys) ? l.unprotected : "No Activity" })),
        efficiency: {
          tax: perf.performance_tax_percent || 0,
          size: perf.data_transfer_mb || 0,
          carbon: perf.carbon_footprint_g || 0
        },
        auditId: `PD-AUDIT-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
        timestamp: new Date().toUTCString()
      };
    } catch (e) { return null; }
  }, [data, activeProtections, url]);

  const filteredList = useMemo(() => {
    if (!audit) return [];
    return audit.fullList.filter(t => {
      const matchSearch = t.domain.toLowerCase().includes(searchTerm.toLowerCase()) || t.brandName.toLowerCase().includes(searchTerm.toLowerCase());
      const matchCat = filterCategory === 'All' || t.category.toLowerCase().includes(filterCategory.toLowerCase());
      return matchSearch && matchCat;
    });
  }, [audit, searchTerm, filterCategory]);

  const handleAnalyze = (targetUrl = url) => {
    if (!targetUrl) return;
    const cleanUrl = targetUrl.startsWith('http') ? targetUrl : `https://${targetUrl}`;
    setUrl(cleanUrl); setLoading(true); setProgress(0); setLogs([]); setActiveProtections([]);
    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/scan`);
    socket.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "log") msg.message.startsWith("PROGRESS:") ? setProgress(Number(msg.message.split(":")[1])) : setLogs(p => [...p, msg.message]);
      if (msg.type === "data") { setData(msg.payload); setLoading(false); setHistory(prev => [{ url: msg.payload.target_url || cleanUrl, score: msg.payload.score, time: new Date().toLocaleTimeString() }, ...prev.slice(0, 9)]); }
    };
    socket.onopen = () => socket.send(cleanUrl);
    socket.onerror = () => { setLoading(false); setLogs(p => [...p, "Error: System backend unreachable."]); };
  };

  const exportCSV = () => {
    if (!audit) return;
    const rows = audit.fullList.map(t => `"${t.brandName}","${t.category}","${t.domain}","${t.isShadowFire}"`).join("\n");
    const blob = new Blob([`Collector,Category,Domain,ShadowFire\n${rows}`], { type: 'text/csv' });
    const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = `audit_${Date.now()}.csv`; link.click();
  };

  return (
    <div className="relative min-h-screen grain">
      <ScrollStyle />
      <AmbientBackground />
      <SnowyParticles />
      <ScrollToTop />
      <div className="relative z-10 w-full flex flex-col items-center">
        <button onClick={() => setShowHistory(!showHistory)} className="fixed left-8 top-10 z-50 p-4 rounded-2xl bg-white/[0.05] glass-border backdrop-blur-3xl hover:bg-white/[0.1] transition-all no-print">
          {showHistory ? <X size={20} className="opacity-60" /> : <Menu size={20} className="opacity-60" />}
        </button>

        <AnimatePresence>
          {showHistory && (
            <motion.aside initial={{ x: -300 }} animate={{ x: 0 }} exit={{ x: -300 }} className="fixed left-0 top-0 bottom-0 w-80 bg-black/40 backdrop-blur-[100px] border-r border-white/10 z-40 p-10 pt-32 overflow-y-auto no-print">
              <div className="flex items-center gap-3 mb-10 opacity-40 font-bold text-[10px] tracking-[0.3em]">SEARCH HISTORY</div>
              {history.map((h, i) => (
                <div key={i} onClick={() => { handleAnalyze(h.url); setShowHistory(false); }} className="group cursor-pointer p-6 rounded-[2rem] border border-transparent hover:border-white/10 hover:bg-white/[0.05] mb-4 transition-all">
                  <p className="text-xs font-bold text-white/50 truncate mb-1 group-hover:text-blue-400 font-mono tracking-tight">{h.url.replace('https://', '')}</p>
                  <div className="flex justify-between items-center text-[10px] opacity-25 font-bold"><span>{h.time}</span><span className="bg-white/10 px-2 py-0.5 rounded-lg">{h.score}</span></div>
                </div>
              ))}
            </motion.aside>
          )}
        </AnimatePresence>

        <div className="w-full max-w-7xl px-10">
          <main className="pb-40 pt-20">
            <header className="text-center pb-24 hero-header">
              <h1 className="text-[4rem] md:text-[6rem] font-bold tracking-tighter bg-gradient-to-b from-white to-white/10 bg-clip-text text-transparent leading-none">privacy detective.</h1>
              <p className="mt-6 text-white/30 text-xs font-black tracking-[0.6em] uppercase max-w-lg mx-auto leading-relaxed">Exposing hidden trackers and corporate data-sharing networks.</p>
              <div className={`max-w-2xl mx-auto mt-14 bg-white/[0.03] backdrop-blur-[100px] glass-border rounded-[3.5rem] overflow-hidden transition-all duration-1000 ${loading ? 'ring-2 ring-blue-500/30' : ''} no-print`}>
                <div className="flex p-3 border-b border-white/[0.05]">
                  <input value={url} onChange={e => setUrl(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleAnalyze()} placeholder="Target URL..." className="flex-grow bg-transparent px-8 py-5 outline-none text-xl font-medium text-white font-mono" />
                  <button onClick={() => handleAnalyze()} className="px-14 rounded-[2.5rem] font-black text-xs tracking-widest bg-white text-black hover:bg-blue-600 hover:text-white transition-all uppercase">{loading ? <Activity className="animate-spin" size={16} /> : "Scan"}</button>
                </div>
                <div className="bg-white/[0.01]">
                  <div className="flex items-center justify-between px-12 py-5 cursor-pointer opacity-30 hover:opacity-100" onClick={() => setShowLogs(!showLogs)}>
                    <div className="flex items-center gap-2"><Terminal size={14} className="text-blue-500" /><span className="text-[10px] font-black uppercase tracking-widest">Live Audit Log</span></div>
                    {showLogs ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                  <AnimatePresence>{showLogs && (<motion.div initial={{ height: 0 }} animate={{ height: "auto" }} exit={{ height: 0 }} className="overflow-hidden border-t border-white/[0.03]"><div className="px-12 py-8 h-40 overflow-y-auto space-y-2 font-mono text-[11px] text-white/20 bg-black/40">{logs.map((log, i) => <div key={i} className="flex gap-4"><span>{i + 1}</span><span>{log}</span></div>)}<div ref={logEndRef} /></div></motion.div>)}</AnimatePresence>
                </div>
                {loading && <motion.div animate={{ width: `${progress}%` }} className="h-1 bg-blue-500" />}
              </div>
            </header>

            <AnimatePresence mode="wait">
              {audit && !loading && (
                <motion.div id="forensic-report" initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} className="space-y-12 mt-20">

                  {/* METRIC ROW */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 metric-container no-print">
                    <MetricBox title="Trust Score" value={`${audit.optimizedScore}%`} sub="Compliance Health" delta={audit.optimizedScore - audit.safetyScore} />
                    <MetricBox title="Total Trackers" value={audit.optimizedTrackers} danger={audit.optimizedTrackers > 15} sub="Telemetry Points" delta={audit.optimizedTrackers - audit.trackers} invertDelta={true} icon={<Activity size={14} />} />
                    <MetricBox title="Consent Form" value={audit.hasConsentForm ? "DET" : "VOID"} sub={audit.hasConsentForm ? "Detected" : "Form Not Found"} icon={<Scale size={14} />} danger={!audit.hasConsentForm} />
                    <MetricBox title="Shadow Fires" value={audit.shadowFires} sub="Unauthorized Execs" icon={<FileWarning size={14} />} danger={audit.shadowFires > 0} />
                  </div>

                  {/* SENSORS ROW */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 sensor-grid no-print">
                    <div className="lg:col-span-2">
                      <DashboardCard title="Forensic Leakage Sensors" icon={<Radio size={16} />} height="h-[650px]" isScrollable={true}>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4 px-4 pb-10">
                          {audit.leaks.map((leak, i) => (
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} key={i} className={`p-10 rounded-[3rem] border transition-all duration-500 relative overflow-hidden group/leak ${leak.isSafe ? 'bg-blue-500/5 border-blue-500/20 hover:bg-blue-500/10' : 'bg-red-500/5 border-red-500/20 hover:bg-red-500/10'}`}>
                              <motion.div animate={{ y: ["0%", "500%"] }} transition={{ duration: 3, repeat: Infinity, ease: "linear" }} className={`scanner-line opacity-10 ${leak.isSafe ? 'bg-blue-500' : 'bg-red-500'}`} />
                              <div className="relative z-10">
                                <div className="flex justify-between items-start mb-6">{leak.isSafe ? <Lock size={16} className="text-blue-500" /> : <Unlock size={16} className="text-red-500 animate-pulse" />}</div>
                                <h4 className="text-lg font-bold text-white/90 mb-2">{leak.type}</h4>
                                <p className={`text-[11px] font-mono uppercase tracking-[0.2em] ${leak.isSafe ? 'text-blue-400' : 'text-red-500/60'}`}>{leak.status}</p>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </DashboardCard>
                    </div>
                    <DashboardCard title="Resource Audit" icon={<Database size={16} />} height="h-[650px]" isScrollable={true}>
                      <div className="space-y-10 pt-10 px-4 overflow-y-auto h-full pb-20">
                        <ResourceItem icon={<Cpu size={20} />} label="Script Bloat" value={`+${Math.round(audit.efficiency.tax * 1.4)}%`} sub="Telemetry Overhead" danger />
                        <ResourceItem icon={<HardDrive size={20} />} label="Packet Size" value={`${audit.efficiency.size.toFixed(2)}MB`} sub="Unconsented Transfer" />
                        <ResourceItem icon={<Leaf size={20} />} label="Emissions" value={`${audit.efficiency.carbon.toFixed(3)}g`} sub="Wasteful CO2 Output" />
                      </div>
                    </DashboardCard>
                  </div>

                  {/* TOOLS ROW */}
                  <div className="w-full tool-suite no-print">
                    <DashboardCard title="Consent Enforcement Tools" icon={<Settings size={16} />} height="h-auto pb-16">
                      <div className="px-14 py-8 grid grid-cols-1 md:grid-cols-3 gap-10">
                        {audit.tools.map((tool) => {
                          const isActive = activeProtections.includes(tool.id);
                          return (
                            <div key={tool.id} className={`p-12 rounded-[4rem] glass-border transition-all flex flex-col justify-between ${isActive ? 'bg-blue-600/10 border-blue-500/50 shadow-3xl' : 'bg-white/[0.04] hover:bg-white/[0.08]'}`}>
                              <div>
                                <div className="flex justify-between items-start mb-8">
                                  <div onClick={() => setActiveProtections(p => isActive ? p.filter(t => t !== tool.id) : [...p, tool.id])} className={`p-5 rounded-3xl cursor-pointer transition-colors ${isActive ? 'bg-blue-600 text-white shadow-[0_0_30px_rgba(59,130,246,0.5)]' : 'bg-white/5 text-white/30 hover:bg-white/10'}`}>
                                    {isActive ? <Check size={22} /> : <Zap size={22} />}
                                  </div>
                                  <a href={tool.link} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-blue-600 text-[9px] font-black uppercase transition-all">Setup <ExternalLink size={10} /></a>
                                </div>
                                <h3 className="text-xl font-bold mb-2">{tool.name}</h3>
                                <p className="text-[10px] font-black text-blue-500 uppercase mb-6">Method: {tool.action}</p>
                                <p className="text-sm text-white/40 leading-relaxed mb-8">{tool.desc}</p>
                              </div>
                              <div className="pt-6 border-t border-white/5 flex items-center justify-between"><span className="text-[10px] font-bold text-white/20 uppercase">Risk Reduction</span><span className="text-sm font-black text-white">+{Math.round(tool.impact * 100)}%</span></div>
                            </div>
                          );
                        })}
                      </div>
                    </DashboardCard>
                  </div>

                  {/* CHARTS ROW */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 chart-row no-print">
                    <DashboardCard title="Forensic Fingerprint" icon={<Fingerprint size={16} />} height="h-[550px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={audit.riskData}>
                          <PolarGrid stroke="#ffffff08" />
                          <PolarAngleAxis dataKey="subject" tick={{ fill: '#ffffff30', fontSize: 11, fontWeight: 800 }} />
                          <Radar dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} animationDuration={1000} />
                        </RadarChart>
                      </ResponsiveContainer>
                    </DashboardCard>
                    <DashboardCard title="Violating Entities" icon={<Share2 size={16} />} height="h-[550px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={audit.brandData} layout="vertical" margin={{ left: 40, right: 60, top: 20, bottom: 20 }}>
                          <XAxis type="number" hide />
                          <YAxis dataKey="name" type="category" tick={{ fill: '#ffffff40', fontSize: 12, fontWeight: 900 }} width={140} axisLine={false} tickLine={false} />
                          <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} contentStyle={{ backgroundColor: '#0a0a0a', border: 'none' }} />
                          <Bar dataKey="count" fill="#3b82f6" radius={[0, 20, 20, 0]} barSize={34} animationDuration={1000} />
                        </BarChart>
                      </ResponsiveContainer>
                    </DashboardCard>
                  </div>

                  {/* TIMELINE ROW - FIXED DATA KEY TO MATCH BACKEND */}
                  <div className="w-full timeline-row no-print">
                    <DashboardCard title="Telemetry Ingestion Timeline" icon={<Clock size={16} />} height="h-[450px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={audit.timeline} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                          <defs>
                            <linearGradient id="colorTrack" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                          <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#ffffff20', fontSize: 10 }} />
                          <YAxis axisLine={false} tickLine={false} tick={{ fill: '#ffffff20', fontSize: 10 }} />
                          <Tooltip contentStyle={{ backgroundColor: '#0a0a0a', border: '1px solid #ffffff10', borderRadius: '15px' }} />
                          {/* Note: dataKey changed from 'count' to 'requests' to match main.py output */}
                          <Area type="monotone" dataKey="requests" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTrack)" animationDuration={2000} />
                        </AreaChart>
                      </ResponsiveContainer>
                    </DashboardCard>
                  </div>

                  {/* COMPLIANCE LEDGER (PDF TARGET) */}
                  <div className="w-full print-card">
                    <DashboardCard title="Privacy Compliance Ledger" isScrollable={true} height="h-[850px]" icon={<List size={16} />} headerExtras={(
                      <div className="flex gap-4 ml-auto no-print">
                        <button onClick={exportCSV} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/[0.05] glass-border text-[10px] font-black uppercase hover:bg-white/10 transition-all"><Download size={12} />CSV</button>
                        <button onClick={() => window.print()} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/[0.05] glass-border text-[10px] font-black uppercase hover:bg-white/10 transition-all"><FileText size={12} />PDF</button>
                      </div>
                    )}>

                      {/* SEARCH AND FILTER UI */}
                      <div className="px-14 pb-8 flex flex-col md:flex-row gap-6 search-filter-bar no-print">
                        <div className="relative flex-grow">
                          <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-white/20" size={16} />
                          <input value={searchTerm} onChange={e => setSearchTerm(e.target.value)} placeholder="Search domains or providers..." className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 pl-14 pr-6 text-sm font-medium outline-none focus:border-blue-500/50 transition-all placeholder:text-white/10" />
                        </div>
                        <div className="relative min-w-[200px]">
                          <Filter className="absolute left-6 top-1/2 -translate-y-1/2 text-white/20" size={16} />
                          <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)} className="w-full appearance-none bg-white/[0.03] border border-white/10 rounded-2xl py-4 pl-14 pr-10 text-sm font-black uppercase tracking-widest outline-none cursor-pointer hover:bg-white/[0.05] text-white">
                            <option value="All">All Categories</option>
                            <option value="Marketing">Marketing</option>
                            <option value="Analytics">Analytics</option>
                            <option value="Fingerprint">Fingerprinting</option>
                            <option value="Functional">Functional</option>
                          </select>
                          <ChevronDown className="absolute right-6 top-1/2 -translate-y-1/2 text-white/20 pointer-events-none" size={14} />
                        </div>
                      </div>

                      <table className="w-full text-left ledger-table">
                        <thead>
                          <tr className="no-print">
                            <th className="px-14 py-10 opacity-20 text-[10px] font-black tracking-widest uppercase">Collector</th>
                            <th className="px-14 py-10 opacity-20 text-[10px] font-black tracking-widest uppercase">Category</th>
                            <th className="px-14 py-10 opacity-20 text-[10px] font-black tracking-widest uppercase">Consent Status</th>
                          </tr>
                          <tr className="hidden @media print:table-row">
                            <th>ENTITY PROVIDER</th><th>TRACKER CATEGORY</th><th>FORENSIC AUDIT STATUS</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                          {filteredList.map((t, i) => (
                            <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                              <td className="px-14 py-8 text-sm font-bold text-white/40 group-hover:text-white uppercase tracking-tight @media print:px-0 @media print:text-[#1a1a1a]">{t.brandName}</td>
                              <td className="px-14 py-8 @media print:px-0"><span className="text-[11px] font-black px-5 py-2 rounded-full border border-white/5 text-white/20 group-hover:text-blue-500 group-hover:border-blue-500/30 transition-all @media print:border-none @media print:text-[#4b5563] @media print:p-0">{t.category}</span></td>
                              <td className="px-14 py-8 @media print:px-0">
                                <div className="flex items-center gap-4">
                                  <span className={`text-[10px] font-mono font-bold ${t.isShadowFire ? 'text-red-500 shadow-fire-text' : 'text-white/20 normal-text'}`}>
                                    {t.isShadowFire ? 'SHADOW FIRE (REJECTED)' : audit.hasConsentForm ? 'IDLE / REJECTED' : 'ACTIVE (NO FORM)'}
                                  </span>
                                  {t.isShadowFire && <AlertTriangle size={12} className="text-red-500 animate-pulse no-print" />}
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>

                      {/* PDF FOOTER SIGNATURE */}
                      <div className="print-footer">
                        <div className="flex justify-between font-bold mb-6 border-b border-gray-100 pb-4">
                          <div><span className="text-black">AUDIT ID:</span> {audit.auditId}</div>
                          <div><span className="text-black">TARGET:</span> {audit.url}</div>
                          <div><span className="text-black">TIMESTAMP:</span> {audit.timestamp}</div>
                        </div>
                        <p className="max-w-2xl">This forensic report was generated by Privacy Detective. It provides a point-in-time audit of network requests and execution behaviors. All detected entities listed in this ledger were captured during active browser telemetry monitoring.</p>
                      </div>
                    </DashboardCard>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </main>
        </div>
      </div>
    </div>
  );
}

const MetricBox = ({ title, value, sub, danger, delta, invertDelta, icon }) => {
  const isPos = invertDelta ? delta < 0 : delta > 0;
  return (
    <div className={`relative p-14 rounded-[4rem] glass-border bg-white/[0.02] backdrop-blur-[45px] transition-all hover:bg-white/[0.06] hover:border-white/30 hover:scale-[1.02] group overflow-hidden no-print`}>
      <div className="relative z-10">
        <div className="flex justify-between items-start mb-12">
          <div className="flex items-center gap-2">
            <div className={`opacity-20 group-hover:opacity-100 transition-opacity ${danger ? 'text-red-500' : 'text-blue-500'}`}>{icon}</div>
            <p className="text-[10px] font-black tracking-[0.4em] uppercase opacity-20">{title}</p>
          </div>
          {delta !== 0 && !isNaN(delta) && <span className={`text-[11px] font-bold px-4 py-1.5 rounded-2xl border ${isPos ? 'border-green-500/20 text-green-400' : 'border-red-500/20 text-red-400'}`}>{delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)}</span>}
        </div>
        <p className={`text-[5rem] font-bold tracking-tighter leading-none ${danger ? 'text-red-500' : 'text-white'}`}>{value}</p>
        <p className="text-[12px] mt-8 opacity-10 font-black uppercase tracking-[0.3em]">{sub}</p>
      </div>
      <div className="absolute inset-0 bg-blue-500/0 group-hover:bg-blue-500/5 transition-colors duration-500 pointer-events-none" />
    </div>
  );
};

const ResourceItem = ({ icon, label, value, sub, danger }) => (
  <div className={`p-8 rounded-[2.5rem] ${danger ? 'bg-red-500/5 border-red-500/10 hover:bg-red-500/10' : 'bg-white/[0.02] border-white/5 hover:bg-white/[0.06]'} border flex justify-between items-center group transition-all`}>
    <div className="flex items-center gap-6">
      <div className={`${danger ? 'text-red-500' : 'text-blue-500'} opacity-40 group-hover:opacity-100`}>{icon}</div>
      <div>
        <p className={`text-xs font-black uppercase ${danger ? 'text-red-500/50' : 'text-white/30'} tracking-widest`}>{label}</p>
        <p className="text-[10px] opacity-10 font-medium tracking-tighter uppercase">{sub}</p>
      </div>
    </div>
    <span className={`text-xl font-bold ${danger ? 'text-red-500' : 'text-white'}`}>{value}</span>
  </div>
);

const DashboardCard = ({ title, icon, children, height, isScrollable, headerExtras }) => (
  <div className={`relative bg-white/[0.01] backdrop-blur-[45px] glass-border rounded-[4.5rem] ${height} flex flex-col overflow-hidden transition-all hover:bg-white/[0.03] hover:border-white/20 shadow-3xl group print-card`}>
    <div className="relative z-10 p-14 pb-8 flex items-center gap-6 no-print">
      <div className="flex items-center gap-6 opacity-30 group-hover:opacity-100 transition-opacity">
        <div className="p-4 bg-white/5 rounded-[1.5rem] text-blue-500">{icon}</div>
        <span className="text-[11px] font-black tracking-[0.5em] uppercase">{title}</span>
      </div>
      {headerExtras}
    </div>
    <div className="hidden @media print:block px-12 py-10">
      <h2 className="text-3xl font-black uppercase tracking-[0.2em] text-[#1a1a1a] mb-2">{title}</h2>
      <p className="text-[9px] text-[#9ca3af] font-bold uppercase tracking-widest">Privacy Detective Forensic Intelligence Report</p>
    </div>
    <div className={`relative z-10 flex-grow ${isScrollable ? 'overflow-y-auto' : 'p-14 pt-0'}`}>{children}</div>
    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-transparent group-hover:from-blue-500/[0.02] transition-all duration-700 pointer-events-none no-print" />
  </div>
);

export default function App() { return <ErrorBoundary><PrivacyApp /></ErrorBoundary>; }