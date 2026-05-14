# Daviprueba — Microservices

Prueba tecnica para daviplata simulando una aplicacion financiera en la cual se puede recargar transferir y validar movimientos 

---

## Requisitos previos

| Herramienta | Versión mínima |
|---|---|
| Docker | 24+ |
| Docker Compose | 2.24+ |
| Python | 3.12+ |
| Node.js | 20+ |
| Java | 17+ |
| Maven | 3.9+ |

---

## Paso a paso para despliegue

```bash
# 1. Clona el repositorio
git clone <url-del-repo>
cd financial-system

# 2. Copia el archivo de variables de entorno
cp .env.example .env

# 3. Levanta todos los servicios
docker compose up --build -d

# 4. Verifica que todos los servicios estén saludables
docker compose ps
```

La aplicación estará disponible en **http://localhost** en aproximadamente 60 segundos.

---

## URLs de cada servicio

| Servicio | URL | Swagger |
|---|---|---|
| Frontend | http://localhost | — |
| Auth Service | http://localhost:3000 | http://localhost:3000/auth/docs |
| Core Usuarios | http://localhost:5001 | http://localhost:5001/core1/docs |
| Core Saldo y Movimientos | http://localhost:5002 | http://localhost:5002/core2/docs |
| Core Transferencias | http://localhost:5003 | http://localhost:5003/core3/docs |
| Orchestrator Service | http://localhost:8080 | http://localhost:8080/orchestrator/docs |
| PostgreSQL | localhost:5432 | — |
| Redis | localhost:6379 | — |

---

## Flujo de uso

```
1. Registro    → POST /auth/register
2. Login       → POST /auth/login         → recibe sessionId
3. Saldo       → GET  /accounts/balance   → header: X-Session-Id
4. Transferir  → POST /transfers          → header: X-Session-Id
5. Movimientos → GET  /movements          → header: X-Session-Id
6. Logout      → POST /auth/logout        → header: X-Session-Id
```

---

## Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores:

| Variable | Descripción | Default |
|---|---|---|
| `POSTGRES_DB` | Nombre de la base de datos | `financial_db` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `postgres123` |
| `REDIS_PASSWORD` | Contraseña de Redis | `redis123` |
| `SESSION_ENCRYPTION_KEY` | Clave AES-256 (exactamente 32 chars) | ver ejemplo |
| `SESSION_TTL_SECONDS` | Duración de sesión en segundos | `1800` |
| `MAX_FAILED_ATTEMPTS` | Intentos antes de bloquear usuario | `5` |

> **Importante:** En producción cambia todos los valores por defecto.

---

## Comandos útiles

```bash
# Ver logs de un servicio
docker compose logs -f auth-service
docker compose logs -f orchestrator-service

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (borra la DB)
docker compose down -v

# Reconstruir un servicio específico
docker compose up --build -d core-usuarios

# Conectarse a PostgreSQL
docker exec -it financial-postgres psql -U postgres -d financial_db

# Conectarse a Redis
docker exec -it financial-redis redis-cli -a redis123
```

---

## Ejecutar pruebas unitarias

### Python (Core Usuarios, Core Saldo, Core Transferencias)
```bash
cd core-usuarios
pip install -r requirements.txt
pytest -v

cd ../core-saldo-movimientos
pip install -r requirements.txt
pytest -v

cd ../core-transferencias
pip install -r requirements.txt
pytest -v
```

### Node.js (Auth Service)
```bash
cd auth-service
npm install
npm test
```

### Java (Orchestrator Service)
```bash
cd orchestrator-service
mvn test
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                        FRONTEND                         │
│              React + TypeScript (puerto 80)             │
└───────────────────────┬─────────────────────────────────┘
                        │ sessionId (header)
          ┌─────────────┴──────────────┐
          │                            │
  ┌───────▼───────┐          ┌─────────▼────────┐
  │  Auth Service │          │  Orchestrator    │
  │   Node.js     │          │  Java Spring Boot│
  │  puerto 3000  │          │   puerto 8080    │
  └───────┬───────┘          └────────┬─────────┘
          │                           │
     ┌────▼────┐              ┌───────┼───────┐
     │  Redis  │◄─────────────┤       │       │
     │ Sesiones│              │       │       │
     └─────────┘        ┌─────▼──┐ ┌──▼─────┐
                        │ Core   │ │  Core  │
          ┌─────────────► Saldo  │ │ Trans. │
          │             │ :5002  │ │ :5003  │
  ┌───────▼───────┐     └───┬────┘ └───┬────┘
  │ Core Usuarios │         │          │
  │  Python :5001 │    ┌────▼──────────▼────┐
  └───────────────┘    │     PostgreSQL     │
          │            │   financial_db     │
          └────────────►                    │
                       └────────────────────┘
```

### Flujo de sesión
```
Login                         Redis                    Core Usuarios
  │──POST /auth/login────────►│                             │
  │                           │──POST /core1/users/login───►│
  │                           │◄────────userData────────────│
  │                           │──encrypt(userData)──►Redis  │
  │◄────sessionId─────────────│                             │

Request autenticado
  │──GET /accounts/balance ──►Orchestrator
  │   X-Session-Id: xxx       │──get("session:xxx")──►Redis
  │                           │◄──decrypt──►sessionData
  │                           │──POST /core2/balance (userId desde Redis)
  │◄──────balance─────────────│
```

---

## Seguridad implementada

- Contraseñas almacenadas con **bcrypt** — nunca en texto plano
- Sesiones cifradas con **AES-256-GCM** en Redis
- `sessionId` en memoria del frontend — nunca en `localStorage`
- El `userId` siempre se obtiene de Redis en el orchestrator — el frontend nunca puede modificarlo
- Datos sensibles enmascarados en todos los logs (`password`, `token`, `sessionId` parcial)
- Bloqueo temporal tras múltiples intentos fallidos de login

---

## Circuit Breaker (Resilience4j + Opossum)

| Parámetro | Valor |
|---|---|
| Ventana de evaluación | 10 llamadas |
| Umbral de error para abrir | 50% |
| Tiempo en estado abierto | 30 segundos |
| Reintentos máximos | 3 (no reintenta errores 4xx) |
| Timeout por llamada | 5 segundos |

---

## Logs estructurados

Todos los servicios emiten logs en formato JSON:

```json
{
  "timestamp": "2026-05-13T21:00:00Z",
  "level": "INFO",
  "service": "auth-service",
  "traceId": "abc-123-def",
  "sessionId": "1234***",
  "operation": "LOGIN",
  "message": "Sesión creada",
  "status": "SUCCESS",
  "durationMs": 45,
  "httpStatus": 200,
  "errorCode": null
}
```

El `traceId` se propaga entre todos los servicios vía el header `X-Trace-Id`.
