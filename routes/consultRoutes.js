// routes/consultRoutes.js

const express = require('express');
const router = express.Router();
const authMiddleware = require('../middleware/auth');

const {
  createConsult,
  getConsults,
  getConsultById,
  addFeedback
} = require('../controllers/consultController');

// Create a new consultation
router.post('/consult', authMiddleware, createConsult);

// Get all consultations for logged-in user
router.get('/', authMiddleware, getConsults);

// Get consultation by ID
router.get('/:id', authMiddleware, getConsultById);

// Add feedback for a consultation by ID
router.post('/:id/feedback', authMiddleware, addFeedback);

module.exports = router;
