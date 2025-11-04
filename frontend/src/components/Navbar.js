import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">
          <strong>Blocklist Platform</strong>
        </Link>
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav" 
          aria-controls="navbarNav" 
          aria-expanded="false" 
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <div className="d-flex w-100 justify-content-between align-items-center">
            <ul className="navbar-nav d-flex flex-row">
              <li className="nav-item px-2">
                <Link 
                  to="/" 
                  className={`nav-link ${location.pathname === '/' ? 'active fw-bold' : ''}`}
                >
                  Block/Unblock IOCs
                </Link>
              </li>
              <li className="nav-item px-2">
                <Link 
                  to="/blocklist" 
                  className={`nav-link ${location.pathname === '/blocklist' ? 'active fw-bold' : ''}`}
                >
                  Blocklist Table
                </Link>
              </li>
              <li className="nav-item px-2">
                <Link 
                  to="/logs" 
                  className={`nav-link ${location.pathname === '/logs' ? 'active fw-bold' : ''}`}
                >
                  Logs
                </Link>
              </li>
              {user && user.is_staff && (
                <>
                  <li className="nav-item px-2">
                    <Link 
                      to="/api-keys" 
                      className={`nav-link ${location.pathname === '/api-keys' ? 'active fw-bold' : ''}`}
                    >
                      API Keys
                    </Link>
                  </li>
                  <li className="nav-item px-2">
                    <Link 
                      to="/api-logs" 
                      className={`nav-link ${location.pathname === '/api-logs' ? 'active fw-bold' : ''}`}
                    >
                      API Logs
                    </Link>
                  </li>
                </>
              )}
            </ul>
            <div className="d-flex align-items-center">
              {user && (
                <span className="text-light me-3">
                  {user.username.replace('admin', '')}
                  {user.is_staff && <span className="badge bg-warning text-dark ms-2">Admin</span>}
                </span>
              )}
              <button 
                className="btn btn-outline-light" 
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
