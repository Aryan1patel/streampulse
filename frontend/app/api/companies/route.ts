import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export interface Company {
    symbol: string;
    name: string;
}

let cache: Company[] | null = null;

export async function GET() {
    if (cache) return NextResponse.json(cache);

    try {
        // Walk up from frontend/app/api/companies → project root → data/companies.csv
        const csvPath = path.join(process.cwd(), '..', 'data', 'companies.csv');
        const raw = fs.readFileSync(csvPath, 'utf-8');
        const lines = raw.split('\n').slice(1); // skip header

        const companies: Company[] = lines
            .map((line) => {
                const cols = line.split(',');
                const symbol = cols[0]?.trim();
                const name = cols[1]?.trim();
                return symbol && name ? { symbol, name } : null;
            })
            .filter(Boolean) as Company[];

        cache = companies;
        return NextResponse.json(companies);
    } catch (err) {
        console.error('Failed to read companies.csv:', err);
        return NextResponse.json([], { status: 500 });
    }
}
