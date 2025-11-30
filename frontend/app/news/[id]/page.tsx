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
  const [searchQuery, setSearchQuery] = useState('');
  const [relatedArticles, setRelatedArticles] = useState<RelatedArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [deepDiveLoading, setDeepDiveLoading] = useState(false);
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
      setSearchQuery(deepDiveData.searchQuery);
      setRelatedArticles(deepDiveData.relatedArticles);
    } catch (err: any) {
      console.error('Deep dive failed:', err);
      
      // Set partial data if available
      setKeywords([]);
      setSearchQuery('');
      setRelatedArticles([]);
      
      // Show user-friendly error
      alert(`Unable to fetch deep dive: ${err.message || 'Request timeout'}. Please try again.`);
    } finally {
      setDeepDiveLoading(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Loader />
        </div>
      </main>
    );
  }

  if (error || !news) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error || 'News not found'}
          </div>
          <button
            onClick={() => router.push('/')}
            className="mt-4 text-blue-600 hover:underline"
          >
            ← Back to trending
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <button
          onClick={() => router.push('/')}
          className="mb-6 text-blue-600 hover:underline flex items-center gap-2"
        >
          ← Back to trending
        </button>

        {/* Original News */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded text-sm font-medium">
                {news.source}
              </span>
              <span className="text-gray-500 text-sm ml-3">
                {new Date(news.fetched_at).toLocaleString()}
              </span>
            </div>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {news.title}
          </h1>
          
          <a
            href={news.link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            View original article →
          </a>
        </div>

        {/* Keywords Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            🔍 Extracted Keywords
          </h2>
          
          {deepDiveLoading ? (
            <Loader />
          ) : keywords.length > 0 ? (
            <div>
              <div className="flex flex-wrap gap-2 mb-4">
                {keywords.map((keyword, idx) => (
                  <KeywordChip
                    key={idx}
                    keyword={keyword}
                    priority={idx < 3}
                  />
                ))}
              </div>
              <p className="text-sm text-gray-600 mt-4">
                <strong>Search Query:</strong> {searchQuery}
              </p>
            </div>
          ) : (
            <p className="text-gray-500">No keywords extracted yet...</p>
          )}
        </div>

        {/* Related Articles */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            📰 Related Articles ({relatedArticles.length})
          </h2>
          
          {deepDiveLoading ? (
            <Loader />
          ) : relatedArticles.length > 0 ? (
            <div className="space-y-4">
              {relatedArticles.map((article, idx) => (
                <div
                  key={idx}
                  className="border-l-4 border-green-500 pl-4 py-2 hover:bg-gray-50 transition-colors"
                >
                  <a
                    href={article.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block"
                  >
                    <h3 className="font-semibold text-gray-900 hover:text-blue-600">
                      {article.title}
                    </h3>
                    {article.description && (
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {article.description}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {article.source}
                      </span>
                    </div>
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No related articles found yet...</p>
          )}
        </div>
      </div>
    </main>
  );
}
