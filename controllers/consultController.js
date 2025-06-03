const Consultation = require('../models/Consultation');
const User = require('../models/User');
const generateReport = require('../utils/reportGenerator');

exports.submitConsultation = async (req, res) => {
  const userId = req.user.id;
  const { symptoms, duration, severity, notes } = req.body;

  try {
    const report = generateReport({ symptoms, duration, severity });

    const newConsult = await Consultation.create({
      userId,
      symptoms,
      duration,
      severity,
      notes,
      report
    });

    await User.findByIdAndUpdate(userId, {
      $push: { history: newConsult._id }
    });

    res.status(201).json({ report, consultId: newConsult._id });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getUserHistory = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).populate('history');
    if (!user) return res.status(404).json({ message: 'User not found' });

    res.json({
      name: user.name,
      email: user.email,
      consultations: user.history
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
