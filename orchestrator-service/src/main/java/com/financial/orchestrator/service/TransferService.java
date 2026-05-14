package com.financial.orchestrator.service;

import com.financial.orchestrator.client.CoreTransferenciasClient;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.dto.TransferRequest;
import com.financial.orchestrator.dto.TransferResponse;
import com.financial.orchestrator.util.StructuredLogger;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class TransferService {

    private final CoreTransferenciasClient coreTransferenciasClient;
    private final StructuredLogger logger;

    public TransferResponse executeTransfer(TransferRequest request,
                                            SessionData session,
                                            String traceId,
                                            String sessionId) {
        long start = System.currentTimeMillis();
        // origin_user_id viene de la sesión — nunca del frontend
        TransferResponse result = coreTransferenciasClient.executeTransfer(
            session.getUserId(),
            request.getDestinationPhone(),
            request.getAmount(),
            traceId
        );
        logger.info("TRANSFER", "Transferencia ejecutada por usuario: " + session.getUsername(),
            traceId, sessionId, "SUCCESS", 201, System.currentTimeMillis() - start);
        return result;
    }
}
