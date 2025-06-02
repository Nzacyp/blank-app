const express = require('express');
const cors = require('cors');

// Import route files
const userRoutes = require('./routes/userRoutes');
const consultRoutes = require('./routes/consultRoutes');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/users', userRoutes);
app.use('/api/consult', consultRoutes);

// Default route
app.get('/', (req, res) => {
  res.send('Medical Self-Consultation API is running');
});

module.exports = app;
