package com.financial.orchestrator.service;

import com.financial.orchestrator.client.CoreSaldoClient;
import com.financial.orchestrator.dto.MovementsResponse;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.util.StructuredLogger;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class MovementService {

    private final CoreSaldoClient coreSaldoClient;
    private final StructuredLogger logger;

    public MovementsResponse getMovements(SessionData session, int page, int pageSize,
                                          String traceId, String sessionId) {
        long start = System.currentTimeMillis();
        MovementsResponse result = coreSaldoClient.getMovements(session.getUserId(), page, pageSize, traceId);
        logger.info("GET_MOVEMENTS", "Movimientos consultados para usuario: " + session.getUsername(),
            traceId, sessionId, "SUCCESS", 200, System.currentTimeMillis() - start);
        return result;
    }
}
