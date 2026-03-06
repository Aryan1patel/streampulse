'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect, useMemo } from 'react';
import Loader from '@/components/Loader';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';

interface DeepDiveData {
  symbol: string;
  current_price: number;
  prediction: {
    direction: string;
    expected_change_percent: number;
    confidence: number;
    range: number[] | { low: number; high: number };
    timeframe: string;
    model_predictions: {
      [key: string]: number;
    };
    comparison_predictions?: {
      lstm: number[];
      gru: number[];
    };
    historical_pattern?: {
      similar_events: number;
      success_rate: number | string;
    };
  };
  analysis: {
    event_type: string;
    sentiment: any;
    severity: string;
  };
  fundamentals?: {
    pe_ratio: string | number;
    market_cap: string | number;
    sector: string;
    '52_week_high': string | number;
    '52_week_low': string | number;
    volume?: string | number;
  };
  price_history?: { date: string, price: number }[];
}

export default function DeepDivePage() {
  const params = useParams();
  const router = useRouter();
  const symbol = params.symbol as string;

  const [loading, setLoading] = useState(true);
  const [loadingStep, setLoadingStep] = useState(0);
  const [deepDiveData, setDeepDiveData] = useState<DeepDiveData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [chartScale, setChartScale] = useState(30);
  const [showEnsembleInfo, setShowEnsembleInfo] = useState(false);
  const [exporting, setExporting] = useState(false);

  const LOADING_STEPS = [
    { icon: '📰', label: 'Fetching news sentiment', detail: `Analyzing headline context for ${symbol}` },
    { icon: '📈', label: 'Pulling historical price data', detail: 'Querying Finance API for 60-day OHLCV data' },
    { icon: '💼', label: 'Loading company fundamentals', detail: 'P/E ratio, market cap, 52-week range, sector' },
    { icon: '🔍', label: 'Searching similar past events', detail: 'Querying Qdrant vector DB for historical patterns' },
    { icon: '🤖', label: 'Running ML ensemble', detail: 'LightGBM · GARCH · Prophet · LSTM · GRU models' },
    { icon: '📊', label: 'Computing final prediction', detail: 'Weighted ensemble aggregation + confidence scoring' },
  ];

  const exportPDF = async () => {
    if (!deepDiveData) return;
    setExporting(true);
    try {
      const { default: jsPDF } = await import('jspdf');
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
      const W = pdf.internal.pageSize.getWidth();
      const H = pdf.internal.pageSize.getHeight();
      const margin = 15;
      let y = margin;

      const write = (text: string, size = 10, bold = false) => {
        if (y + 8 > H - margin) { pdf.addPage(); y = margin; }
        pdf.setFontSize(size);
        pdf.setFont('helvetica', bold ? 'bold' : 'normal');
        pdf.setTextColor(0, 0, 0);
        const lines = pdf.splitTextToSize(text, W - margin * 2) as string[];
        pdf.text(lines, margin, y);
        y += lines.length * (size * 0.4) + 2;
      };

      const sep = () => {
        if (y + 5 > H - margin) { pdf.addPage(); y = margin; }
        pdf.setDrawColor(180, 180, 180);
        pdf.line(margin, y, W - margin, y);
        y += 5;
      };

      const pred = deepDiveData.prediction;
      const fund = deepDiveData.fundamentals;
      const analysis = deepDiveData.analysis;
      const ts = new Date().toLocaleString('en-IN', { dateStyle: 'long', timeStyle: 'short' });

      // Header
      write('StreamPulse - Deep Dive Report', 18, true);
      y += 2;
      write(`Symbol: ${deepDiveData.symbol}`, 11, true);
      write(`Generated: ${ts}`, 9);
      sep();

      // Prediction Summary
      write('ML PREDICTION SUMMARY', 12, true);
      y += 1;
      write(`Direction:          ${pred.direction}`);
      write(`Confidence:         ${pred.confidence}%`);
      write(`Expected Move:      +/- ${pred.expected_change_percent.toFixed(2)}%`);
      write(`Timeframe:          ${pred.timeframe}`);
      write(`Current Price:      Rs. ${deepDiveData.current_price}`);
      if (Array.isArray(pred.range)) {
        const lo = (deepDiveData.current_price * (1 + pred.range[0] / 100)).toFixed(2);
        const hi = (deepDiveData.current_price * (1 + pred.range[1] / 100)).toFixed(2);
        write(`3-Day Price Range:  Rs. ${lo} to Rs. ${hi}`);
      }
      if (pred.confidence < 60) {
        y += 1;
        write('NOTE: Low Conviction - Models disagree. Treat this prediction with caution.', 9);
      }
      sep();

      // Model Breakdown
      write('ENSEMBLE MODEL BREAKDOWN', 12, true);
      y += 1;
      const weights: Record<string, string> = {
        lightgbm: 'High (4/4)',
        qdrant: 'Medium-High (3/4)',
        garch: 'Medium (2/4)',
        prophet: 'Low (1/4)',
      };
      Object.entries(pred.model_predictions).forEach(([model, val]) => {
        const v = Number(val);
        write(`  ${model.toUpperCase().padEnd(12)}   ${v >= 0 ? '+' : ''}${v.toFixed(2)}%     Weight: ${weights[model] ?? '-'}`);
      });
      if (pred.comparison_predictions) {
        y += 2;
        write('Deep Learning Models (comparison only):', 9, true);
        const lstm = pred.comparison_predictions.lstm;
        const gru = pred.comparison_predictions.gru;
        if (Array.isArray(lstm)) write(`  LSTM   Day1: ${lstm[0]?.toFixed(2) ?? '-'}%   Day2: ${lstm[1]?.toFixed(2) ?? '-'}%   Day3: ${lstm[2]?.toFixed(2) ?? '-'}%`);
        if (Array.isArray(gru)) write(`  GRU    Day1: ${gru[0]?.toFixed(2) ?? '-'}%   Day2: ${gru[1]?.toFixed(2) ?? '-'}%   Day3: ${gru[2]?.toFixed(2) ?? '-'}%`);
      }
      sep();

      // Analysis Context
      write('ANALYSIS CONTEXT', 12, true);
      y += 1;
      const sentLabel = typeof analysis.sentiment === 'string'
        ? analysis.sentiment
        : `${analysis.sentiment?.label || 'Neutral'} (${((analysis.sentiment?.score || 0) * 100).toFixed(0)}%)`;
      write(`Event Type:   ${analysis.event_type || 'Unknown'}`);
      write(`Sentiment:    ${sentLabel}`);
      write(`Severity:     ${analysis.severity || 'Medium'}`);
      sep();

      // Historical Pattern
      if (pred.historical_pattern) {
        write('HISTORICAL PATTERN', 12, true);
        y += 1;
        write(`Similar Events:  ${pred.historical_pattern.similar_events}`);
        const sr = pred.historical_pattern.success_rate;
        write(`Success Rate:    ${typeof sr === 'string' ? sr : `${(Number(sr) * 100).toFixed(0)}%`}`);
        sep();
      }

      // Company Fundamentals
      if (fund) {
        write('COMPANY FUNDAMENTALS', 12, true);
        y += 1;
        write(`P/E Ratio:    ${fund.pe_ratio || 'N/A'}`);
        write(`Market Cap:   ${fund.market_cap || 'N/A'}`);
        write(`Sector:       ${fund.sector || 'N/A'}`);
        write(`52W High:     Rs. ${fund['52_week_high'] || 'N/A'}`);
        write(`52W Low:      Rs. ${fund['52_week_low'] || 'N/A'}`);
        write(`Volume:       ${fund.volume || 'N/A'}`);
        sep();
      }

      // Footer
      write('For informational purposes only. Not financial advice.', 8);
      write('Generated by StreamPulse AI', 8);

      pdf.save(`StreamPulse_${deepDiveData.symbol}_${new Date().toISOString().slice(0, 10)}.pdf`);
    } catch (e) {
      console.error('PDF export failed:', e);
    } finally {
      setExporting(false);
    }
  };

  const [visibleModels, setVisibleModels] = useState<Record<string, boolean>>({
    ensemble: true,
    lstm: true,
    gru: true,
    lightgbm: false,
    garch: false,
    prophet: false,
    qdrant: false
  });

  const chartData = useMemo(() => {
    if (!deepDiveData?.price_history) return [];

    // Slice history based on selected scale
    const slicedHistory = deepDiveData.price_history.slice(-chartScale);

    // Base data (historical)
    const baseData = slicedHistory.map(p => ({
      name: p.date,
      price: p.price,
      actual: p.price
    }));

    // Add 3-day prediction projection
    const lastPrice = baseData[baseData.length - 1].price;
    const futureTags = ['+1D', '+2D', '+3D'];

    const futureData = futureTags.map((tag, i) => {
      const step = (i + 1) / 3;
      const point: any = { name: tag };

      // Ensemble Prediction
      const ensembleMove = (deepDiveData.prediction.expected_change_percent / 100) * (deepDiveData.prediction.direction === 'UP' ? 1 : -1);
      point.ensemble = lastPrice * (1 + ensembleMove * step);

      // Comparison Models (Recursive Trajectories)
      if (deepDiveData.prediction.comparison_predictions) {
        const { lstm, gru } = deepDiveData.prediction.comparison_predictions;

        if (Array.isArray(lstm)) {
          // Use the specific cumulative prediction for this day
          point.lstm = lastPrice * (1 + (lstm[i] ?? lstm[lstm.length - 1]) / 100);
        } else if (typeof lstm === 'number') {
          point.lstm = lastPrice * (1 + (lstm / 100) * step);
        }

        if (Array.isArray(gru)) {
          point.gru = lastPrice * (1 + (gru[i] ?? gru[gru.length - 1]) / 100);
        } else if (typeof gru === 'number') {
          point.gru = lastPrice * (1 + (gru / 100) * step);
        }
      }

      // Individual Models
      Object.entries(deepDiveData.prediction.model_predictions).forEach(([model, move]) => {
        point[model] = lastPrice * (1 + (Number(move) / 100) * step);
      });

      return point;
    });

    return [...baseData, ...futureData];
  }, [deepDiveData, chartScale]);

  useEffect(() => {
    fetchDeepDive();
  }, [symbol]);

  // Advance the loading step indicator while fetch is in progress
  useEffect(() => {
    if (!loading) return;
    if (loadingStep >= LOADING_STEPS.length - 1) return;
    const timer = setTimeout(() => {
      setLoadingStep(prev => Math.min(prev + 1, LOADING_STEPS.length - 1));
    }, 2200);
    return () => clearTimeout(timer);
  }, [loading, loadingStep]);

  const fetchDeepDive = async () => {
    try {
      setLoading(true);
      setLoadingStep(0);
      setError(null);

      console.log('Fetching deep dive for:', symbol);

      // Call deep dive ML service
      const response = await fetch(
        `http://localhost:7004/deep-dive?symbol=${encodeURIComponent(symbol)}&headline=Stock%20Analysis&event_type=analysis&sentiment_label=neutral&sentiment_score=0.5&severity=medium`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch deep dive: ${response.statusText}`);
      }

      const data = await response.json();
      setDeepDiveData(data);
      console.log('Deep dive data:', data);
    } catch (err: any) {
      console.error('Deep dive error:', err);
      setError(err.message || 'Failed to load deep dive analysis');
    } finally {
      setLoading(false);
    }
  };


  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-[#6e72d5] via-[#7b5fd4] to-[#9061e0]">
        <div className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
            <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-500 hover:text-gray-800 font-semibold text-sm transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
              Back
            </button>
            <div className="flex items-center gap-2 text-xs font-bold text-gray-400 tracking-widest uppercase">
              <div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
              Running AI Pipeline
            </div>
            <div className="text-sm font-bold text-gray-700 bg-purple-50 border border-purple-100 px-3 py-1.5 rounded-full">{symbol}</div>
          </div>
        </div>
        <div className="max-w-2xl mx-auto px-6 py-12">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4 shadow-md" style={{ background: 'linear-gradient(135deg, #7c3aed, #2563eb)' }}>
                <span className="text-2xl">⚡</span>
              </div>
              <h2 className="text-xl font-extrabold text-gray-900">Deep Dive Analysis</h2>
              <p className="text-gray-500 text-sm mt-1">Running AI pipeline for <span className="font-bold text-[#6d5bda]">{symbol}</span></p>
            </div>
            <div className="space-y-2">
              {LOADING_STEPS.map((step, i) => {
                const isDone = i < loadingStep;
                const isActive = i === loadingStep;
                return (
                  <div key={i} className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-all duration-500 ${isActive ? 'bg-purple-50 border border-purple-200' : isDone ? 'bg-gray-50' : 'opacity-40'
                    }`}>
                    <div className="shrink-0 w-7 h-7 flex items-center justify-center">
                      {isDone ? <span className="text-base">✅</span> : isActive ? (
                        <svg className="animate-spin w-5 h-5 text-purple-500" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                        </svg>
                      ) : <span className="text-base">{step.icon}</span>}
                    </div>
                    <div className="flex-1">
                      <p className={`text-sm font-semibold ${isActive ? 'text-purple-800' : isDone ? 'text-gray-700' : 'text-gray-400'}`}>{step.label}</p>
                      {(isActive || isDone) && <p className={`text-xs mt-0.5 ${isActive ? 'text-purple-500' : 'text-gray-400'}`}>{step.detail}</p>}
                    </div>
                    {isDone && <span className="text-[10px] text-green-600 font-bold bg-green-50 px-2 py-0.5 rounded-full border border-green-200">done</span>}
                    {isActive && <span className="text-[10px] text-purple-600 font-bold bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200 animate-pulse">running</span>}
                  </div>
                );
              })}
            </div>
            <div className="mt-6">
              <div className="flex justify-between text-xs text-gray-400 font-medium mb-1.5">
                <span>Progress</span>
                <span>{Math.round((loadingStep / LOADING_STEPS.length) * 100)}%</span>
              </div>
              <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-700" style={{ width: `${(loadingStep / LOADING_STEPS.length) * 100}%`, background: 'linear-gradient(90deg, #7c3aed, #2563eb)' }} />
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (error || !deepDiveData) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-[#6e72d5] via-[#7b5fd4] to-[#9061e0]">
        <div className="bg-white border-b border-gray-100 shadow-sm">
          <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center">
            <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-500 hover:text-gray-800 font-semibold text-sm transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
              Back
            </button>
          </div>
        </div>
        <div className="max-w-2xl mx-auto px-6 py-12">
          <div className="bg-white rounded-2xl p-6 border border-red-100 shadow-sm">
            <p className="font-semibold text-red-600">⚠️ {error || 'Failed to load analysis'}</p>
            <button onClick={() => router.back()} className="mt-4 text-sm text-[#6d5bda] font-semibold hover:underline">← Go back</button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#6e72d5] via-[#7b5fd4] to-[#9061e0]">
      {/* Top Nav */}
      <div className="bg-white border-b border-purple-100 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
          <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-500 hover:text-gray-800 font-semibold text-sm transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            Back
          </button>
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-bold tracking-widest uppercase text-gray-400">StreamPulse</span>
            <span className="text-gray-300">/</span>
            <span className="text-xs font-bold text-white bg-[#6d5bda] px-3 py-1 rounded-full shadow-sm">Deep Dive</span>
            <span className="text-gray-300">/</span>
            <span className="text-[10px] font-bold tracking-widest uppercase text-gray-500">{deepDiveData.symbol}</span>
            <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.8)] animate-pulse ml-1" />
          </div>
          <button
            onClick={exportPDF}
            disabled={exporting}
            className="flex items-center gap-1.5 text-sm font-semibold text-white bg-[#6d5bda] hover:bg-[#7c68e8] px-4 py-2 rounded-full transition-colors shadow-md disabled:opacity-60"
          >
            {exporting ? 'Exporting...' : '↓ Export PDF'}
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Hero row */}
        <div className="bg-white rounded-2xl p-7 shadow-sm border border-gray-100 mb-6">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold tracking-wider uppercase text-gray-400 bg-gray-50 border border-gray-100 px-2.5 py-1 rounded-full">Deep Dive Analysis</span>
                <span className="text-[10px] text-gray-400">AI-Powered</span>
              </div>
              <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-[#6d5bda] via-[#8b5cf6] to-[#3b82f6] bg-clip-text text-transparent drop-shadow-sm"
                style={{ filter: 'drop-shadow(0 0 20px rgba(109,91,218,0.3))' }}>
                {deepDiveData.symbol}
              </h1>
              <p className="text-gray-500 mt-1.5 text-sm">Current Price: <span className="font-bold text-gray-800 text-base">₹{deepDiveData.current_price}</span></p>
            </div>
            <div className={`flex items-center gap-2 px-6 py-3 rounded-2xl text-white font-extrabold text-xl shadow-lg ${deepDiveData.prediction.direction === 'UP' ? 'bg-green-500' :
              deepDiveData.prediction.direction === 'DOWN' ? 'bg-red-500' : 'bg-gray-400'
              }`}>
              {deepDiveData.prediction.direction === 'UP' ? '📈 UP' : deepDiveData.prediction.direction === 'DOWN' ? '📉 DOWN' : '➡️ NEUTRAL'}
            </div>
          </div>
        </div>

        {/* Low confidence warning */}
        {deepDiveData.prediction.confidence < 60 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl px-5 py-3 mb-6 flex items-center gap-3 shadow-sm">
            <span className="text-lg">⚠️</span>
            <p className="text-sm text-amber-800 font-semibold">
              Low Conviction: Models show disagreement (Confidence: {deepDiveData.prediction.confidence}%). Consider waiting for stronger signals.
            </p>
          </div>
        )}

        {/* Stat cards row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {/* Expected Move */}
          <div className="rounded-2xl p-5 shadow-md hover:shadow-xl transition-all hover:-translate-y-0.5 border-l-4 border-l-blue-400"
            style={{ background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)' }}>
            <div className="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center mb-3">
              <span className="text-base">📊</span>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Expected Move</p>
            <p className="text-2xl font-extrabold text-blue-600">±{deepDiveData.prediction.expected_change_percent.toFixed(2)}%</p>
          </div>

          {/* Confidence */}
          <div className="rounded-2xl p-5 shadow-md hover:shadow-xl transition-all hover:-translate-y-0.5"
            style={{
              background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)',
              borderLeft: deepDiveData.prediction.confidence >= 70 ? '4px solid #22c55e'
                : deepDiveData.prediction.confidence >= 50 ? '4px solid #f59e0b' : '4px solid #ef4444'
            }}>
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-3 ${deepDiveData.prediction.confidence >= 70 ? 'bg-green-100' :
                deepDiveData.prediction.confidence >= 50 ? 'bg-yellow-100' : 'bg-red-100'}`}>
              <span className="text-base">🎯</span>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Confidence</p>
            <p className={`text-2xl font-extrabold ${deepDiveData.prediction.confidence >= 70 ? 'text-green-600' :
                deepDiveData.prediction.confidence >= 50 ? 'text-yellow-500' : 'text-red-500'}`}>
              {deepDiveData.prediction.confidence}%
            </p>
          </div>

          {/* Price Range */}
          <div className="rounded-2xl p-5 shadow-md hover:shadow-xl transition-all hover:-translate-y-0.5 border-l-4 border-l-emerald-400"
            style={{ background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)' }}>
            <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center mb-3">
              <span className="text-base">💰</span>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Price Range</p>
            <p className="text-sm font-extrabold text-emerald-600 leading-snug">
              {Array.isArray(deepDiveData.prediction.range)
                ? `₹${(deepDiveData.current_price * (1 + deepDiveData.prediction.range[0] / 100)).toFixed(0)} – ₹${(deepDiveData.current_price * (1 + deepDiveData.prediction.range[1] / 100)).toFixed(0)}`
                : `₹${deepDiveData.prediction.range.low} – ₹${deepDiveData.prediction.range.high}`}
            </p>
          </div>

          {/* Timeframe */}
          <div className="rounded-2xl p-5 shadow-md hover:shadow-xl transition-all hover:-translate-y-0.5 border-l-4 border-l-orange-400"
            style={{ background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)' }}>
            <div className="w-9 h-9 rounded-xl bg-orange-100 flex items-center justify-center mb-3">
              <span className="text-base">⏱️</span>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Timeframe</p>
            <p className="text-2xl font-extrabold text-orange-500">{deepDiveData.prediction.timeframe}</p>
          </div>
        </div>

        {/* 2-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* LEFT: Chart + Model breakdown */}
          <div className="lg:col-span-2 space-y-5">


            {/* AI Models Ensemble — shown first */}
            {deepDiveData.prediction.model_predictions && Object.keys(deepDiveData.prediction.model_predictions).length > 0 && (
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase">🤖 AI Models Ensemble</p>
                  <button
                    onClick={() => setShowEnsembleInfo(prev => !prev)}
                    className={`px-3 py-1 rounded-full text-xs font-bold border transition-all ${showEnsembleInfo ? 'bg-[#6d5bda] text-white border-[#6d5bda]' : 'text-[#6d5bda] border-[#6d5bda] hover:bg-purple-50'
                      }`}
                  >
                    {showEnsembleInfo ? '✕ Hide' : 'ℹ How it works'}
                  </button>
                </div>
                {showEnsembleInfo && (
                  <div className="mb-5 bg-purple-50 rounded-xl p-4 border border-purple-100">
                    <p className="text-xs text-gray-600 leading-relaxed mb-4">💡 Predictions use a weighted ensemble. ML and semantic models get higher weight; statistical models add trend stability.</p>
                    <div className="space-y-2">
                      {[
                        { name: 'LightGBM', label: 'ML · Gradient Boosting', bars: 4, color: '#f59e0b', desc: 'Trained on sentiment + fundamentals' },
                        { name: 'Qdrant', label: 'Semantic · Vector Search', bars: 3, color: '#14b8a6', desc: 'Similar historical events' },
                        { name: 'GARCH', label: 'Statistical · Volatility', bars: 2, color: '#ec4899', desc: 'Volatility range forecasting' },
                        { name: 'Prophet', label: 'Statistical · Time Series', bars: 1, color: '#6366f1', desc: 'Long-term price trends' },
                      ].map(({ name, label, bars, color, desc }) => (
                        <div key={name} className="flex items-center gap-3">
                          <div className="w-20 shrink-0">
                            <span className="font-bold text-gray-700 text-xs">{name}</span>
                            <p className="text-[10px] text-gray-400">{label}</p>
                          </div>
                          <div className="flex gap-1 items-center flex-1">
                            {[1, 2, 3, 4].map(i => <div key={i} className="h-4 w-8 rounded" style={{ background: i <= bars ? color : '#e5e7eb', opacity: i <= bars ? 1 : 0.4 }} />)}
                            <span className="ml-2 text-[10px] text-gray-400 italic">{desc}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <div className="space-y-2">
                  {Object.entries(deepDiveData.prediction.model_predictions).map(([model, pred]: [string, any]) => {
                    const direction = pred?.direction || (pred > 0 ? 'UP' : 'DOWN');
                    const changePercent = pred?.change_percent ?? pred ?? 0;
                    return (
                      <div key={model} className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors">
                        <span className="font-semibold text-gray-700 text-sm capitalize">{model.replace(/_/g, ' ')}</span>
                        <span className={`font-extrabold text-sm ${direction === 'UP' ? 'text-green-600' : 'text-red-600'}`}>
                          {direction} {changePercent > 0 ? '+' : ''}{Number(changePercent).toFixed(2)}%
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Chart — shown below ensemble */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
                <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase">� Price Chart & Predictions</p>
                <div className="flex gap-1.5 flex-wrap">
                  {['7D', '14D', '30D', '60D'].map(label => {
                    const days = parseInt(label);
                    return (
                      <button key={label} onClick={() => setChartScale(days)}
                        className={`px-3 py-1 rounded-lg text-xs font-bold transition-all border ${chartScale === days ? 'bg-[#6d5bda] text-white border-[#6d5bda]' : 'bg-white text-gray-500 border-gray-200 hover:border-[#6d5bda]'
                          }`}>{label}</button>
                    );
                  })}
                </div>
              </div>
              <div className="flex gap-1.5 flex-wrap mb-4">
                {Object.keys(visibleModels).map(model => (
                  <button key={model} onClick={() => setVisibleModels(prev => ({ ...prev, [model]: !prev[model] }))}
                    className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${visibleModels[model] ? 'bg-[#6d5bda] text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                      }`}>
                    {model === 'ensemble' ? 'Ensemble' : model === 'lstm' ? 'LSTM' : model === 'gru' ? 'GRU' : model.toUpperCase()}
                  </button>
                ))}
              </div>
              <div className="h-[340px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} tickFormatter={(val) => val.includes('-') ? val.split('-').slice(1).join('/') : val} />
                    <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} tickFormatter={(val) => `₹${val.toFixed(0)}`} />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} formatter={(value: any) => [`₹${Number(value).toFixed(2)}`, '']} />
                    <Legend iconType="circle" />
                    <Line type="monotone" dataKey="actual" stroke="#374151" strokeWidth={2.5} dot={false} name="Price" />
                    {visibleModels.ensemble && <Line type="monotone" dataKey="ensemble" stroke="#9333ea" strokeWidth={2.5} strokeDasharray="5 5" name="Ensemble" />}
                    {visibleModels.lstm && <Line type="monotone" dataKey="lstm" stroke="#3b82f6" strokeWidth={1.5} strokeDasharray="3 3" name="LSTM" />}
                    {visibleModels.gru && <Line type="monotone" dataKey="gru" stroke="#10b981" strokeWidth={1.5} strokeDasharray="3 3" name="GRU" />}
                    {visibleModels.lightgbm && <Line type="monotone" dataKey="lightgbm" stroke="#f59e0b" strokeWidth={1} strokeDasharray="2 2" name="LightGBM" />}
                    {visibleModels.garch && <Line type="monotone" dataKey="garch" stroke="#ec4899" strokeWidth={1} strokeDasharray="2 2" name="GARCH" />}
                    {visibleModels.prophet && <Line type="monotone" dataKey="prophet" stroke="#6366f1" strokeWidth={1} strokeDasharray="2 2" name="Prophet" />}
                    {visibleModels.qdrant && <Line type="monotone" dataKey="qdrant" stroke="#14b8a6" strokeWidth={1} strokeDasharray="2 2" name="Qdrant" />}
                    <ReferenceLine x={chartData[chartData.length - 4]?.name} stroke="#d1d5db" strokeDasharray="3 3" label={{ position: 'top', value: 'Prediction Start', fontSize: 10, fill: '#9ca3af' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Analysis context */}
            <div>
              <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase mb-3 px-1">📰 Analysis Context</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                  <div className="w-8 h-8 rounded-xl bg-purple-100 flex items-center justify-center mb-3"><span className="text-sm">📋</span></div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Event Type</p>
                  <p className="text-base font-extrabold text-gray-800 capitalize">{deepDiveData.analysis.event_type || 'Unknown'}</p>
                </div>
                <div className={`bg-white rounded-2xl p-5 shadow-sm border hover:shadow-md transition-shadow ${(typeof deepDiveData.analysis.sentiment === 'string' ? deepDiveData.analysis.sentiment : deepDiveData.analysis.sentiment?.label) === 'positive' ? 'border-green-100' :
                  (typeof deepDiveData.analysis.sentiment === 'string' ? deepDiveData.analysis.sentiment : deepDiveData.analysis.sentiment?.label) === 'negative' ? 'border-red-100' : 'border-gray-100'
                  }`}>
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center mb-3 ${(typeof deepDiveData.analysis.sentiment === 'string' ? deepDiveData.analysis.sentiment : deepDiveData.analysis.sentiment?.label) === 'positive' ? 'bg-green-100' :
                    (typeof deepDiveData.analysis.sentiment === 'string' ? deepDiveData.analysis.sentiment : deepDiveData.analysis.sentiment?.label) === 'negative' ? 'bg-red-100' : 'bg-gray-100'
                    }`}><span className="text-sm">💬</span></div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Sentiment</p>
                  <p className={`text-base font-extrabold capitalize ${(typeof deepDiveData.analysis.sentiment === 'string' ? deepDiveData.analysis.sentiment : deepDiveData.analysis.sentiment?.label) === 'positive' ? 'text-green-600' :
                    (typeof deepDiveData.analysis.sentiment === 'string' ? deepDiveData.analysis.sentiment : deepDiveData.analysis.sentiment?.label) === 'negative' ? 'text-red-600' : 'text-gray-800'
                    }`}>
                    {typeof deepDiveData.analysis.sentiment === 'string'
                      ? deepDiveData.analysis.sentiment
                      : `${deepDiveData.analysis.sentiment?.label || 'Neutral'} (${((deepDiveData.analysis.sentiment?.score || 0) * 100).toFixed(0)}%)`}
                  </p>
                </div>
                <div className={`bg-white rounded-2xl p-5 shadow-sm border hover:shadow-md transition-shadow ${deepDiveData.analysis.severity === 'high' ? 'border-orange-100' :
                  deepDiveData.analysis.severity === 'medium' ? 'border-yellow-100' : 'border-gray-100'
                  }`}>
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center mb-3 ${deepDiveData.analysis.severity === 'high' ? 'bg-orange-100' :
                    deepDiveData.analysis.severity === 'medium' ? 'bg-yellow-100' : 'bg-gray-100'
                    }`}><span className="text-sm">{deepDiveData.analysis.severity === 'high' ? '🔴' : deepDiveData.analysis.severity === 'medium' ? '🟡' : '🟢'}</span></div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Severity</p>
                  <p className={`text-base font-extrabold capitalize ${deepDiveData.analysis.severity === 'high' ? 'text-orange-600' :
                    deepDiveData.analysis.severity === 'medium' ? 'text-yellow-600' : 'text-gray-800'
                    }`}>{deepDiveData.analysis.severity || 'Medium'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT: Fundamentals + Historical sidebar */}
          <div className="lg:col-span-1 space-y-5">

            {deepDiveData.fundamentals && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-5 border-b border-gray-50">
                  <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase">💼 Fundamentals</p>
                </div>
                <div className="divide-y divide-gray-50">
                  {([
                    { label: 'P/E Ratio', value: deepDiveData.fundamentals.pe_ratio },
                    { label: 'Market Cap', value: deepDiveData.fundamentals.market_cap },
                    { label: 'Sector', value: deepDiveData.fundamentals.sector },
                    { label: '52W High', value: deepDiveData.fundamentals['52_week_high'] ? `₹${deepDiveData.fundamentals['52_week_high']}` : null },
                    { label: '52W Low', value: deepDiveData.fundamentals['52_week_low'] ? `₹${deepDiveData.fundamentals['52_week_low']}` : null },
                    { label: 'Volume', value: deepDiveData.fundamentals.volume },
                  ] as { label: string, value: string | number | undefined | null }[]).map(({ label, value }) => (
                    <div key={label} className="flex items-center justify-between px-5 py-3.5 hover:bg-gray-50 transition-colors">
                      <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{label}</span>
                      <span className="text-sm font-extrabold text-gray-800">{value || 'N/A'}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {deepDiveData.prediction.historical_pattern && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-5 border-b border-gray-50">
                  <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase">📚 Historical Pattern</p>
                </div>
                <div className="p-5 grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-blue-400 mb-1">Similar Events</p>
                    <p className="text-2xl font-extrabold text-blue-700">{deepDiveData.prediction.historical_pattern.similar_events}</p>
                  </div>
                  <div className="bg-green-50 rounded-xl p-4 border border-green-100">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-green-400 mb-1">Success Rate</p>
                    <p className="text-2xl font-extrabold text-green-700">
                      {typeof deepDiveData.prediction.historical_pattern.success_rate === 'string'
                        ? deepDiveData.prediction.historical_pattern.success_rate
                        : `${(deepDiveData.prediction.historical_pattern.success_rate * 100).toFixed(0)}%`}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-blue-50 rounded-2xl p-5 border border-blue-100">
              <h4 className="text-sm font-bold text-blue-800 mb-2">Deep Learning Models</h4>
              <p className="text-xs text-blue-600 leading-relaxed">LSTM and GRU analyze 60 days of sequential patterns to identify non-linear trends.</p>
            </div>
            <div className="bg-purple-50 rounded-2xl p-5 border border-purple-100">
              <h4 className="text-sm font-bold text-purple-800 mb-2">Ensemble Approach</h4>
              <p className="text-xs text-purple-600 leading-relaxed">LightGBM, GARCH, Prophet, and Qdrant combined with intelligent weighting for high-conviction signals.</p>
            </div>

          </div>
        </div>
      </div>
    </main>
  );
}
