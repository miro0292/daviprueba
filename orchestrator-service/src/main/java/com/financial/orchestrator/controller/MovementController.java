package com.financial.orchestrator.controller;

import com.financial.orchestrator.dto.MovementsResponse;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.filter.SessionValidationFilter;
import com.financial.orchestrator.service.MovementService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/movements")
@RequiredArgsConstructor
@Tag(name = "Movimientos", description = "Consulta de movimientos del usuario autenticado")
public class MovementController {

    private final MovementService movementService;

    @GetMapping
    @Operation(
        summary = "Consultar movimientos",
        description = "Retorna los movimientos paginados de la cuenta del usuario autenticado."
    )
    public ResponseEntity<MovementsResponse> getMovements(
        @Parameter(description = "Número de página") @RequestParam(defaultValue = "1") int page,
        @Parameter(description = "Tamaño de página (máx 100)") @RequestParam(defaultValue = "20", name = "page_size") int pageSize,
        HttpServletRequest request
    ) {
        SessionData session = (SessionData) request.getAttribute(SessionValidationFilter.SESSION_DATA_ATTR);
        String traceId     = (String) request.getAttribute(SessionValidationFilter.TRACE_ID_ATTR);
        String sessionId   = (String) request.getAttribute(SessionValidationFilter.SESSION_ID_ATTR);
        return ResponseEntity.ok(movementService.getMovements(session, page, pageSize, traceId, sessionId));
    }
}
