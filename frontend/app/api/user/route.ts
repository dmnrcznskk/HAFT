import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // Pobieramy token z nagłówka Authorization, który wyślemy z frontendu
  const authHeader = request.headers.get('authorization');

  if (!authHeader) {
    return NextResponse.json({ detail: "Brak tokena" }, { status: 401 });
  }

  try {
    const response = await fetch('https://haft-gjxw.onrender.com/auth/me', {
      method: 'GET',
      headers: {
        'accept': 'application/json',
        'Authorization': authHeader, // Przekazujemy token dalej
      },
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ detail: "Błąd połączenia z serwerem API" }, { status: 500 });
  }
}