'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Square, 
  Terminal, 
  Loader2, 
  AlertCircle, 
  CheckCircle,
  Settings,
  HelpCircle,
  TrendingDown,
  Zap,
  Activity
} from 'lucide-react';
import { useStore } from '../../store/useStore';
import { API, createWebSocket, apiPost } from '../../lib/api';

export default function TrainingPage() {
  const trainingActive = useStore(state => state.trainingActive);
  const trainingLogs = useStore(state => state.trainingLogs);
  const appendTrainingLog = useStore(state => state.appendTrainingLog);
  const setTrainingStatus = useStore(state => state.setTrainingStatus);
  const clearTrainingLogs = useStore(state => state.clearTrainingLogs);

  // Training config state
  const [config, setConfig] = useState({
    epochs: 60,
    batch_size: 8,
    lr: '3e-4',
    hidden_size: 512,
    num_layers: 12,
    num_heads: 8,
    vocab_size: 8000,
    max_len: 512,
    device: 'auto',
  });

  const [starting, setStarting] = useState(false);
  const [lastLoss, setLastLoss] = useState(0);
  const [lastEpoch, setLastEpoch] = useState(0);
  const [lastThroughput, setLastThroughput] = useState(0);
  const [lossHistory, setLossHistory] = useState([]);
  const [ws, setWs] = useState(null);
  const logEndRef = useRef(null);

  // Connect WebSocket for training log events
  useEffect(() => {
    const socket = createWebSocket();
    
    socket.onopen = () => {
      console.log('Training page WS connected');
      appendTrainingLog('[WS] Connected to Vibhu-Oska gateway');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle training log events from EventBus
        if (data.type === API.wsEvents.TRAINING_LOG) {
          const logMsg = data.payload?.log || '';
          appendTrainingLog(logMsg);
          
          // Parse metrics from log line
          const epochMatch = logMsg.match(/Epoch\s+(\d+)\/(\d+)/);
          const lossMatch = logMsg.match(/Loss:\s+([\d.]+)/);
          const throughputMatch = logMsg.match(/Rate:\s+([\d,]+)\s*tok\/s/);
          
          if (epochMatch) {
            setLastEpoch(parseInt(epochMatch[1], 10));
          }
          if (lossMatch) {
            const loss = parseFloat(lossMatch[1]);
            setLastLoss(loss);
            setLossHistory(prev => {
              const next = [...prev, loss];
              return next.length > 100 ? next.slice(-100) : next;
            });
          }
          if (throughputMatch) {
            setLastThroughput(parseInt(throughputMatch[1].replace(/,/g, ''), 10));
          }
        }
      } catch (err) {
        console.error('Training page WS parse error:', err);
      }
    };

    socket.onclose = () => {
      appendTrainingLog('[WS] Disconnected from gateway');
    };

    setWs(socket);
    return () => socket.close();
  }, [appendTrainingLog]);

  // Scroll to bottom of logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [trainingLogs]);

  const handleConfigChange = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const handleStartTraining = async () => {
    if (trainingActive) return;
    setStarting(true);
    clearTrainingLogs();
    appendTrainingLog('[UI] Starting training with config: ' + JSON.stringify(config));
    
    try {
      const response = await apiPost(API.endpoints.modelTrain, config);
      appendTrainingLog('[API] ' + (response.message || 'Training started'));
      appendTrainingLog('[API] Status: ' + response.status);
      setTrainingStatus(true);
    } catch (err) {
      appendTrainingLog('[ERROR] Failed to start training: ' + err.message);
      setTrainingStatus(false);
    } finally {
      setStarting(false);
    }
  };

  const handleStopTraining = () => {
    // Note: No stop endpoint exists yet; this just updates local state
    appendTrainingLog('[UI] Stop requested (local only — server training continues)');
    setTrainingStatus(false);
  };

  const handleClearLogs = () => {
    clearTrainingLogs();
    setLossHistory([]);
    setLastLoss(0);
    setLastEpoch(0);
    setLastThroughput(0);
  };

  return (
    <div className="space-y-6">
      
      {/* Title Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold font-mono tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-[#E8EEFF] to-[#00D4FF]">
            SOVEREIGN GPT TRAINING
          </h1>
          <p className="text-xs text-[#E8EEFF]/40 font-mono mt-1">
            Configure and launch local transformer training from scratch
          </p>
        </div>

        {/* Control buttons */}
        <div className="flex gap-2">
          {!trainingActive && !starting ? (
            <button 
              onClick={handleStartTraining}
              disabled={starting}
              className="px-4 py-2 bg-[#00D4FF] hover:bg-[#00D4FF]/90 text-black font-mono font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow-md shadow-[#00D4FF]/10 active:scale-95 disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              {starting ? 'STARTING...' : 'START TRAINING'}
            </button>
          ) : (
            <button 
              onClick={handleStopTraining}
              className="px-4 py-2 bg-[#FF4444] hover:bg-[#FF4444]/90 text-white font-mono font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow-md shadow-[#FF4444]/10 active:scale-95"
            >
              <Square className="w-3.5 h-3.5 fill-white" />
              STOP (LOCAL)
            </button>
          )}
          <button 
            onClick={handleClearLogs}
            className="glass-panel px-3 py-2 rounded-lg flex items-center gap-2 font-mono text-[10px] text-[#E8EEFF]/70 hover:text-[#E8EEFF] hover:bg-[#00D4FF]/5 transition-all border border-transparent hover:border-[#00D4FF]/20 active:scale-95 cursor-pointer"
          >
            <Terminal className="w-3.5 h-3.5" />
            CLEAR LOGS
          </button>
        </div>
      </div>

      {/* Config Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Epochs */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Epochs</label>
          <input
            type="number"
            min="1"
            max="500"
            value={config.epochs}
            onChange={(e) => handleConfigChange('epochs', parseInt(e.target.value) || 1)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

        {/* Batch Size */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Batch Size</label>
          <input
            type="number"
            min="1"
            max="64"
            value={config.batch_size}
            onChange={(e) => handleConfigChange('batch_size', parseInt(e.target.value) || 1)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

        {/* Learning Rate */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Learning Rate</label>
          <input
            type="text"
            value={config.lr}
            onChange={(e) => handleConfigChange('lr', e.target.value)}
            placeholder="3e-4"
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

        {/* Device */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Device</label>
          <select
            value={config.device}
            onChange={(e) => handleConfigChange('device', e.target.value)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          >
            <option value="auto">Auto (CUDA if available)</option>
            <option value="cuda">CUDA</option>
            <option value="cpu">CPU</option>
          </select>
        </div>

        {/* Hidden Size */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Hidden Size</label>
          <input
            type="number"
            min="64"
            max="2048"
            step="64"
            value={config.hidden_size}
            onChange={(e) => handleConfigChange('hidden_size', parseInt(e.target.value) || 64)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

        {/* Layers */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Layers</label>
          <input
            type="number"
            min="1"
            max="48"
            value={config.num_layers}
            onChange={(e) => handleConfigChange('num_layers', parseInt(e.target.value) || 1)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

        {/* Attention Heads */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Attention Heads</label>
          <input
            type="number"
            min="1"
            max="32"
            value={config.num_heads}
            onChange={(e) => handleConfigChange('num_heads', parseInt(e.target.value) || 1)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

        {/* Vocab Size */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Vocab Size</label>
          <input
            type="number"
            min="500"
            max="50000"
            step="500"
            value={config.vocab_size}
            onChange={(e) => handleConfigChange('vocab_size', parseInt(e.target.value) || 500)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

        {/* Max Sequence Length */}
        <div className="glass-panel rounded-xl p-4">
          <label className="block text-[10px] text-[#E8EEFF]/40 font-mono uppercase mb-1">Max Seq Len</label>
          <input
            type="number"
            min="64"
            max="4096"
            step="64"
            value={config.max_len}
            onChange={(e) => handleConfigChange('max_len', parseInt(e.target.value) || 64)}
            className="w-full bg-[#060912] border border-[#00D4FF]/10 focus:border-[#00D4FF]/40 rounded-lg p-2 text-white font-mono text-sm outline-none"
          />
        </div>

      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Card: Current Loss */}
        <div className="glass-panel rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-[#00D4FF]/5 rounded-bl-full pointer-events-none" />
          <div className="flex items-center gap-2 text-[#E8EEFF]/40 font-mono text-[10px]">
            <TrendingDown className="w-3.5 h-3.5 text-[#00D4FF]" />
            <span>CURRENT LOSS</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-[#00D4FF]">{lastLoss.toFixed(4)}</span>
            {trainingActive && lastLoss > 0 && <span className="text-[10px] text-[#22D3A0] font-mono">▼</span>}
          </div>
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">Target: < 1.000</div>
        </div>

        {/* Card: Current Epoch */}
        <div className="glass-panel rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-[#7B2FBE]/5 rounded-bl-full pointer-events-none" />
          <div className="flex items-center gap-2 text-[#E8EEFF]/40 font-mono text-[10px]">
            <Activity className="w-3.5 h-3.5 text-[#7B2FBE]" />
            <span>EPOCH</span>
          </div>
          <div className="mt-2">
            <span className="text-2xl font-bold font-mono text-white">{lastEpoch}</span>
          </div>
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">History points: {lossHistory.length}</div>
        </div>

        {/* Card: Throughput */}
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
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">Tokens per second</div>
        </div>

        {/* Card: Status */}
        <div className="glass-panel rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center gap-2 text-[#E8EEFF]/40 font-mono text-[10px]">
            <Settings className="w-3.5 h-3.5 text-[#22D3A0]" />
            <span>STATE</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <div className={`w-2.5 h-2.5 rounded-full ${trainingActive ? 'bg-[#22D3A0] animate-pulse shadow-md shadow-[#22D3A0]/30' : 'bg-[#E8EEFF]/20'}`} />
            <span className="text-base font-bold font-mono tracking-wider">
              {trainingActive ? 'TRAINING' : 'IDLE'}
            </span>
          </div>
          <div className="text-[9px] font-mono text-[#E8EEFF]/30 mt-2">Sovereign GPT Pipeline</div>
        </div>

      </div>

      {/* Main Grid: Graph + Console */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Loss Curve Graph */}
        <div className="lg:col-span-2 glass-panel rounded-xl p-5 flex flex-col h-[400px]">
          <div className="font-mono text-xs text-[#E8EEFF]/55 mb-4 uppercase">
            Loss Convergence Curve (Live)
          </div>
          <div className="flex-1 flex items-end gap-[4px] border-b border-l border-white/5 pb-2 pl-2">
            {lossHistory.length === 0 ? (
              <div className="w-full h-full flex items-center justify-center font-mono text-xs text-[#E8EEFF]/25">
                No training data yet — click START TRAINING to begin
              </div>
            ) : (
              lossHistory.map((val, idx) => {
                const heightPct = Math.min(100, (val / 5.0) * 100);
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                    <div className="absolute bottom-full mb-1 scale-0 group-hover:scale-100 transition-all font-mono text-[9px] bg-[#0A0E1A] border border-[#00D4FF]/25 px-1.5 py-0.5 rounded text-[#00D4FF] z-30">
                      {val.toFixed(3)}
                    </div>
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
            <span>EPOCH 1</span>
            <span>REALTIME CONVERGENCE</span>
            <span>LATEST</span>
          </div>
        </div>

        {/* Live Training Console Logs */}
        <div className="glass-panel rounded-xl p-5 flex flex-col h-[400px]">
          <div className="flex items-center gap-2 font-mono text-xs text-[#E8EEFF]/55 mb-4 uppercase">
            <Terminal className="w-3.5 h-3.5" />
            <span>Training Console</span>
          </div>
          <div className="flex-1 bg-black/45 border border-white/5 rounded-lg p-3 font-mono text-[10px] text-[#E8EEFF]/65 overflow-y-auto space-y-1.5">
            {trainingLogs.length === 0 ? (
              <div className="text-[#E8EEFF]/25 italic">Ready. Configure training above and click START.</div>
            ) : (
              trainingLogs.slice().reverse().map((log, idx) => (
                <div key={idx} className="border-b border-white/[0.02] pb-1">
                  <span className="text-[#00D4FF]/60">>></span> {log}
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
        </div>

      </div>

    </div>
  );
}