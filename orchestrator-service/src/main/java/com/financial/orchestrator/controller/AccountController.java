package com.financial.orchestrator.controller;

import com.financial.orchestrator.dto.BalanceResponse;
import com.financial.orchestrator.dto.ErrorResponse;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.filter.SessionValidationFilter;
import com.financial.orchestrator.service.AccountService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/accounts")
@RequiredArgsConstructor
@Tag(name = "Cuentas", description = "Consulta de saldo de la cuenta autenticada")
public class AccountController {

    private final AccountService accountService;

    @GetMapping("/balance")
    @Operation(
        summary = "Consultar saldo",
        description = "Retorna el saldo de la cuenta del usuario autenticado. El userId se obtiene de la sesión en Redis.",
        responses = {
            @ApiResponse(responseCode = "200", description = "Saldo consultado"),
            @ApiResponse(responseCode = "401", description = "Sesión inválida",
                content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "Cuenta no encontrada",
                content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
        }
    )
    public ResponseEntity<BalanceResponse> getBalance(HttpServletRequest request) {
        SessionData session = (SessionData) request.getAttribute(SessionValidationFilter.SESSION_DATA_ATTR);
        String traceId     = (String) request.getAttribute(SessionValidationFilter.TRACE_ID_ATTR);
        String sessionId   = (String) request.getAttribute(SessionValidationFilter.SESSION_ID_ATTR);
        return ResponseEntity.ok(accountService.getBalance(session, traceId, sessionId));
    }
}
