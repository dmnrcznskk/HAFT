'use client';

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<{ username: string; email: string } | null>(null);
  const router = useRouter();

  // 1. Pobieranie danych użytkownika z Proxy API
  const fetchUser = async () => {
    if (typeof window === 'undefined') return;
    const token = localStorage.getItem('token');
    
    if (!token) {
      setUser(null);
      return;
    }

    try {
      const response = await fetch('/api/user', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        localStorage.removeItem('token');
        setUser(null);
      }
    } catch (error) {
      console.error("Błąd autoryzacji:", error);
      setUser(null);
    }
  };

  useEffect(() => {
    fetchUser();
    // Nasłuchiwanie na zmiany (np. po pomyślnym zalogowaniu)
    window.addEventListener('storage', fetchUser);
    return () => window.removeEventListener('storage', fetchUser);
  }, []);

  const closeMenu = () => setOpen(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    closeMenu();
    router.push('/main-page');
    window.location.reload();
  };

  return (
    <html lang="pl">
      <body>
        <header>
          <nav>
            <div className="menu">
              <Link href="/main-page" className="logo" onClick={closeMenu}>Needle Nest</Link>
              <div className="passages">
                <Link href="/generator-page" className="hover:underline">Generator</Link>
                <Link href="/gallery-page" className="hover:underline">Galeria</Link>
              </div>
            </div>

            <div className="search-bar">
              <input type="text" placeholder="Szukaj..." className="search-bar-inside" />
            </div>

            {/* PUNKT 1 i 2: Dynamiczna zamiana "Zaloguj" na link z nazwą użytkownika */}
            <div className="log-in">
              {user ? (
                <Link 
                  href="/dashboard-page" 
                  className="hover:underline font-bold text-white"
                  onClick={closeMenu}
                >
                  {user.username.toUpperCase()}
                </Link>
              ) : (
                <Link href="/login-page" className="hover:underline">
                  Zaloguj
                </Link>
              )}
            </div>

            <div className="hamburger">
              <button onClick={() => setOpen(!open)} aria-label="Menu">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  {open ? (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                  )}
                </svg>
              </button>
            </div>
          </nav>

          {/* Menu Mobilne */}
          <div className={`mobile_menu ${open ? 'max-h-[500px] opacity-100 mt-4' : 'max-h-0 opacity-0 overflow-hidden'} transition-all duration-300`}>
            <div className="search-bar-drop">
              <Link href="/generator-page" className="py-2" onClick={closeMenu}>Generator</Link>
              <Link href="/gallery-page" className="py-2" onClick={closeMenu}>Galeria</Link>
              
              <div className="log-in-inside border-t pt-2 mt-2">
                {user ? (
                  <>
                    {/* Nazwa użytkownika jako link do dashboardu w wersji mobilnej */}
                    <Link href="/dashboard-page" className="py-2 font-bold text-blue-600 block" onClick={closeMenu}>
                      {user.username} (Profil)
                    </Link>
                    <button onClick={handleLogout} className="text-red-500 py-2">Wyloguj się</button>
                  </>
                ) : (
                  <Link href="/login-page" className="font-bold block" onClick={closeMenu}>Zaloguj</Link>
                )}
              </div>
            </div>
          </div>
        </header>

        <main>{children}</main>

        <footer className="px-6 py-4 flex justify-center gap-5">
          <p className="text-sm">Needle Nest 2025</p>
        </footer>
      </body>
    </html>
  );
}