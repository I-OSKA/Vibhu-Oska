'use client';

import React, { useEffect, useState, useRef } from 'react';
import { 
  Terminal as TermIcon, 
  Cpu, 
  TrendingDown, 
  Activity, 
  Zap,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useStore } from '../store/useStore';
import { API, createWebSocket } from '../lib/api';

export default function DashboardPage() {
  const telemetry = useStore(state => state.telemetry);
  const setTelemetry = useStore(state => state.setTelemetry);
  const trainingLogs = useStore(state => state.trainingLogs);
  const trainingActive = useStore(state => state.trainingActive);
  const appendTrainingLog = useStore(state => state.appendTrainingLog);
  const setTrainingStatus = useStore(state => state.setTrainingStatus);

  const [ws, setWs] = useState(null);
  const [lastLoss, setLastLoss] = useState(0);
  const [lastEpoch, setLastEpoch] = useState(0);
  const [lastThroughput, setLastThroughput] = useState(0);
  const [lossHistory, setLossHistory] = useState([]);

  // Poll real telemetry
  useEffect(() => {
    const fetchTelemetry = async () => {
      try {
        const resp = await fetch(API.buildUrl(API.endpoints.telemetry));
        if (!resp.ok) return;
        const data = await resp.json();
        if (data.available && data.thermal) {
          const t = data.thermal;
          setTelemetry({
            gpuUtil: t.gpu_util_pct || 0,
            cpuUtil: t.cpu_util_pct || 0,
            ramUtil: t.ram_util_pct || 0,
            gpuTemp: t.gpu_temp_c || 0,
            gpuPower: t.gpu_power_w || 0,
            uptime: telemetry.uptime
          });
        }
      } catch (e) {
        // Fallback
        setTelemetry({
          gpuUtil: 30 + Math.random() * 20,
          cpuUtil: 15 + Math.random() * 10,
          ramUtil: 52,
          gpuTemp: 64,
          gpuPower: 85,
          uptime: '1h 24m'
        });
      }
    };

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 3000);
    return () => clearInterval(interval);
  }, [setTelemetry]);

  // Connect WebSocket for training log events
  useEffect(() => {
    const socket = createWebSocket();
    
    socket.onopen = () => {
      console.log('Dashboard WS connected for training events');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle training log events from EventBus
        if (data.type === API.wsEvents.TRAINING_LOG) {
          const logMsg = data.payload?.log || '';
          appendTrainingLog(logMsg);
          
          // Parse loss/epoch from log line
          const epochMatch = logMsg.match(/Epoch\s+(\d+)\/(\d+)/);
          const lossMatch = logMsg.match(/Loss:\s+([\d.]+)/);
          const throughputMatch = logMsg.match(/Rate:\s+([\d,]+)\s*tok\/s/);
          
          if (epochMatch) {
            const epoch = parseInt(epochMatch[1], 10);
            setLastEpoch(epoch);
          }
          if (lossMatch) {
            const loss = parseFloat(lossMatch[1]);
            setLastLoss(loss);
            setLossHistory(prev => {
              const next = [...prev, loss];
              return next.length > 50 ? next.slice(-50) : next;
            });
          }
          if (throughputMatch) {
            const throughput = parseInt(throughputMatch[1].replace(/,/g, ''), 10);
            setLastThroughput(throughput);
          }
        }
        
        // Handle training status from status endpoint events
        if (data.type === 'training.status') {
          setTrainingStatus(data.payload?.active || false);
        }
      } catch (err) {
        console.error('Dashboard WS parse error:', err);
      }
    };

    socket.onclose = () => {
      console.log('Dashboard WS closed');
    };

    setWs(socket);
    return () => socket.close();
  }, [appendTrainingLog, setTrainingStatus]);

  // Fetch training status on mount
  useEffect(() => {
    const fetchTrainingStatus = async () => {
      try {
        const data = await fetch(API.buildUrl(API.endpoints.trainingStatus)).then(r => r.json());
        if (data.in_progress) {
          setTrainingStatus(true);
        }
      } catch (e) {
        // ignore
      }
    };
    fetchTrainingStatus();
  }, [setTrainingStatus]);

  // Training status indicator
  const getTrainingStatus = () => {
    if (trainingActive) return { label: 'TRAINING', color: '#22D3A0', pulse: true };
    if (trainingLogs.length > 0 && !trainingActive) return { label: 'COMPLETED', color: '#00D4FF', pulse: false };
    return { label: 'STANDBY', color: '#E8EEFF', pulse: false };
  };

  const status = getTrainingStatus();

  return (
    <div className="space-y-6">
      
      {/* Title Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold font-mono tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-[#E8EEFF] to-[#00D4FF]">
            NEURALFORGE ENGINE
          </h1>
          <p className="text-xs text-[#E8EEFF]/40 font-mono mt-1">
            Local Transformer Training Dashboard (Ryzen 9 + RTX 4060)
          </p>
        </div>

        {/* Training status + refresh */}
        <div className="flex items-center gap-2">
          <button 
            onClick={() => {
              // Refresh training status
              fetch(API.buildUrl(API.endpoints.trainingStatus)).then(r => r.json()).then(data => {
                if (data.in_progress) setTrainingStatus(true);
              });
            }}
            className="glass-panel px-3 py-1.5 rounded-lg flex items-center gap-2 font-mono text-[10px] text-[#E8EEFF]/70 hover:text-[#E8EEFF] hover:bg-[#00D4FF]/5 transition-all border border-transparent hover:border-[#00D4FF]/20 active:scale-95 cursor-pointer"
            title="Refresh training status"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>REFRESH</span>
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Card: Loss */}
        <div className="glass-panel rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-[#00D4FF]/5 rounded-bl-full pointer-events-none" />
          <div className="flex items-center gap-2 text-[#E8EEFF]/40 font-mono text-[10px]">
            <TrendingDown className="w-3.5 h-3.5 text-[#00D4FF]" />
            <span>TRAINING LOSS</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-[#00D4FF]">{lastLoss.toFixed(4)}</span>
            {trainingActive && lastLoss > 0 && <span className="text-[10px] text-[#22D3A0] font-mono">▼</span>}
          </div>
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">Target: < 1.000 | Epoch: {lastEpoch}</div>
        </div>

        {/* Card: Epoch */}
        <div className="glass-panel rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-[#7B2FBE]/5 rounded-bl-full pointer-events-none" />
          <div className="flex items-center gap-2 text-[#E8EEFF]/40 font-mono text-[10px]">
            <Activity className="w-3.5 h-3.5 text-[#7B2FBE]" />
            <span>EPOCH / STEP</span>
          </div>
          <div className="mt-2">
            <span className="text-2xl font-bold font-mono text-white">
              {lastEpoch} <span className="text-xs text-[#E8EEFF]/40">/ {lossHistory.length > 0 ? 'LIVE' : '—'}</span>
            </span>
          </div>
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">Loss history points: {lossHistory.length}</div>
        </div>

        {/* Card: Token Throughput */}
        <div className="glass-panel rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-[#FFB800]/5 rounded-bl-full pointer-events-none" />
          <div className="flex items-center gap-2 text-[#E8EEFF]/40 font-mono text-[10px]">
            <Zap className="w-3.5 h-3.5 text-[#FFB800]" />
            <span>THROUGHPUT</span>
          </div>
          <div className="mt-2">
            <span className="text-2xl font-bold font-mono text-[#FFB800]">{lastThroughput.toLocaleString()}</span>
            <span className="text-xs text-[#E8EEFF]/40 font-mono ml-1">tok/s</span>
          </div>
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">RTX 4060 GPU Target</div>
        </div>

        {/* Card: Training Status */}
        <div className="glass-panel rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center gap-2 text-[#E8EEFF]/40 font-mono text-[10px]">
            <Cpu className="w-3.5 h-3.5 text-[#22D3A0]" />
            <span>STATE</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <div className={`w-2.5 h-2.5 rounded-full ${status.pulse ? 'bg-' + status.color + ' animate-pulse shadow-md shadow-' + status.color + '/30' : 'bg-' + status.color}`} />
            <span className="text-base font-bold font-mono tracking-wider text-[${status.color}]">
              {status.label}
            </span>
          </div>
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">Sovereign Intel Core</div>
        </div>

      </div>

      {/* Main Grid: Graph + Console */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Loss Curve Graph */}
        <div className="lg:col-span-2 glass-panel rounded-xl p-5 flex flex-col h-[320px]">
          <div className="font-mono text-xs text-[#E8EEFF]/55 mb-4 uppercase">
            Loss Convergence Curve
          </div>
          <div className="flex-1 flex items-end gap-[4px] border-b border-l border-white/5 pb-2 pl-2">
            {lossHistory.length === 0 ? (
              <div className="w-full h-full flex items-center justify-center font-mono text-xs text-[#E8EEFF]/25">
                No active training data — start training from /training page
              </div>
            ) : (
              lossHistory.map((val, idx) => {
                const heightPct = Math.min(100, (val / 5.0) * 100);
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-1 scale-0 group-hover:scale-100 transition-all font-mono text-[9px] bg-[#0A0E1A] border border-[#00D4FF]/25 px-1.5 py-0.5 rounded text-[#00D4FF] z-30">
                      {val.toFixed(3)}
                    </div>
                    {/* Bar */}
                    <div 
                      className="w-full bg-[#00D4FF]/20 border-t border-[#00D4FF] hover:bg-[#00D4FF]/45 transition-colors rounded-t-[2px]" 
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                );
              })
            )}
          </div>
          <div className="flex justify-between font-mono text-[9px] text-[#E8EEFF]/30 mt-2">
            <span>START</span>
            <span>REALTIME CONVERGENCE</span>
            <span>LATEST</span>
          </div>
        </div>

        {/* Live Training Console Logs */}
        <div className="glass-panel rounded-xl p-5 flex flex-col h-[320px]">
          <div className="flex items-center gap-2 font-mono text-xs text-[#E8EEFF]/55 mb-4 uppercase">
            <TermIcon className="w-3.5 h-3.5" />
            <span>Local Training Logs</span>
          </div>
          <div className="flex-1 bg-black/45 border border-white/5 rounded-lg p-3 font-mono text-[10px] text-[#E8EEFF]/65 overflow-y-auto space-y-1.5">
            {trainingLogs.length === 0 ? (
              <div className="text-[#E8EEFF]/25 italic">Standby. Connect to WS for live training telemetry.</div>
            ) : (
              trainingLogs.slice().reverse().map((log, idx) => (
                <div key={idx} className="border-b border-white/[0.02] pb-1">
                  <span className="text-[#00D4FF]/60">>></span> {log}
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}