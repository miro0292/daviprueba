package com.financial.orchestrator.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;

@Data
@NoArgsConstructor
public class BalanceResponse {
    @JsonProperty("user_id")
    private String userId;

    @JsonProperty("account_id")
    private String accountId;

    private BigDecimal balance;
    private String currency;

    @JsonProperty("account_status")
    private String accountStatus;
}
