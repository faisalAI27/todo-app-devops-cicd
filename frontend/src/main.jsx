import { createElement, StrictMode } from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  createElement(StrictMode, null, createElement(App)),
);
