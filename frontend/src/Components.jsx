import React, { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';
import { ShieldAlert, Cpu, HardDrive, Leaf, WifiOff, Scan, Lock, Unlock } from 'lucide-react';

export const ScrollStyle = () => (
    <style dangerouslySetInnerHTML={{
        __html: `
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    .custom-scroll::-webkit-scrollbar { width: 4px; }
    .custom-scroll::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.02); }
    .custom-scroll::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.3); border-radius: 10px; }
    body { background-color: #030303; margin: 0; padding: 0; overflow-x: hidden; color: white; font-family: 'Inter', sans-serif; }
    .grain::after { content: ""; position: fixed; top: -100%; left: -100%; right: -100%; bottom: -100%; background-image: url("https://grainy-gradients.vercel.app/noise.svg"); opacity: 0.05; pointer-events: none; z-index: 1; }
    .glass-border { border: 1px solid rgba(255, 255, 255, 0.1); border-top: 1px solid rgba(255, 255, 255, 0.2); border-left: 1px solid rgba(255, 255, 255, 0.2); }
    .scanner-line { height: 2px; background: linear-gradient(90deg, transparent, #3b82f6, transparent); box-shadow: 0 0 15px #3b82f6; width: 100%; position: absolute; z-index: 20; }
    @media print {
      .no-print { display: none !important; }
      body { background: white !important; color: black !important; }
      #forensic-report { display: block !important; width: 100% !important; margin: 0 !important; }
      .print-card { border: none !important; break-inside: avoid !important; background: white !important; color: black !important; height: auto !important; overflow: visible !important; margin-bottom: 30px !important; box-shadow: none !important; }
      .ledger-table { color: black !important; width: 100% !important; border-collapse: collapse; }
      .ledger-table th, .ledger-table td { border-bottom: 1px solid #eee !important; padding: 15px !important; color: black !important; }
      .recharts-surface { filter: invert(1) hue-rotate(180deg) brightness(0.8) !important; }
    }
  `}} />
);

export const SnowyParticles = () => {
    const [particles, setParticles] = useState([]);
    useEffect(() => {
        const p = Array.from({ length: 70 }).map((_, i) => ({ id: i, startX: Math.random() * 100, duration: 12 + Math.random() * 20, delay: Math.random() * -30, size: 1.5 + Math.random() * 3.5, opacity: 0.15 + Math.random() * 0.45, drift: (Math.random() - 0.5) * 12 }));
        setParticles(p);
    }, []);
    return (
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
            {particles.map((p) => (
                <motion.div key={p.id} initial={{ y: "-10vh", x: `${p.startX}vw`, opacity: 0 }} animate={{ y: "110vh", x: `${p.startX + p.drift}vw`, opacity: [0, p.opacity, p.opacity, 0] }} transition={{ duration: p.duration, repeat: Infinity, delay: p.delay, ease: "linear" }} style={{ position: 'absolute', width: `${p.size}px`, height: `${p.size}px`, backgroundColor: '#3b82f6', borderRadius: '50%', filter: 'blur(1.5px)', boxShadow: '0 0 15px rgba(59, 130, 246, 0.8)' }} />
            ))}
        </div>
    );
};

export const MetricBox = ({ title, value, sub, danger, delta, invertDelta, mouseX, mouseY }) => {
    const isPos = invertDelta ? delta < 0 : delta > 0;
    return (
        <div className="relative p-14 rounded-[4rem] glass-border bg-white/[0.03] transition-all hover:scale-[1.02] group overflow-hidden">
            <GlassHighlight mouseX={mouseX} mouseY={mouseY} />
            <div className="relative z-10">
                <div className="flex justify-between items-start mb-12">
                    <p className="text-[10px] font-black tracking-[0.4em] uppercase opacity-20">{title}</p>
                    {delta !== 0 && !isNaN(delta) && <span className={`text-[11px] font-bold px-4 py-1.5 rounded-2xl border ${isPos ? 'border-green-500/20 text-green-400' : 'border-red-500/20 text-red-400'}`}>{delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)}</span>}
                </div>
                <p className={`text-[5rem] font-bold tracking-tighter leading-none ${danger ? 'text-red-500' : 'text-white'}`}>{value}</p>
                <p className="text-[12px] mt-8 opacity-10 font-black uppercase tracking-[0.3em]">{sub}</p>
            </div>
        </div>
    );
};

export const DashboardCard = ({ title, icon, children, height, isScrollable, headerExtras, mouseX, mouseY }) => (
    <div className={`relative bg-white/[0.03] backdrop-blur-[25px] glass-border rounded-[4.5rem] ${height} flex flex-col overflow-hidden transition-all shadow-3xl group`}>
        <GlassHighlight mouseX={mouseX} mouseY={mouseY} />
        <div className="relative z-10 p-14 pb-8 flex items-center gap-6">
            <div className="flex items-center gap-6 opacity-30 group-hover:opacity-100 transition-opacity"><div className="p-4 bg-white/5 rounded-[1.5rem] text-blue-500 no-print">{icon}</div><span className="text-[11px] font-black tracking-[0.5em] uppercase">{title}</span></div>
            {headerExtras}
        </div>
        <div className={`relative z-10 flex-grow no-scrollbar ${isScrollable ? 'overflow-y-auto custom-scroll' : 'p-14 pt-0'}`}>{children}</div>
    </div>
);

export const GlassHighlight = ({ mouseX, mouseY }) => {
    const containerRef = useRef(null);
    const x = useMotionValue(0);
    const y = useMotionValue(0);
    useEffect(() => {
        return mouseX.onChange((latest) => { if (containerRef.current) { const rect = containerRef.current.getBoundingClientRect(); x.set(latest - rect.left); } });
    }, [mouseX]);
    useEffect(() => {
        return mouseY.onChange((latest) => { if (containerRef.current) { const rect = containerRef.current.getBoundingClientRect(); y.set(latest - rect.top); } });
    }, [mouseY]);
    return <motion.div ref={containerRef} className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500" style={{ background: useTransform([x, y], ([latestX, latestY]) => `radial-gradient(600px circle at ${latestX}px ${latestY}px, rgba(255,255,255,0.06), transparent 40%)`) }} />;
};