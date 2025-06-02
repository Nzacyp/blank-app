import React, { useEffect, useState } from 'react';
import API from '../api';

const HistoryPage = () => {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    API.get('/consult/history')
      .then(res => setEntries(res.data.consultations))
      .catch(() => alert('Failed to load history'));
  }, []);

  return (
    <div>
      <h2>Consultation History</h2>
      {entries.length === 0 ? <p>No consultations yet.</p> :
        entries.map((entry, i) => (
          <div key={i} style={{ border: '1px solid #ccc', padding: 10, margin: 10 }}>
            <p><strong>Symptoms:</strong> {entry.symptoms.join(', ')}</p>
            <p><strong>Duration:</strong> {entry.duration}</p>
            <p><strong>Severity:</strong> {entry.severity}</p>
            <p><strong>Report:</strong> {entry.report}</p>
            <p><em>Date:</em> {new Date(entry.createdAt).toLocaleString()}</p>
          </div>
        ))
      }
    </div>
  );
};

export default HistoryPage;
