'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import './dashboard-page.css';

const DashboardPage = () => {
  const [userData, setUserData] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login-page');
      return;
    }

    fetch('/api/user', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setUserData(data))
    .catch(() => router.push('/login-page'));
  }, [router]);

  if (!userData) return <p className="loading-message">Ładowanie...</p>;

  const displayName = userData.username || 'Użytkowniku';

  return (
    <div className="dashboard-wrapper">
      <h1 className="welcome-header">Witaj w Twoim panelu, {displayName}!</h1>
      
      <div className="info-box">
        <p><strong>Email:</strong> {userData.email}</p>
      </div>
      
      <button 
        onClick={() => { 
          localStorage.removeItem('token'); 
          router.push('/login-page');
        }}
        className="btn-logout"
      >
        Wyloguj się
      </button>
    </div>
  );
};

export default DashboardPage;