'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, TrendingNews, RelatedArticle } from '@/lib/api';
import KeywordChip from '@/components/KeywordChip';
import Loader from '@/components/Loader';

export default function NewsDetailPage() {
  const params = useParams();
  const router = useRouter();
  const newsId = params.id as string;

  const [news, setNews] = useState<TrendingNews | null>(null);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [companies, setCompanies] = useState<string[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [relatedArticles, setRelatedArticles] = useState<RelatedArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [deepDiveLoading, setDeepDiveLoading] = useState(false);
  const [deepDiveError, setDeepDiveError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch the trending news item
  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const allNews = await api.getTrending(100);
        const foundNews = allNews.find((n) => n.id === newsId);
        if (foundNews) {
          setNews(foundNews);
        } else {
          setError('News not found');
        }
      } catch (err) {
        setError('Failed to fetch news');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [newsId]);

  // Trigger deep dive when news is loaded
  useEffect(() => {
    if (news) {
      performDeepDive();
    }
  }, [news]);

  const performDeepDive = async () => {
    if (!news) return;

    try {
      setDeepDiveLoading(true);

      console.log('Starting deep dive for:', news.title);
      console.log('Article URL:', news.link);
      console.log('Source:', news.source);

      // Pass URL and source for full article scraping and keyword extraction
      const deepDiveData = await api.getDeepDive(newsId, news.title, news.link, news.source);

      console.log('Deep dive complete:', deepDiveData);
      console.log('Article content length:', deepDiveData.contentLength, 'characters');

      setKeywords(deepDiveData.keywords);
      setCompanies(deepDiveData.companies || []);
      setAnalysis(deepDiveData.analysis || null);
      setSearchQuery(deepDiveData.searchQuery);
      setRelatedArticles(deepDiveData.relatedArticles);
    } catch (err: any) {
      console.error('Deep dive failed:', err);

      // Set partial data if available
      setKeywords([]);
      setCompanies([]);
      setAnalysis(null);
      setSearchQuery('');
      setRelatedArticles([]);

      // Show inline error instead of browser alert
      setDeepDiveError(err.message?.includes('timeout')
        ? 'AI analysis is taking longer than expected (model warming up). Please try again in a moment.'
        : `AI analysis failed: ${err.message || 'Unknown error'}`);
    } finally {
      setDeepDiveLoading(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f0eeff]">
        <div className="bg-white border-b border-purple-100 shadow-sm">
          <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center gap-3">
            <div className="w-1.5 h-1.5 rounded-full bg-[#6d5bda] animate-pulse" />
            <span className="text-xs font-bold text-gray-400 tracking-widest uppercase">StreamPulse · Loading Article</span>
          </div>
        </div>
        <div className="max-w-xl mx-auto px-6 py-16">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-purple-100">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4 shadow-md" style={{ background: 'linear-gradient(135deg, #7c3aed, #6d5bda)' }}>
                <span className="text-2xl">📰</span>
              </div>
              <h2 className="text-xl font-extrabold text-gray-900">Fetching Article</h2>
              <p className="text-gray-500 text-sm mt-1">Loading news & running AI analysis…</p>
            </div>
            <div className="space-y-2">
              {[
                { icon: '📡', label: 'Fetching trending news feed', detail: 'Querying live news database' },
                { icon: '🔍', label: 'Finding your article', detail: 'Matching article ID' },
                { icon: '🤖', label: 'Running AI analysis', detail: 'Sentiment · Event Type · Keywords' },
              ].map((step, i) => (
                <div key={i} className="flex items-center gap-3 rounded-xl px-4 py-3 bg-purple-50 border border-purple-100">
                  <div className="shrink-0 w-7 h-7 flex items-center justify-center">
                    <svg className="animate-spin w-5 h-5 text-[#6d5bda]" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-[#6d5bda]">{step.icon} {step.label}</p>
                    <p className="text-xs text-purple-400 mt-0.5">{step.detail}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 w-full h-1.5 bg-purple-100 rounded-full overflow-hidden">
              <div className="h-full rounded-full animate-pulse" style={{ width: '60%', background: 'linear-gradient(90deg, #7c3aed, #6d5bda)' }} />
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (error || !news) {
    return (
      <main className="min-h-screen bg-[#f0eeff]">
        <div className="bg-white border-b border-purple-100 shadow-sm">
          <div className="max-w-7xl mx-auto px-6 py-3.5">
            <button onClick={() => router.push('/')} className="flex items-center gap-2 text-gray-500 hover:text-gray-800 font-semibold text-sm transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
              Back to Feed
            </button>
          </div>
        </div>
        <div className="max-w-xl mx-auto px-6 py-12">
          <div className="bg-white rounded-2xl p-6 border border-red-100 shadow-sm">
            <p className="font-semibold text-red-600">⚠️ {error || 'News not found'}</p>
            <button onClick={() => router.push('/')} className="mt-4 text-sm text-[#6d5bda] font-semibold hover:underline">← Back to Feed</button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f0eeff]">
      {/* Top nav bar */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-gray-500 hover:text-gray-800 font-semibold text-sm transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Feed
          </button>
          <div className="flex items-center gap-2 text-xs font-bold text-gray-400 tracking-widest uppercase">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.8)] animate-pulse" />
            StreamPulse · AI Analysis
          </div>
          <a
            href={news.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm font-semibold text-white bg-[#6d5bda] hover:bg-[#7c68e8] px-4 py-2 rounded-full transition-colors shadow-md"
          >
            Read Article →
          </a>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Error banner */}
        {deepDiveError && !deepDiveLoading && (
          <div className="flex items-center justify-between bg-amber-50 border border-amber-200 rounded-2xl px-5 py-3 mb-6 shadow-sm">
            <div className="flex items-center gap-2 text-amber-700 text-sm">
              <span>⏳</span> {deepDiveError}
            </div>
            <button
              onClick={() => { setDeepDiveError(null); performDeepDive(); }}
              className="text-xs font-bold bg-amber-500 hover:bg-amber-600 text-white px-3 py-1.5 rounded-full transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* 2-col layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* LEFT COLUMN - Main content (2/3 width) */}
          <div className="lg:col-span-2 space-y-5">

            {/* Article hero card */}
            <div className="bg-white rounded-2xl p-7 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-5">
                <span className="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-wider uppercase text-[#6d5bda] bg-purple-50 border border-purple-100 px-3 py-1 rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#6d5bda]" />
                  {news.source}
                </span>
                <span className="text-xs text-gray-400">{new Date(news.fetched_at).toLocaleString()}</span>
              </div>
              <h1 className="text-[22px] font-extrabold text-gray-900 leading-snug mb-6">
                {news.title}
              </h1>
              <a
                href={news.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#6d5bda] hover:text-[#8b5cf6] transition-colors"
              >
                Read the full original article <span>→</span>
              </a>
            </div>

            {/* AI Analysis stat cards */}
            <div>
              <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase mb-3 px-1">AI Analysis</p>
              {deepDiveLoading ? (
                <div className="grid grid-cols-3 gap-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 animate-pulse h-24" />
                  ))}
                </div>
              ) : analysis ? (
                <div className="grid grid-cols-3 gap-4">
                  {/* Event Type */}
                  <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                    <div className="w-8 h-8 rounded-xl bg-purple-100 flex items-center justify-center mb-3">
                      <span className="text-sm">📋</span>
                    </div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Event Type</p>
                    <p className="text-base font-extrabold text-gray-800 capitalize">{analysis.event_type}</p>
                  </div>
                  {/* Sentiment */}
                  <div className={`bg-white rounded-2xl p-5 shadow-sm border hover:shadow-md transition-shadow ${analysis.sentiment?.label === 'positive' ? 'border-green-100' :
                    analysis.sentiment?.label === 'negative' ? 'border-red-100' : 'border-gray-100'
                    }`}>
                    <div className={`w-8 h-8 rounded-xl flex items-center justify-center mb-3 ${analysis.sentiment?.label === 'positive' ? 'bg-green-100' :
                      analysis.sentiment?.label === 'negative' ? 'bg-red-100' : 'bg-gray-100'
                      }`}>
                      <span className="text-sm">
                        {analysis.sentiment?.label === 'positive' ? '📈' : analysis.sentiment?.label === 'negative' ? '📉' : '➡️'}
                      </span>
                    </div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Sentiment</p>
                    <p className={`text-base font-extrabold capitalize ${analysis.sentiment?.label === 'positive' ? 'text-green-600' :
                      analysis.sentiment?.label === 'negative' ? 'text-red-600' : 'text-gray-800'
                      }`}>
                      {analysis.sentiment?.label || 'Neutral'}
                      {analysis.sentiment?.score && (
                        <span className="text-xs font-semibold ml-1 opacity-60">
                          {Math.round(analysis.sentiment.score * 100)}%
                        </span>
                      )}
                    </p>
                  </div>
                  {/* Severity */}
                  <div className={`bg-white rounded-2xl p-5 shadow-sm border hover:shadow-md transition-shadow ${analysis.severity === 'high' ? 'border-orange-100' :
                    analysis.severity === 'medium' ? 'border-yellow-100' : 'border-gray-100'
                    }`}>
                    <div className={`w-8 h-8 rounded-xl flex items-center justify-center mb-3 ${analysis.severity === 'high' ? 'bg-orange-100' :
                      analysis.severity === 'medium' ? 'bg-yellow-100' : 'bg-gray-100'
                      }`}>
                      <span className="text-sm">
                        {analysis.severity === 'high' ? '🔴' : analysis.severity === 'medium' ? '🟡' : '🟢'}
                      </span>
                    </div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Severity</p>
                    <p className={`text-base font-extrabold capitalize ${analysis.severity === 'high' ? 'text-orange-600' :
                      analysis.severity === 'medium' ? 'text-yellow-600' : 'text-gray-800'
                      }`}>{analysis.severity}</p>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-gray-400 text-sm">
                  Analysis not available
                </div>
              )}
            </div>

            {/* Keywords */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase mb-4">Keywords</p>
              {deepDiveLoading ? (
                <div className="flex gap-2 flex-wrap">
                  {[...Array(8)].map((_, i) => (
                    <div key={i} className="h-7 w-20 bg-gray-100 rounded-full animate-pulse" />
                  ))}
                </div>
              ) : keywords.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {keywords.map((kw, i) => (
                    <span
                      key={i}
                      className="text-xs font-semibold text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 px-3 py-1.5 rounded-full transition-colors cursor-default"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-sm">No keywords extracted yet</p>
              )}
            </div>

            {/* Companies */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase">Companies</p>
                <span className="text-[10px] text-gray-300 font-semibold">🤖 Click for AI stock analysis</span>
              </div>
              {deepDiveLoading ? (
                <div className="flex gap-3 flex-wrap">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-10 w-28 bg-gray-100 rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : companies && companies.length > 0 ? (
                <div className="flex flex-wrap gap-3">
                  {companies.map((company, i) => (
                    <button
                      key={i}
                      onClick={() => router.push(`/deep-dive/${company}`)}
                      className="group flex items-center gap-2 bg-purple-50 hover:bg-[#6d5bda] border border-purple-100 hover:border-[#6d5bda] text-[#6d5bda] hover:text-white font-bold text-sm px-5 py-2.5 rounded-xl transition-all hover:shadow-lg hover:shadow-purple-200 hover:-translate-y-0.5"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-[#6d5bda] group-hover:bg-white transition-colors" />
                      {company}
                      <span className="text-xs opacity-50 group-hover:opacity-100">→</span>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-sm">No companies detected</p>
              )}
            </div>

          </div>

          {/* RIGHT COLUMN - Related articles sidebar (1/3 width) */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 sticky top-20">
              <div className="p-5 border-b border-gray-50">
                <p className="text-[11px] font-bold tracking-[0.18em] text-gray-400 uppercase">
                  Related Articles
                  {!deepDiveLoading && relatedArticles.length > 0 && (
                    <span className="ml-2 bg-purple-100 text-[#6d5bda] px-2 py-0.5 rounded-full text-[10px]">
                      {relatedArticles.length}
                    </span>
                  )}
                </p>
              </div>
              <div className="divide-y divide-gray-50 max-h-[calc(100vh-200px)] overflow-y-auto">
                {deepDiveLoading ? (
                  <div className="p-4 space-y-4">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="space-y-2 animate-pulse">
                        <div className="h-4 bg-gray-100 rounded-full w-full" />
                        <div className="h-3 bg-gray-100 rounded-full w-2/3" />
                      </div>
                    ))}
                  </div>
                ) : relatedArticles.length > 0 ? (
                  relatedArticles.map((article, i) => (
                    <a
                      key={i}
                      href={article.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group flex items-start gap-3 p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="shrink-0 w-1.5 h-1.5 rounded-full bg-purple-300 group-hover:bg-[#6d5bda] mt-2 transition-colors" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-700 group-hover:text-[#6d5bda] transition-colors line-clamp-2 leading-snug">
                          {article.title}
                        </p>
                        <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wide mt-1.5">
                          {article.source}
                        </p>
                      </div>
                    </a>
                  ))
                ) : (
                  <p className="text-gray-400 text-sm p-5">No related articles found</p>
                )}
              </div>
            </div>
          </div>

        </div>
      </div>
    </main>
  );
}


