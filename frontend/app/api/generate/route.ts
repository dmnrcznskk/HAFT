import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    // 1. Pobieramy FormData z żądania frontendu
    const formData = await req.formData();
    
    // 2. Pobieramy parametry z URL (num_colors, width_cm, itp.)
    const { searchParams } = new URL(req.url);
    
    // 3. Budujemy URL do zewnętrznego backendu
    const backendUrl = new URL('http://127.0.0.1:8000/content/embroidery/generate');
    backendUrl.search = searchParams.toString();

    // 4. Przesyłamy żądanie dalej do FastAPI
    const response = await fetch(backendUrl.toString(), {
      method: 'POST',
      body: formData, // Przekazujemy FormData (w tym plik) bezpośrednio
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error("Proxy error:", error);
    return NextResponse.json(
      { error: "Internal Server Error" },
      { status: 500 }
    );
  }
}