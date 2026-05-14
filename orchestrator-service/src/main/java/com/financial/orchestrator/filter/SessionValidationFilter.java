package com.financial.orchestrator.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.financial.orchestrator.dto.ErrorResponse;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.util.CryptoUtil;
import com.financial.orchestrator.util.StructuredLogger;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Set;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class SessionValidationFilter extends OncePerRequestFilter {

    public static final String SESSION_DATA_ATTR = "sessionData";
    public static final String SESSION_ID_ATTR   = "sessionId";
    public static final String TRACE_ID_ATTR     = "traceId";

    private static final Set<String> SKIP_PATHS = Set.of(
        "/orchestrator/docs", "/orchestrator/openapi.json",
        "/orchestrator/health", "/actuator", "/health"
    );

    private final StringRedisTemplate redis;
    private final CryptoUtil cryptoUtil;
    private final StructuredLogger logger;
    private final ObjectMapper objectMapper;

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getRequestURI();
        return SKIP_PATHS.stream().anyMatch(path::startsWith);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {

        String sessionId = request.getHeader("X-Session-Id");
        String traceId   = request.getHeader("X-Trace-Id");
        if (traceId == null || traceId.isBlank()) traceId = UUID.randomUUID().toString();

        if (sessionId == null || sessionId.isBlank()) {
            logger.warn("SESSION_VALIDATE", "Header X-Session-Id ausente",
                traceId, null, "FAILED", 401, "SESSION_MISSING");
            writeError(response, 401, "SESSION_MISSING", "Sesión requerida");
            return;
        }

        String encrypted = redis.opsForValue().get("session:" + sessionId);
        if (encrypted == null) {
            logger.warn("SESSION_VALIDATE", "Sesión no encontrada o expirada",
                traceId, sessionId, "FAILED", 401, "SESSION_EXPIRED");
            writeError(response, 401, "SESSION_EXPIRED", "Sesión expirada o inválida");
            return;
        }

        SessionData sessionData;
        try {
            String json = cryptoUtil.decrypt(encrypted);
            sessionData = objectMapper.readValue(json, SessionData.class);
        } catch (Exception e) {
            logger.error("SESSION_DECRYPT", "Error al descifrar sesión", traceId, sessionId, 401, "SESSION_INVALID");
            writeError(response, 401, "SESSION_INVALID", "Sesión inválida");
            return;
        }

        // Inyecta en el request — nunca confiamos en datos del frontend
        request.setAttribute(SESSION_DATA_ATTR, sessionData);
        request.setAttribute(SESSION_ID_ATTR, sessionId);
        request.setAttribute(TRACE_ID_ATTR, traceId);

        chain.doFilter(request, response);
    }

    private void writeError(HttpServletResponse response, int status, String code, String message) throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        objectMapper.writeValue(response.getWriter(), new ErrorResponse(code, message));
    }
}
