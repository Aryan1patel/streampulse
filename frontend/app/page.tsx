'use client';

import { useEffect, useState } from 'react';
import { api, TrendingNews } from '@/lib/api';
import NewsCard from '@/components/NewsCard';
import Loader from '@/components/Loader';
import StockSearch from '@/components/StockSearch';

export default function Home() {
  const [trending, setTrending] = useState<TrendingNews[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        setLoading(true);
        const data = await api.getTrending(50);
        setTrending(data);
      } catch (err) {
        setError('Failed to fetch trending news');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTrending();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#6273e9] via-[#6d5bda] to-[#7f5ae6]">
      <div className="max-w-7xl mx-auto px-4 py-8 flex flex-col items-center">

        {/* Header */}
        <header className="mb-6 flex flex-col items-center text-center">
          <div className="bg-white rounded-full px-10 py-1 inline-flex items-center gap-8 shadow-xl mb-3 mt-2">
            <div className="w-7 h-7 bg-[#a855f7] rounded-[4px]"></div>
            <h1 className="text-[34px] font-bold text-[#8b5cf6] tracking-tight">StreamPulse</h1>
          </div>

          <p className="text-white/95 text-lg font-medium mb-2 max-w-2xl">
            Real-time market-moving news with AI-powered deep insights
          </p>

          <div className="flex items-center gap-6 text-[13px] text-white/80 font-medium mb-2">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#4ade80] shadow-[0_0_8px_rgba(74,222,128,0.8)]"></div>
              Live Updates
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#60a5fa] shadow-[0_0_8px_rgba(96,165,250,0.8)]"></div>
              AI Analysis
            </div>
          </div>

          <div className="w-full flex flex-col items-center mt-1 max-w-3xl">
            <div className="text-white/80 text-[11px] font-bold tracking-[0.15em] uppercase mb-2 flex items-center gap-2">
              <span>🔍</span> DIRECT STOCK DEEP DIVE
            </div>
            <StockSearch />
          </div>
        </header>

        {/* Main Content Area */}
        <div className="w-full max-w-[1100px] mt-4">

          {/* Loading */}
          {loading && <Loader />}

          {/* Error */}
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-white px-4 py-3 rounded-xl backdrop-blur-sm">
              {error}
            </div>
          )}

          {/* Trending News */}
          {!loading && !error && (
            <>
              {/* Trending Header Bar */}
              <div className="bg-white rounded-[20px] p-5 flex items-center justify-between mb-8 shadow-xl">
                <h2 className="text-[22px] font-bold flex items-center gap-2" style={{ color: '#ff4500' }}>
                  <span>🔥</span> Trending Now
                </h2>
                <span className="bg-[#f3f4f6] text-[#6b7280] px-4 py-2 rounded-full text-xs font-bold tracking-wide">
                  {trending.length} articles
                </span>
              </div>

              {/* News Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {trending.map((news) => (
                  <NewsCard key={news.id} news={news} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}