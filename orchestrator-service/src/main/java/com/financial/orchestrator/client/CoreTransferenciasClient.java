package com.financial.orchestrator.client;

import com.financial.orchestrator.dto.TransferResponse;
import com.financial.orchestrator.exception.ServiceException;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.Map;

@Component
@RequiredArgsConstructor
public class CoreTransferenciasClient {

    private final RestTemplate restTemplate;

    @Value("${app.core.transferencias-url}")
    private String coreTransferenciasUrl;

    @CircuitBreaker(name = "coreTransferencias", fallbackMethod = "transferFallback")
    @Retry(name = "coreTransferencias")
    public TransferResponse executeTransfer(String originUserId,
                                            String destinationPhone,
                                            BigDecimal amount,
                                            String traceId) {
        HttpHeaders headers = buildHeaders(traceId);
        Map<String, Object> body = Map.of(
            "origin_user_id", originUserId,
            "destination_phone", destinationPhone,
            "amount", amount,
            "trace_id", traceId
        );
        return restTemplate.exchange(
            coreTransferenciasUrl + "/core3/transfers",
            HttpMethod.POST,
            new HttpEntity<>(body, headers),
            TransferResponse.class
        ).getBody();
    }

    public TransferResponse transferFallback(String originUserId, String destinationPhone,
                                             BigDecimal amount, String traceId, Exception ex) {
        if (ex instanceof ServiceException se) throw se;
        throw new RuntimeException("Servicio de transferencias no disponible temporalmente");
    }

    private HttpHeaders buildHeaders(String traceId) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Trace-Id", traceId);
        return headers;
    }
}
