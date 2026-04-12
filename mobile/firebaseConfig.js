// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyB4pdllgZ15BONtUMNlm4SXKdauq-9wwrk",
  authDomain: "campus-ai-agent.firebaseapp.com",
  projectId: "campus-ai-agent",
  storageBucket: "campus-ai-agent.firebasestorage.app",
  messagingSenderId: "316968821683",
  appId: "1:316968821683:web:238fd95320e2d1937ba1c6"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export default app;