import { NextRequest, NextResponse } from 'next/server';

const RELATED_FETCHER_URL = process.env.RELATED_FETCHER_URL || 'http://localhost:7001';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const headline = searchParams.get('headline');
    const keywords = searchParams.get('keywords');
    const isBusiness = searchParams.get('is_business') || 'true';

    if (!headline) {
      return NextResponse.json(
        { error: 'headline parameter is required' },
        { status: 400 }
      );
    }

    const params = new URLSearchParams({ 
      headline,
      is_business: isBusiness
    });
    
    // Add keywords if provided (improves search quality)
    if (keywords) {
      params.append('keywords', keywords);
    }

    console.log(`🔍 Fetching related articles - Headline: "${headline}", Keywords: "${keywords}"`);
    
    const response = await fetch(`${RELATED_FETCHER_URL}/fetch_related?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Related Fetcher returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Related Fetcher API Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch related articles' },
      { status: 500 }
    );
  }
}
