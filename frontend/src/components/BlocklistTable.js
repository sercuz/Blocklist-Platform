import React, { useState, useEffect } from 'react';
import { getBlocklist, unblockIndicators } from '../services/api';

function BlocklistTable() {
  const [blocklist, setBlocklist] = useState([]);
  const [filteredList, setFilteredList] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [unblockReason, setUnblockReason] = useState('');
  const [unblockingItem, setUnblockingItem] = useState(null);

  // Fetch blocklist on component mount
  useEffect(() => {
    fetchBlocklist();
  }, []);

  // Filter blocklist when search term changes
  useEffect(() => {
    if (searchTerm) {
      const filtered = blocklist.filter(item => 
        item.indicator.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.reason && item.reason.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (item.type && item.type.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredList(filtered);
    } else {
      setFilteredList(blocklist);
    }
  }, [searchTerm, blocklist]);

  const fetchBlocklist = async () => {
    try {
      setLoading(true);
      const data = await getBlocklist();
      console.log('Blocklist data:', data);
      setBlocklist(data);
      setFilteredList(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching blocklist:', err);
      setError('Failed to load blocklist. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUnblock = async (item) => {
    if (!unblockReason.trim()) {
      setError('Please enter a reason for unblocking');
      return;
    }

    try {
      setLoading(true);
      await unblockIndicators(item.type, item.indicator, unblockReason);
      
      // Refresh the blocklist
      await fetchBlocklist();
      
      setMessage(`Successfully unblocked ${item.indicator}`);
      setUnblockingItem(null);
      setUnblockReason('');
    } catch (err) {
      console.error('Error unblocking indicator:', err);
      setError('Failed to unblock indicator. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Blocklist Table</h2>
      
      {message && (
        <div className="alert alert-success">{message}</div>
      )}
      
      {error && (
        <div className="alert alert-danger">{error}</div>
      )}
      
      <div className="search-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Search by indicator, type, or reason..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      {loading && !unblockingItem ? (
        <p>Loading blocklist...</p>
      ) : (
        <>
          {filteredList.length === 0 ? (
            <p>No indicators found in the blocklist.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Indicator</th>
                  <th>Added By</th>
                  <th>Date</th>
                  <th>Reason</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredList.map((item, index) => (
                  <tr key={index}>
                    <td>{item.type || 'N/A'}</td>
                    <td>{item.indicator}</td>
                    <td>{item.added_by || 'N/A'}</td>
                    <td>{item.added_at || 'N/A'}</td>
                    <td>{item.reason || 'N/A'}</td>
                    <td>
                      {unblockingItem === item.indicator ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                          <input
                            type="text"
                            placeholder="Reason for unblocking"
                            value={unblockReason}
                            onChange={(e) => setUnblockReason(e.target.value)}
                          />
                          <div style={{ display: 'flex', gap: '5px' }}>
                            <button 
                              className="danger" 
                              onClick={() => handleUnblock(item)}
                              disabled={loading}
                            >
                              Confirm
                            </button>
                            <button 
                              className="secondary" 
                              onClick={() => {
                                setUnblockingItem(null);
                                setUnblockReason('');
                              }}
                              disabled={loading}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button 
                          className="danger" 
                          onClick={() => setUnblockingItem(item.indicator)}
                          disabled={loading}
                        >
                          Unblock
                        </button>
                      )}
                    </td>
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

export default BlocklistTable;
