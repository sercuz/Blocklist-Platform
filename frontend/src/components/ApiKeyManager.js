import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getApiKeys, createApiKey, deleteApiKey, regenerateApiKey } from '../services/api';

const ApiKeyManager = () => {
  const { user } = useAuth();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [readOnly, setReadOnly] = useState(true);
  const [successMessage, setSuccessMessage] = useState('');

  console.log('ApiKeyManager user:', user); // Debug output

  // Fetch API keys on component mount
  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      setLoading(true);
      const keys = await getApiKeys();
      setApiKeys(keys);
      setError('');
    } catch (err) {
      console.error('Error fetching API keys:', err);
      setError('Failed to load API keys. ' + (err.message || ''));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApiKey = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('API key name is required');
      return;
    }

    try {
      setLoading(true);
      const newKey = await createApiKey(name, readOnly);
      setApiKeys([...apiKeys, newKey]);
      setName('');
      setSuccessMessage('API key created successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error creating API key:', err);
      setError('Failed to create API key. ' + (err.message || ''));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteApiKey = async (id) => {
    if (!window.confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    try {
      setLoading(true);
      await deleteApiKey(id);
      setApiKeys(apiKeys.filter(key => key.id !== id));
      setSuccessMessage('API key deleted successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error deleting API key:', err);
      setError('Failed to delete API key. ' + (err.message || ''));
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateApiKey = async (id) => {
    if (!window.confirm('Are you sure you want to regenerate this API key? The old key will no longer work.')) {
      return;
    }

    try {
      setLoading(true);
      const updatedKey = await regenerateApiKey(id);
      setApiKeys(apiKeys.map(key => key.id === id ? updatedKey : key));
      setSuccessMessage('API key regenerated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error regenerating API key:', err);
      setError('Failed to regenerate API key. ' + (err.message || ''));
    } finally {
      setLoading(false);
    }
  };

  // Only show this component to admin users
  if (!user || !user.is_staff) {
    return <div className="container mt-4">
      <div className="alert alert-warning">Only administrators can manage API keys.</div>
    </div>;
  }

  return (
    <div className="container mt-4">
      <h2>API Key Management</h2>
      
      {error && <div className="alert alert-danger">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}
      
      <div className="card mb-4">
        <div className="card-header">
          <h4>Create New API Key</h4>
        </div>
        <div className="card-body">
          <form onSubmit={handleCreateApiKey}>
            <div className="mb-3">
              <label htmlFor="apiKeyName" className="form-label">API Key Name</label>
              <input 
                type="text" 
                className="form-control" 
                id="apiKeyName" 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
                placeholder="Enter a descriptive name for this API key"
                required
              />
            </div>
            
            <div className="mb-3 form-check">
              <input 
                type="checkbox" 
                className="form-check-input" 
                id="readOnlyCheck" 
                checked={readOnly} 
                onChange={(e) => setReadOnly(e.target.checked)} 
              />
              <label className="form-check-label" htmlFor="readOnlyCheck">
                Read-only (can only view data, not modify it)
              </label>
            </div>
            
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create API Key'}
            </button>
          </form>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h4>Your API Keys</h4>
        </div>
        <div className="card-body">
          {loading && <p>Loading API keys...</p>}
          
          {!loading && apiKeys.length === 0 && (
            <p>You don't have any API keys yet. Create one using the form above.</p>
          )}
          
          {!loading && apiKeys.length > 0 && (
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Key</th>
                    <th>Type</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {apiKeys.map(key => (
                    <tr key={key.id}>
                      <td>{key.name}</td>
                      <td>
                        <code className="user-select-all">{key.key}</code>
                      </td>
                      <td>
                        {key.read_only ? (
                          <span className="badge bg-info">Read-only</span>
                        ) : (
                          <span className="badge bg-warning">Full Access</span>
                        )}
                      </td>
                      <td>{new Date(key.created_at).toLocaleString()}</td>
                      <td>
                        <button 
                          className="btn btn-sm btn-outline-secondary me-2" 
                          onClick={() => handleRegenerateApiKey(key.id)}
                          disabled={loading}
                        >
                          Regenerate
                        </button>
                        <button 
                          className="btn btn-sm btn-outline-danger" 
                          onClick={() => handleDeleteApiKey(key.id)}
                          disabled={loading}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
      
      <div className="card mt-4">
        <div className="card-header">
          <h4>How to Use API Keys</h4>
        </div>
        <div className="card-body">
          <p>Include your API key in the <code>Authorization</code> header of your HTTP requests:</p>
          <pre className="bg-light p-3 user-select-all">
            Authorization: ApiKey your-api-key-here
          </pre>
          
          <h5 className="mt-3">Access Levels</h5>
          <ul>
            <li><strong>Read-only API Keys:</strong> Can only access GET endpoints (view data)</li>
            <li><strong>Full Access API Keys:</strong> Can access all endpoints (view and modify data)</li>
          </ul>
          
          <h5 className="mt-3">Example Usage</h5>
          <pre className="bg-light p-3">
            {`// JavaScript example
fetch('http://localhost:8000/api/blocklist/', {
  headers: {
    'Authorization': 'ApiKey your-api-key-here'
  }
})
.then(response => response.json())
.then(data => console.log(data));`}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default ApiKeyManager;
