const mongoose = require('mongoose');

const consultationSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },

  symptoms: [String],
  duration: String,
  severity: String,
  notes: String,
  report: String,

  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Consultation', consultationSchema);
