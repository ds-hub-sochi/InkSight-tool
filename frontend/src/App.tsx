import React from 'react';
import { AuthProvider, useAuth } from './components/AuthProvider';
import { LoginPage } from './components/LoginPage';
import { ProtectedApp } from './components/ProtectedApp';

const AppContent: React.FC = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return <ProtectedApp />;
};

function App() {

  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;