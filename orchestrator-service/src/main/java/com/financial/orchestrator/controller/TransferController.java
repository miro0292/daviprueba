package com.financial.orchestrator.controller;

import com.financial.orchestrator.dto.ErrorResponse;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.dto.TransferRequest;
import com.financial.orchestrator.dto.TransferResponse;
import com.financial.orchestrator.filter.SessionValidationFilter;
import com.financial.orchestrator.service.TransferService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/transfers")
@RequiredArgsConstructor
@Tag(name = "Transferencias", description = "Ejecución de transferencias por número de teléfono")
public class TransferController {

    private final TransferService transferService;

    @PostMapping
    @Operation(
        summary = "Realizar transferencia",
        description = "Transfiere fondos al usuario con el teléfono indicado. El usuario origen se toma de la sesión.",
        responses = {
            @ApiResponse(responseCode = "201", description = "Transferencia exitosa"),
            @ApiResponse(responseCode = "401", description = "Sesión inválida",
                content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "422", description = "Error de validación de negocio",
                content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "503", description = "Servicio no disponible",
                content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
        }
    )
    public ResponseEntity<TransferResponse> transfer(@Valid @RequestBody TransferRequest body,
                                                      HttpServletRequest request) {
        SessionData session = (SessionData) request.getAttribute(SessionValidationFilter.SESSION_DATA_ATTR);
        String traceId     = (String) request.getAttribute(SessionValidationFilter.TRACE_ID_ATTR);
        String sessionId   = (String) request.getAttribute(SessionValidationFilter.SESSION_ID_ATTR);
        TransferResponse result = transferService.executeTransfer(body, session, traceId, sessionId);
        return ResponseEntity.status(HttpStatus.CREATED).body(result);
    }
}
