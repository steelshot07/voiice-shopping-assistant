import React, { createContext, useContext, useState, useEffect } from "react";

interface AuthContextData {
  token: string | null;
  isLoading: boolean;
  signIn: (token: string) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Generate a unique ID for this specific tab
    const myTabId = Math.random().toString(36).substring(2);
    // Claim the active session globally
    localStorage.setItem("active_tab_id", myTabId);

    const loadToken = () => {
      const storedToken = sessionStorage.getItem("auth_token");
      if (storedToken) {
        setToken(storedToken);
      }
      setIsLoading(false);
    };
    loadToken();

    // Check on every interaction if another tab has claimed the session
    const checkActiveTab = () => {
      const currentActiveTab = localStorage.getItem("active_tab_id");
      if (currentActiveTab && currentActiveTab !== myTabId) {
        // Another tab has opened, kill this tab's session
        sessionStorage.removeItem("auth_token");
        setToken(null);
      }
    };

    // Listen to clicks to instantly kick them out if they try to interact
    // Use capture phase (true) to intercept the click before it does anything else
    document.addEventListener("click", checkActiveTab, true);
    
    // Also listen to storage events to kick them out instantly when the other tab opens
    window.addEventListener("storage", checkActiveTab);

    return () => {
      document.removeEventListener("click", checkActiveTab, true);
      window.removeEventListener("storage", checkActiveTab);
    };
  }, []);

  const signIn = (newToken: string) => {
    sessionStorage.setItem("auth_token", newToken);
    setToken(newToken);
  };

  const signOut = () => {
    sessionStorage.removeItem("auth_token");
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, isLoading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
