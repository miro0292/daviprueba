package com.financial.orchestrator.client;

import com.financial.orchestrator.dto.BalanceResponse;
import com.financial.orchestrator.dto.MovementsResponse;
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

import java.util.Map;

@Component
@RequiredArgsConstructor
public class CoreSaldoClient {

    private final RestTemplate restTemplate;

    @Value("${app.core.saldo-url}")
    private String coreSaldoUrl;

    @CircuitBreaker(name = "coreSaldo", fallbackMethod = "balanceFallback")
    @Retry(name = "coreSaldo")
    public BalanceResponse getBalance(String userId, String traceId) {
        HttpHeaders headers = buildHeaders(traceId);
        Map<String, String> body = Map.of("user_id", userId);
        return restTemplate.exchange(
            coreSaldoUrl + "/core2/balance",
            HttpMethod.POST,
            new HttpEntity<>(body, headers),
            BalanceResponse.class
        ).getBody();
    }

    @CircuitBreaker(name = "coreSaldo", fallbackMethod = "movementsFallback")
    @Retry(name = "coreSaldo")
    public MovementsResponse getMovements(String userId, int page, int pageSize, String traceId) {
        HttpHeaders headers = buildHeaders(traceId);
        Map<String, Object> body = Map.of("user_id", userId, "page", page, "page_size", pageSize);
        return restTemplate.exchange(
            coreSaldoUrl + "/core2/movements",
            HttpMethod.POST,
            new HttpEntity<>(body, headers),
            MovementsResponse.class
        ).getBody();
    }

    public BalanceResponse balanceFallback(String userId, String traceId, Exception ex) {
        if (ex instanceof ServiceException se) throw se;
        throw new RuntimeException("Servicio de saldo no disponible temporalmente");
    }

    public MovementsResponse movementsFallback(String userId, int page, int pageSize, String traceId, Exception ex) {
        if (ex instanceof ServiceException se) throw se;
        throw new RuntimeException("Servicio de movimientos no disponible temporalmente");
    }

    private HttpHeaders buildHeaders(String traceId) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Trace-Id", traceId);
        return headers;
    }
}
