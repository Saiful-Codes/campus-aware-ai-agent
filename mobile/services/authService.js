import { auth } from "../firebaseConfig";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "firebase/auth";


// SIGN UP
export const signUp = async (email, password) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(
      auth,
      email,
      password
    );

    const user = userCredential.user;
    console.log("User signed up:", user);

    return user;
  } catch (error) {
    console.error("Signup error:", error.code, error.message);
    throw new Error(error.message);
  }
};


// SIGN IN
export const signIn = async (email, password) => {
  try {
    const userCredential = await signInWithEmailAndPassword(
      auth,
      email,
      password
    );

    const user = userCredential.user;
    console.log("User logged in:", user);

    return user;
  } catch (error) {
    console.error("Login error:", error.code, error.message);
    throw new Error(error.message);
  }
};


// LOG OUT
export const logOut = async () => {
  try {
    await signOut(auth);
    console.log("User logged out");
  } catch (error) {
    console.error("Logout error:", error.code, error.message);
    throw new Error(error.message);
  }
};