'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import './signup-page.css';

const SignupPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    setIsError(false);

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Konto utworzone pomyślnie! Przekierowanie...');
        setTimeout(() => router.push('/login-page'), 2000);
      } else {
        setIsError(true);
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            setMessage(data.detail.map((err: any) => err.msg).join(', '));
          } else {
            setMessage(data.detail);
          }
        } else {
          setMessage('Wystąpił nieoczekiwany błąd.');
        }
      }
    } catch (err) {
      setIsError(true);
      setMessage('Błąd połączenia z serwerem.');
    }
  };

  return (
    <div className="login-container">
      <h1>Rejestracja</h1>
      <form onSubmit={handleRegister} className="login-form">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          placeholder="twoj@email.pl"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="login-input"
        />

        <label htmlFor="password">Hasło</label>
        <input
          id="password"
          type="password"
          placeholder="Min. 8 znaków"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="login-input"
        />

        <button type="submit" className="login-button">
          ZAREJESTRUJ SIĘ
        </button>
      </form>

      {message && (
        <div className={isError ? "error-message" : "success-message"}>
          {message}
        </div>
      )}
    </div>
  );
};

export default SignupPage;