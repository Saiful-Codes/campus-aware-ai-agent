import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, setPersistence, browserSessionPersistence } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyB4pdllgZ15BONtUMNlm4SXKdauq-9wwrk",
  authDomain: "campus-ai-agent.firebaseapp.com",
  projectId: "campus-ai-agent",
  storageBucket: "campus-ai-agent.firebasestorage.app",
  messagingSenderId: "316968821683",
  appId: "1:316968821683:web:238fd95320e2d1937ba1c6"
};

const app = getApps().length ? getApp() : initializeApp(firebaseConfig);

export const auth = getAuth(app);

// Ensure session is not restored after logout on web
if (typeof window !== "undefined") {
  setPersistence(auth, browserSessionPersistence).catch((e) => {
    console.log("[firebase] setPersistence error:", e);
  });
}
export const db = getFirestore(app);