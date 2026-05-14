const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');
const authService = require('../services/authService');

const registerSchema = Joi.object({
  document_number: Joi.string().trim().min(5).max(20).required(),
  email: Joi.string().email().required(),
  phone: Joi.string().pattern(/^\d{7,15}$/).required(),
  username: Joi.string().trim().alphanum().min(3).max(50).required(),
  password: Joi.string().min(8).required(),
});

const loginSchema = Joi.object({
  username: Joi.string().required(),
  password: Joi.string().required(),
});

async function register(req, res, next) {
  const traceId = req.headers['x-trace-id'] || uuidv4();
  const { error, value } = registerSchema.validate(req.body, { abortEarly: false });
  if (error) {
    return res.status(422).json({
      error_code: 'VALIDATION_ERROR',
      message: 'Datos de entrada inválidos',
      detail: error.details.map((d) => ({ field: d.path.join('.'), message: d.message })),
    });
  }
  try {
    const result = await authService.register(value, traceId);
    res.status(201).json(result);
  } catch (err) {
    next(err);
  }
}

async function login(req, res, next) {
  const traceId = req.headers['x-trace-id'] || uuidv4();
  const { error, value } = loginSchema.validate(req.body);
  if (error) {
    return res.status(422).json({
      error_code: 'VALIDATION_ERROR',
      message: 'Datos de entrada inválidos',
    });
  }
  try {
    const result = await authService.login(value, traceId);
    res.status(200).json(result);
  } catch (err) {
    next(err);
  }
}

async function logout(req, res, next) {
  try {
    const result = await authService.logout(req.sessionId, req.traceId);
    res.status(200).json(result);
  } catch (err) {
    next(err);
  }
}

module.exports = { register, login, logout };
