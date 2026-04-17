import React, { createContext, useContext, useEffect, useState } from "react";
import {
  User,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
} from "firebase/auth";
import { auth } from "../lib/firebase";


type AuthContextType = {
  user: User | null;
  loading: boolean;
  isGuest: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  continueAsGuest: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      console.log("[AuthContext] onAuthStateChanged, user:", firebaseUser);
      setUser(firebaseUser);
      setLoading(false);
      // If a real user logs in, exit guest mode
      if (firebaseUser) setIsGuest(false);
    });
    return unsubscribe;
  }, []);

  const login = async (email: string, password: string) => {
    const userCredential = await signInWithEmailAndPassword(
      auth,
      email.trim(),
      password
    );
    setUser(userCredential.user);
    setIsGuest(false);
    setLoading(false);
  };

  const signup = async (email: string, password: string) => {
    const userCredential = await createUserWithEmailAndPassword(
      auth,
      email.trim(),
      password
    );
    setUser(userCredential.user);
    setIsGuest(false);
    setLoading(false);
  };

  const logout = async () => {
    console.log("[AuthContext] Logging out...");
    try {
      await signOut(auth);
      console.log("[AuthContext] signOut success");
      // Clear local state immediately; onAuthStateChanged should also confirm this.
      setUser(null);
      setIsGuest(false);
    } catch (e) {
      console.log("[AuthContext] signOut error:", e);
      throw e;
    }
    // After signOut, onAuthStateChanged should fire and set user to null
  };

  // Guest mode: set guest flag, clear user
  const continueAsGuest = () => {
    setUser(null);
    setIsGuest(true);
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{ user, loading, isGuest, login, signup, logout, continueAsGuest }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}