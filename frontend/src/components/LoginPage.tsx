import { useState, type FormEvent } from 'react';
import { login, register } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export function LoginPage() {
  const { login: onLogin } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register({ email, password, full_name: fullName });
      } else {
        await login({ email, password });
      }
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Support Triager</h1>
        <h2>{isRegister ? 'Register' : 'Log in'}</h2>

        {isRegister && (
          <input
            type="text"
            placeholder="Full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={4}
        />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? 'Please wait...' : isRegister ? 'Register' : 'Log in'}
        </button>

        <p className="switch">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button type="button" className="link" onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? 'Log in' : 'Register'}
          </button>
        </p>
      </form>
    </div>
  );
}
