const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },

  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true
  },

  password: {
    type: String,
    required: true
  },

  // Profile fields (optional, extendable)
  age: Number,
  gender: { type: String, enum: ['male', 'female', 'other'], default: 'other' },

  // Reference to consultations
  history: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Consultation'
  }]
});

module.exports = mongoose.model('User', userSchema);

