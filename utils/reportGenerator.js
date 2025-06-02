function generateReport({ symptoms, duration, severity }) {
  const lowerSymptoms = symptoms.map(s => s.toLowerCase());

  if (lowerSymptoms.includes('fever') && severity === 'high') {
    return "You reported a high fever. This may indicate a serious infection. Seek immediate medical attention.";
  }

  if (lowerSymptoms.includes('cough') && duration === 'more than 1 week') {
    return "Persistent cough for over a week suggests a chronic or serious issue. A clinical evaluation is advised.";
  }

  if (lowerSymptoms.includes('headache') && severity === 'moderate') {
    return "Moderate headache reported. Ensure proper hydration and rest. Monitor for worsening symptoms.";
  }

  if (severity === 'low' && duration === 'less than 3 days') {
    return "Your symptoms appear mild and recent. Rest and monitor your condition. Seek care if it worsens.";
  }

  return "Your symptoms are non-specific. Please monitor your condition and consult a doctor if symptoms persist or worsen.";
}

module.exports = generateReport;
