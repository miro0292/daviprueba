package com.financial.orchestrator.exception;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.financial.orchestrator.dto.ErrorResponse;
import com.financial.orchestrator.util.StructuredLogger;
import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@RestControllerAdvice
@RequiredArgsConstructor
public class GlobalExceptionHandler {

    private final StructuredLogger logger;
    private final ObjectMapper objectMapper;

    @ExceptionHandler(ServiceException.class)
    public ResponseEntity<Object> handleServiceException(ServiceException ex) {
        try {
            Object body = objectMapper.readValue(ex.getBody(), Object.class);
            return ResponseEntity.status(ex.getStatusCode()).body(body);
        } catch (Exception e) {
            return ResponseEntity.status(ex.getStatusCode())
                .body(new ErrorResponse("UPSTREAM_ERROR", ex.getBody()));
        }
    }

    @ExceptionHandler(CallNotPermittedException.class)
    public ResponseEntity<ErrorResponse> handleCircuitBreaker(CallNotPermittedException ex) {
        logger.error("CIRCUIT_BREAKER", "Circuit breaker abierto: " + ex.getCausingCircuitBreakerName(),
            "-", null, 503, "SERVICE_UNAVAILABLE");
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
            .body(new ErrorResponse("SERVICE_UNAVAILABLE", "Servicio temporalmente no disponible"));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(MethodArgumentNotValidException ex) {
        var errors = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> Map.of("field", e.getField(), "message", e.getDefaultMessage()))
            .toList();
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body(Map.of("error_code", "VALIDATION_ERROR", "message", "Datos inválidos", "detail", errors));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception ex) {
        logger.error("UNHANDLED", ex.getMessage(), "-", null, 500, "INTERNAL_ERROR");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("INTERNAL_ERROR", "Error interno del servidor"));
    }
}
