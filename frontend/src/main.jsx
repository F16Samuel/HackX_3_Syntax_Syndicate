import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import {BrowserRouter} from 'react-router-dom';
import { AuthProvider } from './context/AuthContext'; // <-- 1. Import the AuthProvider

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <AuthProvider> {/* <-- 2. Wrap your App component */}
      <App />
    </AuthProvider>
  </BrowserRouter>
)

