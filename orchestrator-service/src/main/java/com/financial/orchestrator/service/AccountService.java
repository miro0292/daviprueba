package com.financial.orchestrator.service;

import com.financial.orchestrator.client.CoreSaldoClient;
import com.financial.orchestrator.dto.BalanceResponse;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.util.StructuredLogger;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AccountService {

    private final CoreSaldoClient coreSaldoClient;
    private final StructuredLogger logger;

    public BalanceResponse getBalance(SessionData session, String traceId, String sessionId) {
        long start = System.currentTimeMillis();
        // userId proviene de la sesión validada en Redis — nunca del frontend
        BalanceResponse result = coreSaldoClient.getBalance(session.getUserId(), traceId);
        logger.info("GET_BALANCE", "Saldo consultado para usuario: " + session.getUsername(),
            traceId, sessionId, "SUCCESS", 200, System.currentTimeMillis() - start);
        return result;
    }
}
