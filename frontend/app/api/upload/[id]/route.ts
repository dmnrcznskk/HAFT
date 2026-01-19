import { NextResponse } from 'next/server';

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = await params;
    const authHeader = request.headers.get('Authorization');
    const contentType = request.headers.get('content-type');

    // Sprawdzamy, czy zapytanie zawiera poprawne nagłówki
    if (!contentType || !contentType.includes('multipart/form-data')) {
        return NextResponse.json({ error: 'Nieprawidłowy Content-Type' }, { status: 400 });
    }

    // Pobieramy całe body jako Blob (dane binarne wraz z boundary)
    const blob = await request.blob();

    // Przekazujemy dane bezpośrednio do Rendera
    const backendResponse = await fetch(`https://haft-gjxw.onrender.com/content/${id}/embroidery/`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader || '',
        'accept': 'application/json',
        // PRZEKAZUJEMY ORYGINALNY CONTENT-TYPE (zawiera boundary!)
        'content-type': contentType,
      },
      body: blob,
    });

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      console.error("Backend 422 Error:", data);
      return NextResponse.json(data, { status: backendResponse.status });
    }

    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error("Proxy Upload Critical Error:", error);
    return NextResponse.json({ error: 'Server error', message: error.message }, { status: 500 });
  }
}

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = await params;
    const authHeader = request.headers.get('Authorization');

    const backendResponse = await fetch(`http://127.0.0.1:8000/content/${id}/embroidery/`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader || '',
        'accept': 'application/json',
      },
    });

    if (!backendResponse.ok) {
      return NextResponse.json({ error: 'Błąd pobierania z backendu' }, { status: backendResponse.status });
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    return NextResponse.json({ error: 'Server error', message: error.message }, { status: 500 });
  }
}