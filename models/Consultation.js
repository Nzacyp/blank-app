const mongoose = require('mongoose');

const ConsultationSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  symptoms: { type: [String], required: true },
  duration: { type: String, required: true },
  severity: { type: String, required: true },
  notes: { type: String },
  diagnosis: { type: String, required: true },
  treatment: { type: String, required: true },
  labExams: { type: String, required: true },
  differentialDiagnoses: [
    {
      condition: String,
      confidence: String,
    },
  ],
  feedback: {
    rating: { type: Number, min: 1, max: 5 }, // e.g., 1-5 stars
    comments: String,
  },
  createdAt: { type: Date, default: Date.now },
});

module.exports = mongoose.model('Consultation', ConsultationSchema);
