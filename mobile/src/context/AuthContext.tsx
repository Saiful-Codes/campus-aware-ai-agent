import React, { createContext, useContext, useEffect, useState } from "react";
import {
  deleteUser,
  User,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
} from "firebase/auth";
import { doc, serverTimestamp, setDoc, updateDoc } from "firebase/firestore";
import { auth, db } from "../lib/firebase";
import { clearGuestChatStorage } from "../lib/guestChatStorage";

export type SignupExtraUserData = {
  fullName: string;
  role: "student" | "staff";
  campus?: string;
  course?: string;
  yearOfStudy?: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  isGuest: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, extraUserData: SignupExtraUserData) => Promise<void>;
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

    try {
      await updateDoc(doc(db, "users", userCredential.user.uid), {
        lastLoginAt: serverTimestamp(),
      });
    } catch (e) {
      console.log("[AuthContext] Could not update lastLoginAt", e);
    }

    setUser(userCredential.user);
    setIsGuest(false);
    setLoading(false);
  };

  const signup = async (email: string, password: string, extraUserData: SignupExtraUserData) => {
    const normalizedEmail = email.trim();
    const normalizedName = extraUserData.fullName.trim();

    if (!normalizedName) {
      throw new Error("Full name is required.");
    }

    const userCredential = await createUserWithEmailAndPassword(
      auth,
      normalizedEmail,
      password
    );

    try {
      await setDoc(doc(db, "users", userCredential.user.uid), {
        fullName: normalizedName,
        email: normalizedEmail,
        role: extraUserData.role,
        campus: extraUserData.campus?.trim() ?? "",
        course: extraUserData.course?.trim() ?? "",
        yearOfStudy: extraUserData.yearOfStudy?.trim() ?? "",
        createdAt: serverTimestamp(),
        lastLoginAt: serverTimestamp(),
        preferences: {
          theme: "light",
          largeText: false,
        },
        usage: {
          totalChats: 0,
        },
      });
    } catch (e) {
      try {
        await deleteUser(userCredential.user);
      } catch (deleteError) {
        console.log("[AuthContext] rollback deleteUser failed", deleteError);
      }
      throw new Error("Account created but profile setup failed. Please try signing up again.");
    }

    setUser(userCredential.user);
    setIsGuest(false);
    setLoading(false);
  };

  const logout = async () => {
    console.log("[AuthContext] Logging out...");
    try {
      await signOut(auth);
      console.log("[AuthContext] signOut success");
      // Purge any leftover guest chat data so the next guest starts clean.
      await clearGuestChatStorage();
      // Clear local state immediately; onAuthStateChanged should also confirm this.
      setUser(null);
      setIsGuest(false);
    } catch (e) {
      console.log("[AuthContext] signOut error:", e);
      throw e;
    }
    // After signOut, onAuthStateChanged should fire and set user to null
  };

  // Guest mode: set guest flag, clear user.
  // Purge any persisted guest chat data first so a fresh guest can never
  // inherit a previous guest session's conversations (privacy). Guest chat
  // history is kept in memory only for the lifetime of the session.
  const continueAsGuest = () => {
    void clearGuestChatStorage();
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