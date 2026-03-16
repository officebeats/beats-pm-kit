import { readAllTrackers, readVersion } from '@/lib/markdown';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const trackers = readAllTrackers();
  const version = readVersion();
  return NextResponse.json({ trackers, version, timestamp: new Date().toISOString() });
}
