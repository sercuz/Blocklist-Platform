import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getApiLogs } from '../services/api';

const ApiLogViewer = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds

  // Function to fetch logs
  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await getApiLogs();
      setLogs(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching API logs:', err);
      setError('Failed to load API logs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch and setup refresh interval
  useEffect(() => {
    fetchLogs();

    // Set up auto-refresh
    const intervalId = setInterval(() => {
      fetchLogs();
    }, refreshInterval * 1000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [refreshInterval]);

  // Handle filter change
  const handleFilterChange = (e) => {
    setFilter(e.target.value);
  };

  // Filter logs based on search input
  const filteredLogs = logs.filter(log => {
    const searchTerm = filter.toLowerCase();
    return (
      (log.path && log.path.toLowerCase().includes(searchTerm)) ||
      (log.method && log.method.toLowerCase().includes(searchTerm)) ||
      (log.status_code && log.status_code.toString().includes(searchTerm)) ||
      (log.user && log.user.toLowerCase().includes(searchTerm)) ||
      (log.api_key && log.api_key.toLowerCase().includes(searchTerm)) ||
      (log.ip_address && log.ip_address.toLowerCase().includes(searchTerm))
    );
  });

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Get status code class for styling
  const getStatusCodeClass = (statusCode) => {
    if (!statusCode) return '';
    if (statusCode < 300) return 'text-success';
    if (statusCode < 400) return 'text-info';
    if (statusCode < 500) return 'text-warning';
    return 'text-danger';
  };

  // Get method class for styling
  const getMethodClass = (method) => {
    if (!method) return '';
    switch (method.toUpperCase()) {
      case 'GET': return 'badge bg-success';
      case 'POST': return 'badge bg-primary';
      case 'PUT': return 'badge bg-info';
      case 'PATCH': return 'badge bg-warning';
      case 'DELETE': return 'badge bg-danger';
      default: return 'badge bg-secondary';
    }
  };

  // Only show this component to admin users
  if (!user || !user.is_staff) {
    return <div className="container mt-4">
      <div className="alert alert-warning">Only administrators can view API logs.</div>
    </div>;
  }

  return (
    <div className="container mt-4">
      <div className="row mb-4">
        <div className="col">
          <h2>API Call Logs</h2>
          <p className="text-muted">
            View all API calls made to your Blocklist Platform. Logs are automatically refreshed every {refreshInterval} seconds.
          </p>
        </div>
      </div>

      <div className="row mb-3">
        <div className="col-md-6">
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Filter logs..."
              value={filter}
              onChange={handleFilterChange}
            />
            <button 
              className="btn btn-outline-secondary" 
              type="button"
              onClick={() => setFilter('')}
            >
              Clear
            </button>
          </div>
        </div>
        <div className="col-md-6 text-md-end mt-2 mt-md-0">
          <button 
            className="btn btn-primary me-2" 
            onClick={fetchLogs}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
          <select 
            className="form-select d-inline-block w-auto"
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
          >
            <option value="0">Manual refresh only</option>
            <option value="10">Auto refresh: 10s</option>
            <option value="30">Auto refresh: 30s</option>
            <option value="60">Auto refresh: 1m</option>
            <option value="300">Auto refresh: 5m</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger">{error}</div>
      )}

      <div className="table-responsive">
        <table className="table table-striped table-hover">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Method</th>
              <th>Path</th>
              <th>Status</th>
              <th>Response Time</th>
              <th>User</th>
              <th>API Key</th>
              <th>IP Address</th>
            </tr>
          </thead>
          <tbody>
            {loading && !logs.length ? (
              <tr>
                <td colSpan="8" className="text-center">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </td>
              </tr>
            ) : filteredLogs.length === 0 ? (
              <tr>
                <td colSpan="8" className="text-center">
                  {filter ? 'No logs match your filter criteria.' : 'No API logs found.'}
                </td>
              </tr>
            ) : (
              filteredLogs.map((log, index) => (
                <tr key={index}>
                  <td>{formatTimestamp(log.timestamp)}</td>
                  <td>
                    <span className={getMethodClass(log.method)}>
                      {log.method || 'N/A'}
                    </span>
                  </td>
                  <td>
                    <code>{log.path || 'N/A'}</code>
                  </td>
                  <td className={getStatusCodeClass(log.status_code)}>
                    {log.status_code || 'N/A'}
                  </td>
                  <td>
                    {log.response_time ? `${log.response_time.toFixed(2)}ms` : 'N/A'}
                  </td>
                  <td>{log.user || 'Anonymous'}</td>
                  <td>
                    {log.api_key ? (
                      <span className="badge bg-info">{log.api_key}</span>
                    ) : (
                      <span className="text-muted">None</span>
                    )}
                  </td>
                  <td>{log.ip_address || 'N/A'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {logs.length > 0 && filteredLogs.length === 0 && (
        <div className="alert alert-info mt-3">
          No logs match your filter criteria. <button className="btn btn-sm btn-link" onClick={() => setFilter('')}>Clear filter</button>
        </div>
      )}
    </div>
  );
};

export default ApiLogViewer;
