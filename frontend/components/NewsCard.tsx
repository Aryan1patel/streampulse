import Link from 'next/link';
import { TrendingNews } from '@/lib/api';

interface NewsCardProps {
  news: TrendingNews;
}

export default function NewsCard({ news }: NewsCardProps) {
  return (
    <Link href={`/news/${news.id}`}>
      <div className="bg-white p-5 h-full flex flex-col rounded-2xl hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 cursor-pointer relative overflow-hidden group">

        {/* Subtle top-right glow */}
        <div className="absolute -top-8 -right-8 w-24 h-24 bg-purple-200/25 rounded-full blur-2xl group-hover:bg-purple-300/35 transition-colors duration-300 pointer-events-none"></div>

        <h3 className="font-bold text-[15px] text-gray-800 mb-5 line-clamp-3 leading-snug relative z-10 flex-grow">
          {news.title}
        </h3>

        <div className="flex items-center justify-between mt-auto relative z-10">
          <span className="text-[11px] font-semibold text-white px-3 py-1 rounded-full" style={{ background: 'rgba(109, 91, 218, 0.85)' }}>
            {news.source}
          </span>
          <span className="text-[11px] text-gray-400 font-medium">{new Date(news.fetched_at).toLocaleDateString()}</span>
        </div>
      </div>
    </Link>
  );
}
