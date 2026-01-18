'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { jsPDF } from 'jspdf';
import './generator-page.css';

interface PaletteColor {
  dmc: string;
  name: string;
  rgb: [number, number, number];
  symbol: string;
}

interface EmbroideryData {
  preview_png: string;
  grid?: string[][]; 
  meta: {
    width: number;
    height: number;
    aida: number;
    colors: number;
  };
  palette: PaletteColor[];
  stats: Record<string, number>;
}

export default function GeneratorPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'generating' | 'preview-ready' | 'saving' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [isUserLoggedIn, setIsUserLoggedIn] = useState<boolean>(false);

  const [generatedData, setGeneratedData] = useState<EmbroideryData | null>(null);
  const [grid, setGrid] = useState<string[][]>([]);
  const [history, setHistory] = useState<string[][][]>([]);
  const [historyStep, setHistoryStep] = useState(-1);
  const [selectedDmc, setSelectedDmc] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [numColors, setNumColors] = useState<number>(12);
  const [widthCm, setWidthCm] = useState<number>(20);
  const [aidaCount, setAidaCount] = useState<number>(14);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsUserLoggedIn(!!token);
  }, []);

  const tryRefreshToken = async (): Promise<string | null> => {
    try {
      const res = await fetch('/api/refresh', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        const newToken = typeof data === 'string' ? data : data.access_token;
        if (newToken) {
          localStorage.setItem('token', newToken);
          setIsUserLoggedIn(true);
          return newToken;
        }
      }
    } catch (err) { console.error("Błąd odświeżania:", err); }
    return null;
  };

  const initializeGridFromImage = useCallback((data: EmbroideryData) => {
    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.src = data.preview_png;
    
    img.onload = () => {
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = data.meta.width;
      tempCanvas.height = data.meta.height;
      const tempCtx = tempCanvas.getContext('2d');
      if (!tempCtx) return;

      tempCtx.drawImage(img, 0, 0, data.meta.width, data.meta.height);
      const imageData = tempCtx.getImageData(0, 0, data.meta.width, data.meta.height).data;
      
      const newGrid: string[][] = [];
      for (let y = 0; y < data.meta.height; y++) {
        const row: string[] = [];
        for (let x = 0; x < data.meta.width; x++) {
          const i = (y * data.meta.width + x) * 4;
          const [r, g, b] = [imageData[i], imageData[i+1], imageData[i+2]];

          const closest = data.palette.reduce((prev, curr) => {
            const dPrev = Math.sqrt((prev.rgb[0]-r)**2 + (prev.rgb[1]-g)**2 + (prev.rgb[2]-b)**2);
            const dCurr = Math.sqrt((curr.rgb[0]-r)**2 + (curr.rgb[1]-g)**2 + (curr.rgb[2]-b)**2);
            return dCurr < dPrev ? curr : prev;
          });
          row.push(closest.dmc);
        }
        newGrid.push(row);
      }
      setGrid(newGrid);
      setHistory([JSON.parse(JSON.stringify(newGrid))]);
      setHistoryStep(0);
    };
  }, []);

  useEffect(() => {
    if (!isEditing || !grid.length || !canvasRef.current || !generatedData) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const displaySize = 10;
    canvas.width = generatedData.meta.width * displaySize;
    canvas.height = generatedData.meta.height * displaySize;

    grid.forEach((row, y) => {
      row.forEach((dmc, x) => {
        const color = generatedData.palette.find(p => p.dmc === dmc);
        if (color) {
          ctx.fillStyle = `rgb(${color.rgb.join(',')})`;
          ctx.fillRect(x * displaySize, y * displaySize, displaySize, displaySize);
          ctx.strokeStyle = 'rgba(0,0,0,0.05)';
          ctx.strokeRect(x * displaySize, y * displaySize, displaySize, displaySize);
        }
      });
    });
  }, [grid, isEditing, generatedData]);

  const saveToHistory = (newGrid: string[][]) => {
    const newHistory = history.slice(0, historyStep + 1);
    newHistory.push(JSON.parse(JSON.stringify(newGrid)));
    if (newHistory.length > 20) newHistory.shift();
    setHistory(newHistory);
    setHistoryStep(newHistory.length - 1);
  };

  const undo = () => {
    if (historyStep > 0) {
      const prevGrid = JSON.parse(JSON.stringify(history[historyStep - 1]));
      setGrid(prevGrid);
      setHistoryStep(historyStep - 1);
    }
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isEditing || !selectedDmc || !generatedData) return;
    const rect = canvasRef.current!.getBoundingClientRect();
    const scaleX = generatedData.meta.width / rect.width;
    const scaleY = generatedData.meta.height / rect.height;
    const x = Math.floor((e.clientX - rect.left) * scaleX);
    const y = Math.floor((e.clientY - rect.top) * scaleY);

    if (y >= 0 && y < grid.length && x >= 0 && x < grid[0].length) {
      const newGrid = [...grid];
      if (newGrid[y][x] !== selectedDmc) {
        newGrid[y] = [...newGrid[y]];
        newGrid[y][x] = selectedDmc;
        setGrid(newGrid);
        saveToHistory(newGrid);
      }
    }
  };

  const handleGenerate = useCallback(async () => {
    if (!selectedFile) return;
    setStatus('generating');
    try {
      const url = `/api/generate?num_colors=${numColors}&width_cm=${widthCm}&aida_count=${aidaCount}`;
      const formData = new FormData();
      formData.append('img', selectedFile);
      const res = await fetch(url, { method: 'POST', body: formData });
      const data: EmbroideryData = await res.json();
      setGeneratedData(data);
      setSelectedDmc(data.palette[0].dmc);
      initializeGridFromImage(data);
      setStatus('preview-ready');
    } catch (err) { setStatus('error'); setErrorMessage("Błąd generowania wzoru."); }
  }, [selectedFile, numColors, widthCm, aidaCount, initializeGridFromImage]);

  useEffect(() => {
    if (selectedFile) {
      const timer = setTimeout(handleGenerate, 800);
      return () => clearTimeout(timer);
    }
  }, [numColors, widthCm, aidaCount, handleGenerate, selectedFile]);

  const downloadAsPDF = () => {
    if (!generatedData || !grid.length) return;
    const doc = new jsPDF();
    const fileName = selectedFile ? selectedFile.name.split('.')[0] : "moj_wzor";
    
    doc.setFontSize(22);
    doc.text("Wzor Haftu", 105, 20, { align: 'center' });
    
    doc.setFontSize(12);
    doc.text(`Liczba sciegow: ${generatedData.meta.width} x ${generatedData.meta.height}`, 20, 50);
    doc.text(`Wymiary haftu: ${widthCm} cm x ${Math.round((generatedData.meta.height / generatedData.meta.width) * widthCm)} cm`, 20, 60);
    doc.text(`Kanwa (Aida): ${aidaCount} ct`, 20, 70);

    const source = isEditing ? canvasRef.current?.toDataURL() : generatedData.preview_png;
    if (source) {
      const pdfImgWidth = 170;
      const pdfImgHeight = (generatedData.meta.height * pdfImgWidth) / generatedData.meta.width;
      doc.addImage(source, 'PNG', 20, 80, pdfImgWidth, Math.min(pdfImgHeight, 180));
    }

    doc.addPage();
    doc.setFontSize(16);
    doc.text("Schemat graficzny", 20, 15);

    const margin = 15;
    const availableWidth = 180;
    const cellSize = availableWidth / generatedData.meta.width;

    let currentY = 25;
    let currentX = margin;

    grid.forEach((row, y) => {
      row.forEach((dmc, x) => {
        const colorData = generatedData.palette.find(p => p.dmc === dmc);
        if (colorData) {
          const posX = currentX + (x * cellSize);
          const posY = currentY + (y * cellSize);
          doc.setFillColor(colorData.rgb[0], colorData.rgb[1], colorData.rgb[2]);
          doc.rect(posX, posY, cellSize, cellSize, 'F');
          doc.setDrawColor(200);
          doc.setLineWidth(0.05);
          doc.rect(posX, posY, cellSize, cellSize, 'S');
          const brightness = (colorData.rgb[0] * 299 + colorData.rgb[1] * 587 + colorData.rgb[2] * 114) / 1000;
          doc.setTextColor(brightness > 128 ? 0 : 255);
          const fontSize = cellSize * 2.5; 
          doc.setFontSize(fontSize > 10 ? 10 : fontSize); 
          if (colorData.symbol) {
            doc.text(colorData.symbol, posX + (cellSize / 2), posY + (cellSize / 1.4), { align: 'center' });
          }
        }
      });
    });

    doc.addPage();
    doc.setTextColor(0);
    doc.setFontSize(18);
    doc.text("Legenda nici DMC", 20, 20);
    let yPos = 40;
    doc.setFontSize(10);
    doc.setFont("helvetica", "bold");
    doc.text("Kolor", 20, yPos);
    doc.text("Kod DMC", 40, yPos);
    doc.text("Symbol", 70, yPos);
    doc.text("Liczba", 150, yPos);
    doc.line(20, yPos + 2, 190, yPos + 2);
    yPos += 10;
    doc.setFont("helvetica", "normal");

    generatedData.palette.forEach((color) => {
      if (yPos > 275) { doc.addPage(); yPos = 20; }
      doc.setFillColor(color.rgb[0], color.rgb[1], color.rgb[2]);
      doc.rect(20, yPos - 4, 10, 5, 'F');
      doc.setDrawColor(200);
      doc.rect(20, yPos - 4, 10, 5, 'S');
      doc.text(color.dmc, 40, yPos);
      doc.text(color.symbol || "-", 70, yPos);
      const count = grid.flat().filter(x => x === color.dmc).length;
      doc.text(count.toString(), 150, yPos);
      yPos += 8;
    });

    doc.save(`${fileName}.pdf`);
  };

  const handleSaveToGallery = async () => {
    let token = localStorage.getItem('token');
    if (!token || !generatedData) return;
    setStatus('saving');
    
    try {
      let fileToUpload: File;
      if (isEditing && canvasRef.current) {
        const blob = await new Promise<Blob | null>(r => canvasRef.current?.toBlob(r, 'image/png'));
        if (!blob) throw new Error("Błąd zapisu obrazu.");
        fileToUpload = new File([blob], `wzor_edycja_${Date.now()}.png`, { type: 'image/png' });
      } else {
        const responseImg = await fetch(generatedData.preview_png);
        fileToUpload = new File([await responseImg.blob()], `wzor_${Date.now()}.png`, { type: 'image/png' });
      }

      const patternFullData = {
        meta: generatedData.meta,
        palette: generatedData.palette,
        grid: grid,
        params: { widthCm, aidaCount, numColors }
      };

      const performCreate = async (t: string) => fetch('/api/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${t}` },
        body: JSON.stringify({
          content_type: "embroidery",
          title: selectedFile?.name || "Mój Wzór",
          text: JSON.stringify(patternFullData), 
          is_public: false
        })
      });

      let res = await performCreate(token);
      if (res.status === 401) {
        const nt = await tryRefreshToken();
        if (nt) res = await performCreate(nt);
        else throw new Error("Sesja wygasła.");
      }

      if (!res.ok) throw new Error("Nie udało się utworzyć wpisu w galerii.");

      const content = await res.json();
      const formData = new FormData();
      formData.append('file', fileToUpload);

      const uploadRes = await fetch(`/api/upload/${content.id}`, { 
        method: 'POST', 
        headers: { 'Authorization': `Bearer ${token}` }, 
        body: formData 
      });

      if (!uploadRes.ok) throw new Error("Błąd podczas przesyłania zdjęcia do serwera.");

      setSuccessMessage("Zapisano pomyślnie cały projekt!");
      setStatus('success');
    } catch (err: any) { 
      console.error(err);
      setStatus('error'); 
      setErrorMessage(err.message || "Wystąpił nieoczekiwany błąd zapisu."); 
    }
  };

  return (
    <div className="generator-container">
      {status === 'error' && <div className="message-box error-box">{errorMessage}</div>}
      {status === 'success' && <div className="message-box success-box">{successMessage}</div>}

      <div className="upload-zone-dashed">
        <input type="file" id="file" className="hidden-input" accept="image/*"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if(f) { 
              setSelectedFile(f); setPreviewUrl(URL.createObjectURL(f)); 
              setGeneratedData(null); setIsEditing(false); 
            }
          }} 
        />
        <label htmlFor="file" className="file-upload-label">
          {selectedFile ? 'ZMIEŃ ZDJĘCIE' : 'WYBIERZ ZDJĘCIE Z DYSKU'}
        </label>
      </div>

      {previewUrl && (
        <div className="generator-workspace">
          <div className="workspace-left">
            <div className="card">
              <div className="card-header-row">
                <h3 className="card-subtitle">Podgląd projektu</h3>
                {generatedData && (
                  <button className={`btn-small ${isEditing ? 'active' : ''}`} onClick={() => setIsEditing(!isEditing)}>
                    {isEditing ? 'COFINJ DO ORYGINAŁU' : 'EDYTUJ RĘCZNIE'}
                  </button>
                )}
              </div>
              {isEditing && (
                <div className="edit-toolbar">
                  <button onClick={undo} disabled={historyStep <= 0} className="btn-undo">↩ Cofnij</button>
                  <span className="edit-hint">Aktywny kolor: <strong>{selectedDmc}</strong></span>
                </div>
              )}
              <div className="image-wrapper">
                {status === 'generating' && <div className="loader-overlay"><div className="spinner" /></div>}
                {!isEditing ? (
                  <img src={generatedData?.preview_png || previewUrl} alt="Podgląd wzoru" className="result-image" />
                ) : (
                  <canvas ref={canvasRef} onMouseDown={handleCanvasClick} className="edit-canvas" />
                )}
              </div>
            </div>
          </div>
          <div className="workspace-right">
            <div className="card sticky-card">
              <h3 className="card-subtitle">Parametry wzoru</h3>
              <div className="input-group">
                <label>Liczba kolorów DMC: {numColors}</label>
                <input type="range" min="2" max="100" value={numColors} onChange={(e) => setNumColors(Number(e.target.value))} />
              </div>
              <div className="input-group">
                <label>Szerokość haftu (cm):</label>
                <input type="number" min="5" max="150" value={widthCm} onChange={(e) => setWidthCm(Number(e.target.value))} />
              </div>
              <div className="input-group">
                <label>Gęstość kanwy (Aida):</label>
                <select value={aidaCount} onChange={(e) => setAidaCount(Number(e.target.value))}>
                  <option value={11}>11 ct (4.4 oczka/cm)</option>
                  <option value={14}>14 ct (5.4 oczka/cm)</option>
                  <option value={16}>16 ct (6.4 oczka/cm)</option>
                  <option value={18}>18 ct (7.0 oczek/cm)</option>
                </select>
              </div>
              {generatedData && (
                <div className="action-buttons-stack">
                  <button onClick={downloadAsPDF} className="btn-primary">POBIERZ PLIK PDF</button>
                  {isUserLoggedIn && (
                    <button onClick={handleSaveToGallery} disabled={status === 'saving'} className="btn-outline">
                      {status === 'saving' ? 'ZAPISYWANIE...' : 'ZAPISZ W GALERII'}
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {generatedData && (
        <section className="palette-results">
          <div className="card">
            <h3 className="card-subtitle">Lista nici DMC</h3>
            <div className="table-scroll">
              <table className="dmc-table">
                <thead>
                  <tr><th>Kolor</th><th>Kod DMC</th><th>Symbol</th><th>Liczba ściegów</th></tr>
                </thead>
                <tbody>
                  {generatedData.palette.map((c) => (
                    <tr key={c.dmc} className={selectedDmc === c.dmc ? 'selected-row' : ''} onClick={() => setSelectedDmc(c.dmc)}>
                      <td><div className="color-swatch" style={{ backgroundColor: `rgb(${c.rgb.join(',')})` }} /></td>
                      <td><strong>{c.dmc}</strong></td>
                      <td className="symbol-cell">{c.symbol}</td>
                      <td>{grid.flat().filter(x => x === c.dmc).length}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}