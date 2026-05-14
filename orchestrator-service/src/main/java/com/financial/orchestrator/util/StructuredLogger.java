package com.financial.orchestrator.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

@Component
public class StructuredLogger {

    private static final Logger log = LoggerFactory.getLogger(StructuredLogger.class);
    private static final ObjectMapper mapper = new ObjectMapper();

    @Value("${spring.application.name:orchestrator-service}")
    private String serviceName;

    public void info(String operation, String message, String traceId, String sessionId,
                     String status, Integer httpStatus, Long durationMs) {
        log.info(buildEntry("INFO", operation, message, traceId, sessionId, status, httpStatus, durationMs, null));
    }

    public void warn(String operation, String message, String traceId, String sessionId,
                     String status, Integer httpStatus, String errorCode) {
        log.warn(buildEntry("WARN", operation, message, traceId, sessionId, status, httpStatus, null, errorCode));
    }

    public void error(String operation, String message, String traceId, String sessionId,
                      Integer httpStatus, String errorCode) {
        log.error(buildEntry("ERROR", operation, message, traceId, sessionId, "FAILED", httpStatus, null, errorCode));
    }

    private String buildEntry(String level, String operation, String message, String traceId,
                               String sessionId, String status, Integer httpStatus,
                               Long durationMs, String errorCode) {
        Map<String, Object> entry = new LinkedHashMap<>();
        entry.put("timestamp", Instant.now().toString());
        entry.put("level", level);
        entry.put("service", serviceName);
        entry.put("traceId", traceId != null ? traceId : "-");
        entry.put("sessionId", mask(sessionId));
        entry.put("operation", operation);
        entry.put("message", message);
        entry.put("status", status);
        if (durationMs != null) entry.put("durationMs", durationMs);
        if (httpStatus != null) entry.put("httpStatus", httpStatus);
        if (errorCode != null) entry.put("errorCode", errorCode);
        try {
            return mapper.writeValueAsString(entry);
        } catch (Exception e) {
            return message;
        }
    }

    private String mask(String value) {
        if (value == null || value.isBlank()) return "-";
        return value.substring(0, Math.min(4, value.length())) + "***";
    }
}
