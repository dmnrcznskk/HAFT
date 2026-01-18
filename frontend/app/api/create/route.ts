import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    // Pobieramy nagłówek, który przyszedł z page.tsx
    const authHeader = request.headers.get('Authorization');

    const backendResponse = await fetch('http://127.0.0.1:8000/content/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        // Przekazujemy otrzymany token Bearer do Rendera
        'Authorization': authHeader || '', 
      },
      body: JSON.stringify(body),
    });

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: 'Błąd autoryzacji backendu', details: JSON.stringify(data) }, 
        { status: backendResponse.status }
      );
    }

    return NextResponse.json(data);
    
  } catch (error: any) {
    return NextResponse.json({ error: 'Server error', message: error.message }, { status: 500 });
  }
}

