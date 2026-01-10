'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

const Dashboard = () => {
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

  if (!userData) return <p>Ładowanie...</p>;

  return (
    <div className="p-10">
      <h1>Witaj w Twoim panelu, {userData.username}!</h1>
      <div className="mt-4 p-4 border rounded">
        <p><strong>Email:</strong> {userData.email}</p>
        <p><strong>ID Użytkownika:</strong> {userData.id}</p>
      </div>
      <button 
        onClick={() => { localStorage.removeItem('token'); window.location.reload(); }}
        className="mt-4 bg-red-500 text-white p-2 rounded"
      >
        Wyloguj się
      </button>
    </div>
  );
};

export default Dashboard;