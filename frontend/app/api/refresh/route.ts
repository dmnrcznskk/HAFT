import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const cookieHeader = request.headers.get('cookie');

    if (!cookieHeader) {
      return NextResponse.json({ error: 'No cookies found' }, { status: 401 });
    }

    const backendResponse = await fetch('http://127.0.0.1:8000/auth/refresh', {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Cookie': cookieHeader,
      },
    });

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(data, { status: backendResponse.status });
    }

    // --- KLUCZOWA ZMIANA ---
    // Pobieramy nagłówki Set-Cookie z backendu
    const setCookie = backendResponse.headers.get('set-cookie');

    const response = NextResponse.json(data);

    // Jeśli backend wysłał nowe ciasteczka, przekazujemy je do przeglądarki
    if (setCookie) {
      response.headers.set('set-cookie', setCookie);
    }

    return response;
    // -----------------------
    
  } catch (error: any) {
    return NextResponse.json({ error: 'Server error', details: error.message }, { status: 500 });
  }
}