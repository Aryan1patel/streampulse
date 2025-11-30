import { NextRequest, NextResponse } from 'next/server';

const KEYWORD_EXTRACTOR_URL = process.env.KEYWORD_EXTRACTOR_URL || 'http://localhost:7002';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const headline = searchParams.get('headline');
    const url = searchParams.get('url');
    const source = searchParams.get('source');

    if (!headline) {
      return NextResponse.json(
        { error: 'headline parameter is required' },
        { status: 400 }
      );
    }

    const params = new URLSearchParams({ headline });
    if (url) params.append('url', url);
    if (source) params.append('source', source);

    const response = await fetch(`${KEYWORD_EXTRACTOR_URL}/keywords?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Keyword Extractor returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Keywords API Error:', error);
    return NextResponse.json(
      { error: 'Failed to extract keywords' },
      { status: 500 }
    );
  }
}
