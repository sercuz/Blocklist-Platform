import React, { useState, useEffect } from 'react';
import { getLogs } from '../services/api';

function LogsView() {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch logs on component mount
  useEffect(() => {
    fetchLogs();
  }, []);

  // Filter logs when search term changes
  useEffect(() => {
    if (searchTerm && Array.isArray(logs)) {
      const filtered = logs.filter(log => 
        (log.indicator && log.indicator.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (log.reason && log.reason.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (log.indicator_type && log.indicator_type.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (log.action && log.action.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (log.username && log.username.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredLogs(filtered);
    } else {
      setFilteredLogs(logs);
    }
  }, [searchTerm, logs]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const logData = await getLogs();
      console.log('Log data type:', typeof logData);
      console.log('Is array:', Array.isArray(logData));
      console.log('Log data:', logData);
      
      // Ensure we're working with an array
      if (logData && Array.isArray(logData)) {
        setLogs(logData);
        setFilteredLogs(logData);
        setError(null);
      } else {
        console.error('Invalid logs format:', logData);
        setError('Received invalid logs format from server');
        // Try to parse if it's a JSON string
        if (typeof logData === 'string') {
          try {
            const parsedData = JSON.parse(logData);
            if (Array.isArray(parsedData)) {
              setLogs(parsedData);
              setFilteredLogs(parsedData);
              setError(null);
              return;
            }
          } catch (e) {
            console.error('Failed to parse logs string:', e);
          }
        }
        setLogs([]);
        setFilteredLogs([]);
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to load logs. Please try again.');
      setLogs([]);
      setFilteredLogs([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Audit Logs</h2>
      
      {error && (
        <div className="alert alert-danger">{error}</div>
      )}
      
      <div className="search-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Search logs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      {loading ? (
        <p>Loading logs...</p>
      ) : (
        <>
          {!Array.isArray(filteredLogs) || filteredLogs.length === 0 ? (
            <p>No logs found.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Type</th>
                  <th>Indicator</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map((log, index) => (
                  <tr key={index}>
                    <td>{log.timestamp || 'N/A'}</td>
                    <td>{log.username || 'N/A'}</td>
                    <td>
                      <span className={log.action === 'BLOCK' ? 'text-danger' : 'text-success'}>
                        {log.action || 'N/A'}
                      </span>
                    </td>
                    <td>{log.indicator_type || 'N/A'}</td>
                    <td>{log.indicator || 'N/A'}</td>
                    <td>{log.reason || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
}

export default LogsView;
