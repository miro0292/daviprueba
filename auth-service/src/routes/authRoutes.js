const { Router } = require('express');
const { register, login, logout } = require('../controllers/authController');
const validateSession = require('../middleware/validateSession');

const router = Router();

/**
 * @openapi
 * /auth/register:
 *   post:
 *     tags: [Auth]
 *     summary: Registro de usuario
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [document_number, email, phone, username, password]
 *             properties:
 *               document_number: { type: string, example: "12345678" }
 *               email: { type: string, format: email, example: "user@test.com" }
 *               phone: { type: string, example: "3001234567" }
 *               username: { type: string, example: "juanperez" }
 *               password: { type: string, minLength: 8, example: "Secure1234" }
 *     responses:
 *       201:
 *         description: Usuario registrado exitosamente
 *       409:
 *         description: Datos duplicados
 *       422:
 *         description: Error de validación
 */
router.post('/register', register);

/**
 * @openapi
 * /auth/login:
 *   post:
 *     tags: [Auth]
 *     summary: Login de usuario
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [username, password]
 *             properties:
 *               username: { type: string, example: "juanperez" }
 *               password: { type: string, example: "Secure1234" }
 *     responses:
 *       200:
 *         description: Login exitoso — retorna sessionId
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 sessionId: { type: string }
 *                 username: { type: string }
 *                 message: { type: string }
 *       401:
 *         description: Credenciales inválidas
 *       403:
 *         description: Usuario bloqueado
 */
router.post('/login', login);

/**
 * @openapi
 * /auth/logout:
 *   post:
 *     tags: [Auth]
 *     summary: Cierre de sesión
 *     security:
 *       - sessionId: []
 *     responses:
 *       200:
 *         description: Sesión cerrada
 *       401:
 *         description: Sesión inválida o expirada
 */
router.post('/logout', validateSession, logout);

module.exports = router;
