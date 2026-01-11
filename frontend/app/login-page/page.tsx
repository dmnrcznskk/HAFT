'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import './login-page.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        window.location.href = '/dashboard-page';
      } else {
        if (Array.isArray(data.detail)) {
          setMessage(data.detail.map((d: any) => d.msg).join(', '));
        } else {
          setMessage(data.detail || 'Nieprawidłowe dane logowania');
        }
      }
    } catch (error) {
      setMessage('Wystąpił błąd połączenia z serwerem.');
    }
  };

  return (
    <div className="login-container">
      <h1>Zaloguj się</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <input 
          type="text" 
          placeholder="Nazwa użytkownika" 
          value={username}
          onChange={(e) => setUsername(e.target.value)} 
          required
          className="login-input"
        />
        <input 
          type="password" 
          placeholder="Hasło" 
          value={password}
          onChange={(e) => setPassword(e.target.value)} 
          required
          className="login-input"
        />
        <button type="submit" className="login-button">
          ZALOGUJ
        </button>
      </form>
      
      <p className="signup-link">
        Nie masz konta? <Link href="/signup-page">Zarejestruj się teraz!</Link>
      </p>
      
      {message && <div className="error-message">{message}</div>}
    </div>
  );
};

export default Login;