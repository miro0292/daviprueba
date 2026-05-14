package com.financial.orchestrator.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;

@Data
@NoArgsConstructor
public class TransferResponse {
    @JsonProperty("transfer_id")
    private String transferId;

    @JsonProperty("origin_account_id")
    private String originAccountId;

    @JsonProperty("destination_account_id")
    private String destinationAccountId;

    private BigDecimal amount;
    private String status;
    private String message;
}
