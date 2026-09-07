import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { HelmetProvider } from "react-helmet-async";
import App from "./App";
import "./index.css";

const client = new QueryClient({ defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } } });
ReactDOM.createRoot(document.getElementById("root")).render(<React.StrictMode><HelmetProvider><QueryClientProvider client={client}><App /></QueryClientProvider></HelmetProvider></React.StrictMode>);
