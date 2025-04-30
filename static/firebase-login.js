// main.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCFpdiPZUZMZ28O87FxeBZKTU9QxDxALIg",
  authDomain: "assignment3-3d41a.firebaseapp.com",
  projectId: "assignment3-3d41a",
  storageBucket: "assignment3-3d41a.firebasestorage.app",
  messagingSenderId: "191609676404",
  appId: "1:191609676404:web:23b8caa7eef325b91f2721",
  measurementId: "G-0DX890M3H5",
};
window.addEventListener("load", function () {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  updateUI(document.cookie);
  console.log("Firebase App Initialized");

  document.getElementById("sign-up")?.addEventListener("click", function () {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        console.log("User Created:", user);

        user.getIdToken().then((token) => {
          document.cookie = `token=${token}; path=/; SameSite=Strict`;
          console.log("Signup Token Set:", document.cookie);
          window.location = "/";
        });
      })
      .catch((error) => {
        console.error("Signup Error:", error.code, error.message);
      });
  });

  document.getElementById("login")?.addEventListener("click", function () {
    console.log("clicking");
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        console.log("User Logged In:", user);

        user.getIdToken().then((token) => {
          document.cookie = `token=${token}; path=/; SameSite=Strict`;
          console.log("Login Token Set:", document.cookie);
          window.location = "/";
        });
      })
      .catch((error) => {
        console.error("Login Error:", error.code, error.message);
      });
  });
  console.log("near sign out");
  document.getElementById("sign-out")?.addEventListener("click", function () {
    signOut(auth)
      .then(() => {
        document.cookie = "token=; path=/; SameSite=Strict";
        console.log("User Signed Out");
        window.location = "/";
      })
      .catch((error) => {
        console.error("Logout Error:", error.code, error.message);
      });
  });
});

function updateUI(cookie) {
  const token = parseCookieToken(cookie);
  if (token.length > 0) {
    const loginBox = document.getElementById("login-box");
    const signOut = document.getElementById("sign-out");
    if (loginBox) loginBox.hidden = true;
    if (signOut) signOut.hidden = false;
  } else {
    const loginBox = document.getElementById("login-box");
    const signOut = document.getElementById("sign-out");
    if (loginBox) loginBox.hidden = false;
    if (signOut) signOut.hidden = true;
  }
}

function parseCookieToken(cookie) {
  const strings = cookie.split(";");
  for (let i = 0; i < strings.length; i++) {
    const temp = strings[i].split("=");
    if (temp[0].trim() === "token") {
      return temp[1];
    }
  }
  return "";
}
