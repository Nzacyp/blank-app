// backend/middleware/authMiddleware.js

function authMiddleware(req, res, next) {
  // Example: check if user is authenticated
  if (req.isAuthenticated && req.isAuthenticated()) {
    return next();
  }
  res.status(401).json({ message: 'Unauthorized' });
}

module.exports = authMiddleware;
