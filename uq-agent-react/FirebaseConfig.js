// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from 'firebase/firestore';
import { getAuth, signInAnonymously } from 'firebase/auth';
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDdMkr7OW0rFj9SYTgdiVstv4fzEOQA7uE",
  authDomain: "uq-agent.firebaseapp.com",
  projectId: "uq-agent",
  storageBucket: "uq-agent.firebasestorage.app",
  messagingSenderId: "906602782530",
  appId: "1:906602782530:web:f165112d2f218844a432db",
  measurementId: "G-K46C0C6P0Y"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);

// Initialize authentication
const initAuth = async () => {
  try {
    await signInAnonymously(auth);
    console.log("Anonymous authentication successful");
    return auth.currentUser;
  } catch (error) {
    console.error("Authentication error:", error);
    throw error;
  }
};

export { db, auth, initAuth };