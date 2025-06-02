const express = require('express');
const router = express.Router();
const { submitConsultation, getUserHistory } = require('../backend/controllers/consultController');
const authMiddleware = require('../middleware/auth');

router.post('/', authMiddleware, submitConsultation);
router.get('/history', authMiddleware, getUserHistory);

module.exports = router;
