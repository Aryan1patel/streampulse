'use client';

import { useEffect, useState } from 'react';
import { api, TrendingNews } from '@/lib/api';
import NewsCard from '@/components/NewsCard';
import Loader from '@/components/Loader';

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
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-10">

        {/* Header */}
        <header className="mb-10">
          <h1 className="text-4xl font-bold text-gray-900">📈 StreamPulse</h1>
          <p className="text-gray-600 mt-2">
            Real-time market-moving news with AI-powered deep insights
          </p>
        </header>

        {/* Loading */}
        {loading && <Loader />}

        {/* Error */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Trending News */}
        {!loading && !error && (
          <>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold text-gray-800">
                🔥 Trending News
              </h2>

              <span className="text-sm text-gray-500">
                {trending.length} articles
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trending.map((news) => (
                <NewsCard key={news.id} news={news} />
              ))}
            </div>
          </>
        )}

      </div>
    </main>
  );
}