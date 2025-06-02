import React, { useState } from 'react';
import API from '../api';

const ConsultationForm = () => {
  const [symptoms, setSymptoms] = useState('');
  const [duration, setDuration] = useState('');
  const [severity, setSeverity] = useState('');
  const [notes, setNotes] = useState('');
  const [report, setReport] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await API.post('/consult', {
        symptoms: symptoms.split(',').map(s => s.trim()),
        duration,
        severity,
        notes
      });
      setReport(data.report);
    } catch (err) {
      alert(err.response?.data?.message || 'Submission failed');
    }
  };

  return (
    <form onSubmit={submit}>
      <h2>Consultation</h2>
      <input value={symptoms} onChange={e => setSymptoms(e.target.value)} placeholder="Symptoms (comma separated)" required />
      <select value={duration} onChange={e => setDuration(e.target.value)} required>
        <option value="">Select duration</option>
        <option>less than 3 days</option>
        <option>3-7 days</option>
        <option>more than 1 week</option>
      </select>
      <select value={severity} onChange={e => setSeverity(e.target.value)} required>
        <option value="">Select severity</option>
        <option>low</option>
        <option>moderate</option>
        <option>high</option>
      </select>
      <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Additional notes..." />
      <button type="submit">Submit</button>
      {report && <div><h3>Report:</h3><p>{report}</p></div>}
    </form>
  );
};

export default ConsultationForm;
