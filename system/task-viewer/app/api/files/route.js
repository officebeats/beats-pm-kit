import { listDirectory, readFile } from '@/lib/markdown';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const dir = searchParams.get('dir') || '';
  const file = searchParams.get('file');

  if (file) {
    const content = readFile(file);
    if (!content) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    return NextResponse.json({ path: file, content });
  }

  const entries = listDirectory(dir);
  return NextResponse.json({ path: dir, entries });
}
