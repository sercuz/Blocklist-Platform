import React, { useState } from 'react';
import { blockIndicators, unblockIndicators } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

function BlockingForm() {
  const [indicatorType, setIndicatorType] = useState('ip');
  const [indicators, setIndicators] = useState('');
  const [reason, setReason] = useState('');
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [invalidIndicators, setInvalidIndicators] = useState([]);
  const [existingIndicators, setExistingIndicators] = useState([]);
  const [nonExistentIndicators, setNonExistentIndicators] = useState([]);
  
  const { currentUser } = useAuth();

  const handleSubmit = async (action) => {
    // Clear previous messages
    setMessage(null);
    setError(null);
    setInvalidIndicators([]);
    setExistingIndicators([]);
    setNonExistentIndicators([]);
    
    // Validate inputs
    if (!indicators.trim()) {
      setError('Please enter at least one indicator');
      return;
    }
    
    if (!reason.trim()) {
      setError('Please enter a reason for this action');
      return;
    }
    
    try {
      setLoading(true);
      
      // Call the appropriate API function based on action
      let response;
      if (action === 'block') {
        response = await blockIndicators(indicatorType, indicators, reason);
        
        // Check for invalid indicators
        if (response.invalid_indicators && response.invalid_indicators.length > 0) {
          setInvalidIndicators(response.invalid_indicators);
        }
        
        // Check for existing indicators
        if (response.existing_indicators && response.existing_indicators.length > 0) {
          setExistingIndicators(response.existing_indicators);
        }
        
        setMessage(response.message || `Successfully blocked ${response.added_indicators.length} indicators`);
      } else {
        response = await unblockIndicators(indicatorType, indicators, reason);
        
        // Check for non-existent indicators
        if (response.non_existent_indicators && response.non_existent_indicators.length > 0) {
          setNonExistentIndicators(response.non_existent_indicators);
        }
        
        setMessage(response.message || `Successfully unblocked ${response.removed_indicators.length} indicators`);
      }
      
      // Clear form after successful submission
      setIndicators('');
      setReason('');
    } catch (err) {
      console.error('Error:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Block/Unblock Indicators of Compromise</h2>
      
      {message && (
        <div className="alert alert-success">{message}</div>
      )}
      
      {error && (
        <div className="alert alert-danger">{error}</div>
      )}
      
      {invalidIndicators.length > 0 && (
        <div className="alert alert-warning">
          <p>The following indicators were invalid for type '{indicatorType}':</p>
          <ul>
            {invalidIndicators.map((item, index) => (
              <li key={index}>
                <strong>{item.original}</strong> (sanitized to: {item.sanitized}) - {item.reason}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {existingIndicators.length > 0 && (
        <div className="alert alert-info">
          <p>The following indicators are already in the {indicatorType} blocklist:</p>
          <ul>
            {existingIndicators.map((item, index) => (
              <li key={index}><strong>{item}</strong></li>
            ))}
          </ul>
        </div>
      )}
      
      {nonExistentIndicators.length > 0 && (
        <div className="alert alert-info">
          <p>The following indicators were not found in the {indicatorType} blocklist:</p>
          <ul>
            {nonExistentIndicators.map((item, index) => (
              <li key={index}><strong>{item}</strong></li>
            ))}
          </ul>
        </div>
      )}
      
      <div className="form-group">
        <label htmlFor="indicator-type">Indicator Type</label>
        <select
          id="indicator-type"
          value={indicatorType}
          onChange={(e) => setIndicatorType(e.target.value)}
          disabled={loading}
        >
          <option value="ip">IP Address</option>
          <option value="domain">Domain</option>
          <option value="url">URL</option>
        </select>
      </div>
      
      <div className="form-group">
        <label htmlFor="indicators">Indicators (one per line)</label>
        <textarea
          id="indicators"
          value={indicators}
          onChange={(e) => setIndicators(e.target.value)}
          placeholder={`Enter ${indicatorType === 'ip' ? 'IP addresses' : indicatorType === 'domain' ? 'domains' : 'URLs'}, one per line\nBrackets and braces will be removed (e.g., google[.]com → google.com, 8[8]8.8 → 888.8)`}
          disabled={loading}
          rows={10}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="reason">Reason</label>
        <textarea
          id="reason"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Enter business/security reason for this action"
          disabled={loading}
          rows={4}
        />
      </div>
      
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={() => handleSubmit('block')}
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Block'}
        </button>
        
        <button
          onClick={() => handleSubmit('unblock')}
          className="secondary"
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Unblock'}
        </button>
      </div>
    </div>
  );
}

export default BlockingForm;
