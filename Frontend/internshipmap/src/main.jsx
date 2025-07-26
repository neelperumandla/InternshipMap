import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import ResumeUpload from './Upload.jsx'
import Login from './Login.jsx'
import Register from './Register.jsx'
import { Routes, Route } from 'react-router-dom';
import Index from './Index.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Index />
  </StrictMode>,
)
