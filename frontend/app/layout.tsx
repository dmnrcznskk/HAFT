'use client';

import { useState, useEffect } from "react";
import NextLink from "next/link";
import { useRouter } from "next/navigation";
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<{ username: string; email: string } | null>(null);
  const router = useRouter();

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

  const displayName = user?.username;

  return (
    <html lang="pl">
      <body>
        <header>
          <nav>
            <div className="menu">
              <NextLink href="/main-page" className="logo" onClick={closeMenu}>Needle Nest</NextLink>
              <div className="passages">
                <NextLink href="/generator-page">Generator</NextLink>
                <NextLink href="/gallery-page">Galeria</NextLink>
              </div>
            </div>

            <div className="search-bar">
              <input type="text" placeholder="Szukaj..." className="search-bar-inside" />
            </div>

            <div className="log-in">
              {user ? (
                <NextLink 
                  href="/dashboard-page" 
                  className="font-bold text-white uppercase"
                  onClick={closeMenu}
                >

                  {displayName}
                </NextLink>
              ) : (
                <NextLink href="/login-page">
                  Zaloguj
                </NextLink>
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

          <div className={`mobile_menu ${open ? 'max-h-[500px] opacity-100 mt-4' : 'max-h-0 opacity-0 overflow-hidden'} transition-all duration-300`}>
            <div className="search-bar-drop">
              <NextLink href="/generator-page" className="py-2" onClick={closeMenu}>Generator</NextLink>
              <NextLink href="/gallery-page" className="py-2" onClick={closeMenu}>Galeria</NextLink>
              
              <div className="log-in-inside pt-2 mt-2">
                {user ? (
                  <>
                    <NextLink href="/dashboard-page" className="name-of-user" onClick={closeMenu}>
                      {displayName}
                    </NextLink>
                  </>
                ) : (
                  <NextLink href="/login-page" className="name-of-user" onClick={closeMenu}>Zaloguj</NextLink>
                )}
              </div>
            </div>
          </div>
        </header>

        <main>{children}</main>

        <footer>
          <p className="text-sm">Needle Nest 2025</p>
        </footer>
      </body>
    </html>
  );
}