package com.financial.orchestrator.service;

import com.financial.orchestrator.client.CoreSaldoClient;
import com.financial.orchestrator.dto.BalanceResponse;
import com.financial.orchestrator.dto.SessionData;
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
class AccountServiceTest {

    @Mock CoreSaldoClient coreSaldoClient;
    @Mock StructuredLogger logger;
    @InjectMocks AccountService accountService;

    private SessionData session;
    private static final String TRACE_ID   = "trace-001";
    private static final String SESSION_ID = "session-001";

    @BeforeEach
    void setUp() {
        session = new SessionData();
        session.setUserId("user-uuid-1");
        session.setUsername("juanperez");
    }

    @Test
    void getBalance_returnsBalanceFromCore() {
        BalanceResponse expected = new BalanceResponse();
        expected.setBalance(new BigDecimal("500000.00"));
        expected.setAccountStatus("ACTIVA");

        when(coreSaldoClient.getBalance("user-uuid-1", TRACE_ID)).thenReturn(expected);

        BalanceResponse result = accountService.getBalance(session, TRACE_ID, SESSION_ID);

        assertThat(result.getBalance()).isEqualByComparingTo("500000.00");
        verify(coreSaldoClient).getBalance("user-uuid-1", TRACE_ID);
    }

    @Test
    void getBalance_usesUserIdFromSession_notFromFrontend() {
        BalanceResponse response = new BalanceResponse();
        when(coreSaldoClient.getBalance(anyString(), anyString())).thenReturn(response);

        accountService.getBalance(session, TRACE_ID, SESSION_ID);

        // Verifica que se usa el userId de la sesión (Redis), no otro valor
        verify(coreSaldoClient).getBalance(eq("user-uuid-1"), eq(TRACE_ID));
    }
}
