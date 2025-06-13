// controllers/consultController.js

const Consultation = require('../models/Consultation');

/**
 * Example advanced scoring logic for multiple diagnoses.
 * Returns an array of conditions with confidence scores sorted descending.
 * You should customize or replace this with your AI/ML logic later.
 */
function scoreConditions(symptoms) {
  const lowerSymptoms = symptoms.map(s => s.toLowerCase());

  const conditions = [
    {
      condition: 'Upper respiratory tract infection (URTI)',
      keywords: ['fever', 'cough', 'sore throat'],
      treatment: 'Paracetamol, rest, fluids',
      labExams: 'CBC, COVID-19 test'
    },
    {
      condition: 'Dental infection',
      keywords: ['toothache', 'gum pain', 'swelling'],
      treatment: 'Amoxicillin, Diclofenac, dental referral',
      labExams: 'Panoramic X-ray'
    },
    {
      condition: 'Gastroenteritis',
      keywords: ['diarrhea', 'vomiting', 'abdominal pain'],
      treatment: 'Oral rehydration salts, zinc, Metronidazole',
      labExams: 'Stool analysis, culture'
    },
    {
      condition: 'Tension headache or migraine',
      keywords: ['headache', 'migraine', 'nausea'],
      treatment: 'Paracetamol or Ibuprofen, hydration, rest',
      labExams: 'Blood pressure check, optional CT if persistent'
    }
  ];

  // Simple scoring by counting keyword matches
  const scored = conditions.map(cond => {
    let score = 0;
    for (const kw of cond.keywords) {
      if (lowerSymptoms.includes(kw)) score++;
    }
    return { ...cond, score };
  });

  // Filter out zero scores and sort descending
  return scored.filter(c => c.score > 0).sort((a, b) => b.score - a.score);
}

// Create new consultation
exports.createConsult = async (req, res) => {
  try {
    const { symptoms, duration, severity, notes, age, comorbidities } = req.body;
    const userId = req.user.id; // From auth middleware

    if (!Array.isArray(symptoms) || symptoms.length === 0 || !duration || !severity) {
      return res.status(400).json({ message: 'Symptoms, duration, and severity are required' });
    }

    const scoredConditions = scoreConditions(symptoms);

    if (scoredConditions.length === 0) {
      // No matching condition found
      const newConsult = new Consultation({
        userId,
        symptoms,
        duration,
        severity,
        notes,
        diagnosis: 'No matching condition found',
        treatment: 'Supportive care, follow up if symptoms worsen',
        labExams: 'Basic CBC and Urinalysis',
        differentialDiagnoses: []
      });

      await newConsult.save();
      return res.status(201).json(newConsult);
    }

    const primary = scoredConditions[0];

    // Personalize treatment based on age and comorbidities
    let personalizedTreatment = primary.treatment;
    let personalizedLabExams = primary.labExams;

    if (age && age > 60) {
      personalizedTreatment += '; monitor closely due to age';
      personalizedLabExams += ', EKG if cardiac symptoms';
    }
    if (comorbidities && Array.isArray(comorbidities) && comorbidities.length > 0) {
      personalizedTreatment += '; consider interactions with existing medications';
    }

    const newConsult = new Consultation({
      userId,
      symptoms,
      duration,
      severity,
      notes,
      diagnosis: primary.condition,
      treatment: personalizedTreatment,
      labExams: personalizedLabExams,
      differentialDiagnoses: scoredConditions.slice(1, 4).map(c => ({
        condition: c.condition,
        confidence: ((c.score / primary.score) * 100).toFixed(1) + '%'
      }))
    });

    await newConsult.save();

    res.status(201).json(newConsult);
  } catch (error) {
    console.error('Error creating consultation:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

// Get all consultations (simple placeholder)
exports.getConsults = async (req, res) => {
  try {
    const userId = req.user.id;
    const consults = await Consultation.find({ userId }).sort({ createdAt: -1 });
    res.status(200).json(consults);
  } catch (error) {
    console.error('Error fetching consultations:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

// Get one consultation by ID
exports.getConsultById = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const consult = await Consultation.findById(id);
    if (!consult) return res.status(404).json({ message: 'Consultation not found' });

    if (consult.userId.toString() !== userId) {
      return res.status(403).json({ message: 'Unauthorized' });
    }

    res.status(200).json(consult);
  } catch (error) {
    console.error('Error fetching consultation:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

// Add feedback to consultation
exports.addFeedback = async (req, res) => {
  try {
    const { id } = req.params;
    const { rating, comments } = req.body;
    const userId = req.user.id;

    const consult = await Consultation.findById(id);
    if (!consult) return res.status(404).json({ message: 'Consultation not found' });

    if (consult.userId.toString() !== userId) {
      return res.status(403).json({ message: 'Unauthorized to add feedback' });
    }

    consult.feedback = { rating, comments };
    await consult.save();

    res.status(200).json({ message: 'Feedback added', consultation: consult });
  } catch (error) {
    console.error('Error adding feedback:', error);
    res.status(500).json({ message: 'Server error' });
  }
};
