interface KeywordChipProps {
  keyword: string;
  priority?: boolean;
}

export default function KeywordChip({ keyword, priority }: KeywordChipProps) {
  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium ${
        priority
          ? 'bg-green-100 text-green-800 border border-green-300'
          : 'bg-gray-100 text-gray-700 border border-gray-300'
      }`}
    >
      {keyword}
    </span>
  );
}
