package com.financial.orchestrator.service;

import com.financial.orchestrator.client.CoreTransferenciasClient;
import com.financial.orchestrator.dto.SessionData;
import com.financial.orchestrator.dto.TransferRequest;
import com.financial.orchestrator.dto.TransferResponse;
import com.financial.orchestrator.util.StructuredLogger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TransferServiceTest {

    @Mock CoreTransferenciasClient coreTransferenciasClient;
    @Mock StructuredLogger logger;
    @InjectMocks TransferService transferService;

    private SessionData session;
    private static final String TRACE_ID   = "trace-transfer-001";
    private static final String SESSION_ID = "session-001";

    @BeforeEach
    void setUp() {
        session = new SessionData();
        session.setUserId("origin-user-uuid");
        session.setUsername("juanperez");
    }

    @Test
    void executeTransfer_usesOriginUserIdFromSession() {
        TransferRequest req = new TransferRequest();
        req.setDestinationPhone("3009876543");
        req.setAmount(new BigDecimal("100000.00"));

        TransferResponse expected = new TransferResponse();
        expected.setStatus("COMPLETADA");
        expected.setTransferId("txn-uuid-1");

        when(coreTransferenciasClient.executeTransfer(
            "origin-user-uuid", "3009876543", new BigDecimal("100000.00"), TRACE_ID
        )).thenReturn(expected);

        TransferResponse result = transferService.executeTransfer(req, session, TRACE_ID, SESSION_ID);

        assertThat(result.getStatus()).isEqualTo("COMPLETADA");
        // El origin_user_id proviene de la sesión, no del request del frontend
        verify(coreTransferenciasClient).executeTransfer(
            eq("origin-user-uuid"), eq("3009876543"), any(), eq(TRACE_ID)
        );
    }

    @Test
    void executeTransfer_propagatesTraceId() {
        TransferRequest req = new TransferRequest();
        req.setDestinationPhone("3009876543");
        req.setAmount(BigDecimal.ONE);

        when(coreTransferenciasClient.executeTransfer(any(), any(), any(), any()))
            .thenReturn(new TransferResponse());

        transferService.executeTransfer(req, session, TRACE_ID, SESSION_ID);

        verify(coreTransferenciasClient).executeTransfer(any(), any(), any(), eq(TRACE_ID));
    }
}
