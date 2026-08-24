import React, { useState } from "react";
import { ShoppingCart, Loader2 } from "lucide-react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { login, register } from "./api/auth";

function AuthScreen() {
  const { signIn } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");

    if (!email || !password) {
      setErrorMsg("Please fill in all fields.");
      return;
    }

    if (!isLoginMode && password !== confirmPassword) {
      setErrorMsg("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      if (isLoginMode) {
        const { access_token } = await login(email, password);
        signIn(access_token);
      } else {
        await register(email, password);
        // Automatically log in after registration
        const { access_token } = await login(email, password);
        signIn(access_token);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Authentication failed";
      setErrorMsg(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <ShoppingCart size={48} color="var(--primary)" style={{ margin: "0 auto 1rem" }} />
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-main)" }}>
            Voice Shopping
          </h1>
          <p style={{ color: "var(--text-muted)", marginTop: "0.25rem" }}>
            {isLoginMode ? "Welcome back to your list" : "Create an account to start"}
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label className="input-label">Email</label>
            <input
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="input-label">Password</label>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {!isLoginMode && (
            <div>
              <label className="input-label">Confirm Password</label>
              <input
                type="password"
                className="input-field"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
          )}

          {errorMsg && <div className="error-text">{errorMsg}</div>}

          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? <Loader2 className="spinner" size={20} /> : (isLoginMode ? "Sign In" : "Create Account")}
          </button>
        </form>

        <div className="auth-switch">
          {isLoginMode ? "Don't have an account? " : "Already have an account? "}
          <button type="button" onClick={() => setIsLoginMode(!isLoginMode)}>
            {isLoginMode ? "Sign Up" : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}

import { Dashboard } from "./pages/Dashboard";

function MainApp() {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <Loader2 className="spinner" size={40} color="var(--primary)" />
      </div>
    );
  }

  return token ? <Dashboard /> : <AuthScreen />;
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
