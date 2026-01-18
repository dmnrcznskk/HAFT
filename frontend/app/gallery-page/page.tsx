'use client';

import React, { useEffect, useState, useRef } from 'react';
import './gallery-page.css';

interface PaletteColor {
  dmc: string;
  name: string;
  rgb: [number, number, number];
  symbol: string;
}

interface GalleryItem {
  id: string;
  url: string;
  title: string;
  text?: string; 
}

export default function GalleryPage() {
  const [images, setImages] = useState<GalleryItem[]>([]);
  const [status, setStatus] = useState<'loading' | 'unauthorized' | 'success' | 'error' | 'saving'>('loading');
  const [selectedItem, setSelectedItem] = useState<GalleryItem | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [grid, setGrid] = useState<string[][]>([]);
  const [palette, setPalette] = useState<PaletteColor[]>([]);
  const [selectedDmc, setSelectedDmc] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

 
  const tryRefreshToken = async (): Promise<string | null> => {
    try {
      const res = await fetch('/api/refresh', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        const newToken = typeof data === 'string' ? data : data.access_token;
        if (newToken) {
          localStorage.setItem('token', newToken);
          return newToken;
        }
      }
    } catch (err) { console.error("Błąd odświeżania:", err); }
    return null;
  };

  const fetchGallery = async (token: string) => {
    try {
      const res = await fetch('/api/gallery', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.status === 401) {
        const newToken = await tryRefreshToken();
        if (newToken) return fetchGallery(newToken);
        setStatus('unauthorized');
        return;
      }
      const data = await res.json();
      setImages(Array.isArray(data) ? data : []);
      setStatus('success');
    } catch (error) { setStatus('error'); }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) fetchGallery(token);
    else setStatus('unauthorized');
  }, []);


  const openEditor = (item: GalleryItem) => {
    setSelectedItem(item);
    if (item.text) {
      try {
        const data = JSON.parse(item.text);
        setGrid(data.grid || []);
        setPalette(data.palette || []);
        setSelectedDmc(data.palette?.[0]?.dmc || null);
        setIsEditing(false);
      } catch (e) { console.error("Błąd parsowania danych", e); }
    }
  };

  useEffect(() => {
    if (!isEditing || !grid.length || !canvasRef.current || !palette.length) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const cellSize = 10;
    canvas.width = grid[0].length * cellSize;
    canvas.height = grid.length * cellSize;

    grid.forEach((row, y) => {
      row.forEach((dmc, x) => {
        const color = palette.find(p => p.dmc === dmc);
        if (color) {
          ctx.fillStyle = `rgb(${color.rgb.join(',')})`;
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
          ctx.strokeStyle = 'rgba(0,0,0,0.1)';
          ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      });
    });
  }, [grid, isEditing, palette]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isEditing || !selectedDmc || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) * (grid[0].length / rect.width));
    const y = Math.floor((e.clientY - rect.top) * (grid.length / rect.height));

    if (y >= 0 && y < grid.length && x >= 0 && x < grid[0].length) {
      const newGrid = [...grid];
      newGrid[y] = [...newGrid[y]];
      newGrid[y][x] = selectedDmc;
      setGrid(newGrid);
    }
  };

  const handleSaveAsNew = async () => {
    let token = localStorage.getItem('token');
    if (!token || !selectedItem || !canvasRef.current) return;

    setStatus('saving');

    const performCreate = async (t: string) => {
     
      const blob = await new Promise<Blob | null>(r => canvasRef.current?.toBlob(r, 'image/png'));
      if (!blob) throw new Error("Błąd generowania obrazu.");
      
      const originalData = JSON.parse(selectedItem.text || '{}');
      const newPatternData = { 
        ...originalData, 
        grid: grid, 
        palette: palette 
      };

      const res = await fetch('/api/create', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${t}` 
        },
        body: JSON.stringify({
          content_type: "embroidery",
          title: `${selectedItem.title} (Edycja)`,
          text: JSON.stringify(newPatternData),
          is_public: false
        })
      });
      return { res, blob };
    };

    try {
      let { res, blob } = await performCreate(token);

      if (res.status === 401) {
        const newToken = await tryRefreshToken();
        if (newToken) {
          const retry = await performCreate(newToken);
          res = retry.res;
          blob = retry.blob;
          token = newToken;
        } else {
          throw new Error("Sesja wygasła.");
        }
      }

      if (!res.ok) throw new Error("Błąd tworzenia nowego wzoru");
      const newContent = await res.json();

      const formData = new FormData();
      formData.append('file', new File([blob!], `edycja_${Date.now()}.png`, { type: 'image/png' }));

      await fetch(`/api/upload/${newContent.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      setSelectedItem(null);
      setIsEditing(false);
      fetchGallery(token!);
    } catch (err: any) {
      alert(err.message);
      setStatus('success');
    }
  };

  return (
    <div className="gallery-container">
      <div className="gallery-grid">
        {images.map((img) => (
          <div key={img.id} className="gallery-item" onClick={() => openEditor(img)}>
            <img src={img.url} alt={img.title} />
            <p className="img-caption">{img.title}</p>
          </div>
        ))}
      </div>

      {selectedItem && (
        <div className="modal-overlay" onClick={() => { setSelectedItem(null); setIsEditing(false); }}>
          <div className="modal-card edit-mode-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{isEditing ? `Edycja: ${selectedItem.title}` : selectedItem.title}</h2>
              <button className="close-btn" onClick={() => { setSelectedItem(null); setIsEditing(false); }}>&times;</button>
            </div>
            <div className="modal-layout">
              <div className="modal-view-main">
                {!isEditing ? (
                  <img src={selectedItem.url} className="full-preview-img" alt="Podgląd" />
                ) : (
                  <div className="canvas-scroll-container">
                    <canvas ref={canvasRef} onMouseDown={handleCanvasClick} className="modal-canvas" />
                  </div>
                )}
              </div>
              <div className="modal-sidebar">
                {!isEditing ? (
                  <button className="btn-primary" onClick={() => setIsEditing(true)}>WŁĄCZ EDYCJĘ</button>
                ) : (
                  <>
                    <div className="mini-palette">
                      <h4>Wybierz kolor:</h4>
                      <div className="palette-grid">
                        {palette.map(c => (
                          <div 
                            key={c.dmc} 
                            className={`swatch ${selectedDmc === c.dmc ? 'active' : ''}`}
                            style={{ backgroundColor: `rgb(${c.rgb.join(',')})` }}
                            onClick={() => setSelectedDmc(c.dmc)}
                            title={c.dmc}
                          />
                        ))}
                      </div>
                    </div>
                    <button className="btn-success" onClick={handleSaveAsNew} disabled={status === 'saving'}>
                      {status === 'saving' ? 'ZAPISYWANIE...' : 'ZAPISZ JAKO NOWY'}
                    </button>
                    <button className="btn-outline" onClick={() => setIsEditing(false)}>ANULUJ</button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}