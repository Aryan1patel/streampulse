import Link from 'next/link';
import { TrendingNews } from '@/lib/api';

interface NewsCardProps {
  news: TrendingNews;
}

export default function NewsCard({ news }: NewsCardProps) {
  return (
    <Link href={`/news/${news.id}`}>
      <div className="p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow cursor-pointer bg-white">
        <h3 className="font-semibold text-lg text-gray-900 mb-2 line-clamp-2">
          {news.title}
        </h3>
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
            {news.source}
          </span>
          <span>{new Date(news.fetched_at).toLocaleDateString()}</span>
        </div>
      </div>
    </Link>
  );
}
