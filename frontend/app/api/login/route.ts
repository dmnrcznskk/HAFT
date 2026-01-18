import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // 1. Odbieramy dane z Twojego formularza (w formacie JSON)
    const body = await request.json(); 

    // 2. Przygotowujemy dane dla zewnętrznego API (OAuth2 wymaga x-www-form-urlencoded)
    const formData = new URLSearchParams();
    formData.append('grant_type', 'password');
    formData.append('username', body.username);
    formData.append('password', body.password);

    const res = await fetch('http://127.0.0.1:8000/auth/token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'accept': 'application/json',
      },
      body: formData.toString(),
    });

    const data = await res.json();

    // Zwracamy odpowiedź z API do Twojego frontendu
    return NextResponse.json(data, { status: res.status });
  } catch (error) {
    console.error("Login Error:", error);
    return NextResponse.json({ detail: "Błąd serwera podczas logowania" }, { status: 500 });
  }
}