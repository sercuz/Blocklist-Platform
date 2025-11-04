import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Components
import Navbar from './components/Navbar';
import Login from './components/Login';
import BlockingForm from './components/BlockingForm';
import BlocklistTable from './components/BlocklistTable';
import LogsView from './components/LogsView';
import ApiKeyManager from './components/ApiKeyManager';
import ApiLogViewer from './components/ApiLogViewer';

// Private Route component
const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Admin Route component
const AdminRoute = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!user || !user.is_staff) {
    return <Navigate to="/" />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <div className="container mt-4">
            <Routes>
              <Route path="/login" element={<Login />} />
              
              <Route path="/" element={
                <PrivateRoute>
                  <BlockingForm />
                </PrivateRoute>
              } />
              
              <Route path="/blocklist" element={
                <PrivateRoute>
                  <BlocklistTable />
                </PrivateRoute>
              } />
              
              <Route path="/logs" element={
                <PrivateRoute>
                  <LogsView />
                </PrivateRoute>
              } />
              
              <Route path="/api-keys" element={
                <AdminRoute>
                  <ApiKeyManager />
                </AdminRoute>
              } />
              
              <Route path="/api-logs" element={
                <AdminRoute>
                  <ApiLogViewer />
                </AdminRoute>
              } />
              
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
