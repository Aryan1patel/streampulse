'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

interface Company {
    symbol: string;
    name: string;
}

export default function StockSearch() {
    const router = useRouter();
    const [query, setQuery] = useState('');
    const [companies, setCompanies] = useState<Company[]>([]);
    const [results, setResults] = useState<Company[]>([]);
    const [open, setOpen] = useState(false);
    const [highlighted, setHighlighted] = useState(-1);
    const inputRef = useRef<HTMLInputElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Fetch company list once
    useEffect(() => {
        fetch('/api/companies')
            .then((r) => r.json())
            .then((data: Company[]) => setCompanies(data))
            .catch(console.error);
    }, []);

    // Filter on query change
    useEffect(() => {
        const q = query.trim().toLowerCase();
        if (!q) { setResults([]); setOpen(false); return; }
        const filtered = companies
            .filter((c) => c.symbol.toLowerCase().includes(q) || c.name.toLowerCase().includes(q))
            .slice(0, 8);
        setResults(filtered);
        setOpen(filtered.length > 0);
        setHighlighted(-1);
    }, [query, companies]);

    // Close on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    const navigate = (symbol: string) => {
        setOpen(false);
        setQuery('');
        router.push(`/deep-dive/${symbol}`);
    };

    const handleKey = (e: React.KeyboardEvent) => {
        if (!open) return;
        if (e.key === 'ArrowDown') { e.preventDefault(); setHighlighted((h) => Math.min(h + 1, results.length - 1)); }
        if (e.key === 'ArrowUp') { e.preventDefault(); setHighlighted((h) => Math.max(h - 1, 0)); }
        if (e.key === 'Enter' && highlighted >= 0) navigate(results[highlighted].symbol);
        if (e.key === 'Escape') setOpen(false);
    };

    return (
        <div ref={containerRef} className="relative w-full max-w-2xl mx-auto">
            {/* Input */}
            <div
                className="flex items-center gap-3 px-5 py-4 rounded-2xl shadow-2xl transition-all duration-200"
                style={{
                    background: 'rgba(255,255,255,0.95)',
                    border: open ? '2px solid #7c3aed' : '2px solid transparent',
                    backdropFilter: 'blur(12px)',
                }}
            >
                {/* Search icon */}
                <svg className="w-5 h-5 shrink-0" style={{ color: '#7c3aed' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" strokeLinecap="round" />
                </svg>

                <input
                    ref={inputRef}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKey}
                    onFocus={() => results.length > 0 && setOpen(true)}
                    placeholder="Search any NSE stock — e.g. TCS, Infosys, RELIANCE..."
                    className="flex-1 outline-none text-gray-800 font-medium placeholder-gray-400 bg-transparent text-base"
                />

                {query && (
                    <button onClick={() => { setQuery(''); setOpen(false); inputRef.current?.focus(); }}
                        className="text-gray-400 hover:text-gray-600 transition-colors">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}

                <button
                    onClick={() => { if (results.length > 0) navigate(results[0].symbol); }}
                    disabled={results.length === 0}
                    className="px-5 py-2 rounded-xl font-bold text-sm text-white transition-all duration-200 disabled:opacity-40"
                    style={{ background: 'linear-gradient(135deg, #7c3aed, #2563eb)', boxShadow: '0 4px 12px rgba(124,58,237,0.35)' }}
                >
                    Deep Dive
                </button>
            </div>

            {/* Dropdown */}
            {open && (
                <div
                    className="absolute left-0 right-0 mt-2 rounded-2xl shadow-2xl overflow-hidden z-50"
                    style={{ background: 'rgba(255,255,255,0.98)', border: '1px solid rgba(124,58,237,0.2)', backdropFilter: 'blur(12px)' }}
                >
                    {results.map((company, i) => {
                        const q = query.trim().toLowerCase();
                        const sym = company.symbol;
                        const name = company.name;

                        // Bold-highlight matching part
                        const highlight = (text: string) => {
                            const idx = text.toLowerCase().indexOf(q);
                            if (idx === -1) return <span>{text}</span>;
                            return (
                                <span>
                                    {text.slice(0, idx)}
                                    <span className="font-extrabold" style={{ color: '#7c3aed' }}>{text.slice(idx, idx + q.length)}</span>
                                    {text.slice(idx + q.length)}
                                </span>
                            );
                        };

                        return (
                            <button
                                key={sym}
                                onMouseDown={() => navigate(sym)}
                                onMouseEnter={() => setHighlighted(i)}
                                className="w-full flex items-center gap-4 px-5 py-3.5 text-left transition-colors duration-100"
                                style={{ background: highlighted === i ? 'linear-gradient(135deg, #f5f3ff, #eff6ff)' : 'transparent' }}
                            >
                                {/* Symbol badge */}
                                <span
                                    className="shrink-0 px-2.5 py-1 rounded-lg text-xs font-extrabold tracking-wide"
                                    style={{ background: 'linear-gradient(135deg, #7c3aed22, #2563eb22)', color: '#7c3aed' }}
                                >
                                    {highlight(sym)}
                                </span>

                                {/* Company name */}
                                <span className="flex-1 text-sm text-gray-700 truncate">{highlight(name)}</span>

                                {/* Arrow */}
                                <span className="text-xs font-bold shrink-0 transition-transform duration-150"
                                    style={{
                                        color: highlighted === i ? '#7c3aed' : '#d1d5db',
                                        transform: highlighted === i ? 'translateX(2px)' : 'none'
                                    }}>
                                    →
                                </span>
                            </button>
                        );
                    })}

                    {/* Footer hint */}
                    <div className="px-5 py-2.5 border-t text-xs text-gray-400 flex items-center gap-2"
                        style={{ borderColor: 'rgba(124,58,237,0.1)' }}>
                        <kbd className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 font-mono text-xs">↑↓</kbd> navigate
                        <kbd className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 font-mono text-xs ml-1">↵</kbd> select
                        <kbd className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 font-mono text-xs ml-1">esc</kbd> close
                        <span className="ml-auto">{companies.length.toLocaleString()} stocks indexed</span>
                    </div>
                </div>
            )}
        </div>
    );
}
