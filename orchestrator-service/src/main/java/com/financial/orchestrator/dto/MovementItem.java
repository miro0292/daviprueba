package com.financial.orchestrator.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Data
@NoArgsConstructor
public class MovementItem {
    private String id;

    @JsonProperty("transfer_id")
    private String transferId;

    private String type;
    private BigDecimal amount;

    @JsonProperty("balance_after")
    private BigDecimal balanceAfter;

    @JsonProperty("created_at")
    private OffsetDateTime createdAt;
}
