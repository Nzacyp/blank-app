import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import ConsultationForm from './components/ConsultationForm';
import HistoryPage from './components/HistoryPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  if (!isLoggedIn) {
    return (
      <div>
        <LoginForm onLogin={() => setIsLoggedIn(true)} />
        <RegisterForm />
      </div>
    );
  }

  return (
    <div>
      <button onClick={() => {
        localStorage.removeItem('token');
        setIsLoggedIn(false);
      }}>Logout</button>
      <ConsultationForm />
      <HistoryPage />
    </div>
  );
}

export default App;
