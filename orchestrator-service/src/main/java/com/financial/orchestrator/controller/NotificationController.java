package com.financial.orchestrator.controller;

import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.filter.SessionValidationFilter;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/notifications")
@Tag(name = "Notificaciones", description = "Notificaciones del usuario autenticado")
public class NotificationController {

    @GetMapping
    @Operation(summary = "Obtener notificaciones", description = "Retorna las notificaciones del usuario autenticado.")
    public ResponseEntity<Map<String, Object>> getNotifications(HttpServletRequest request) {
        SessionData session = (SessionData) request.getAttribute(SessionValidationFilter.SESSION_DATA_ATTR);
        return ResponseEntity.ok(Map.of(
            "user_id", session.getUserId(),
            "notifications", List.of(
                Map.of("id", "1", "message", "Bienvenido al sistema", "read", false,
                    "created_at", Instant.now().toString())
            )
        ));
    }
}
