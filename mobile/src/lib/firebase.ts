import { initializeApp, getApps, getApp } from "firebase/app";
import { initializeAuth, getAuth, getReactNativePersistence, browserLocalPersistence } from "firebase/auth";
import ReactNativeAsyncStorage from "@react-native-async-storage/async-storage";
import { getFirestore } from "firebase/firestore";
import { Platform } from "react-native";

const firebaseConfig = {
  apiKey: "AIzaSyClGXJOVV5Cwu-vZbs7ZWpqbeT-28MM00c",
  authDomain: "campus-ai-agent.firebaseapp.com",
  projectId: "campus-ai-agent",
  storageBucket: "campus-ai-agent.firebasestorage.app",
  messagingSenderId: "316968821683",
  appId: "1:316968821683:web:238fd95320e2d1937ba1c6"
};

const isFirstInit = getApps().length === 0;
const app = isFirstInit ? initializeApp(firebaseConfig) : getApp();

export const auth = isFirstInit
  ? initializeAuth(app, {
      persistence: Platform.OS === "web"
        ? browserLocalPersistence
        : getReactNativePersistence(ReactNativeAsyncStorage),
    })
  : getAuth(app);

export const db = getFirestore(app);