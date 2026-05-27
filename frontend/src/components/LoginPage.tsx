import { useState, type FormEvent } from 'react';
import { login, register } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import { IconSpark } from './Icons';

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
      await onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-art">
        <div className="art-head">
          <div className="logo">
            <IconSpark width={20} height={20} />
          </div>
          <strong>Triage</strong>
        </div>

        <div className="art-body">
          <h1>
            <span className="gradient-text">AI-powered</span> support triage
            that actually scales.
          </h1>
          <p>
            Submit a ticket and watch a fine-tuned agent classify, route, and
            draft a reply in seconds. Your humans focus on what matters.
          </p>

          <div className="stats">
            <div>
              <strong>~4.2s</strong>
              <span>median first response</span>
            </div>
            <div>
              <strong>92%</strong>
              <span>auto-resolution on FAQ</span>
            </div>
            <div>
              <strong>24/7</strong>
              <span>always-on agent</span>
            </div>
          </div>
        </div>
      </div>

      <div className="login-form-wrap">
        <form className="login-form" onSubmit={handleSubmit}>
          <h2>{isRegister ? 'Create account' : 'Welcome back'}</h2>
          <p className="sub">
            {isRegister
              ? 'Get started with your support workspace.'
              : 'Sign in to access your tickets.'}
          </p>

          {isRegister && (
            <div className="field-group">
              <label>Full name</label>
              <input
                className="input"
                type="text"
                placeholder="Jane Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
          )}
          <div className="field-group">
            <label>Email</label>
            <input
              className="input"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="field-group">
            <label>Password</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={4}
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button
            className="btn btn-primary"
            type="submit"
            disabled={loading}
            style={{ marginTop: 4 }}
          >
            {loading
              ? 'Please wait…'
              : isRegister
                ? 'Create account'
                : 'Sign in'}
          </button>

          <p className="switch">
            {isRegister
              ? 'Already have an account?'
              : "Don't have an account?"}{' '}
            <button type="button" onClick={() => setIsRegister(!isRegister)}>
              {isRegister ? 'Sign in' : 'Create one'}
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}
