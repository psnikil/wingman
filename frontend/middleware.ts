import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { useBackendStore } from '@/store/backendStore';

export function middleware(request: NextRequest) {
  const {backendInit, setBackendInit} = useBackendStore();
//   const { initialized } = backendInit

  if (!backendInit && request.nextUrl.pathname !== '/') {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next|favicon.ico|api).*)'], // Adjust based on your routes
};
