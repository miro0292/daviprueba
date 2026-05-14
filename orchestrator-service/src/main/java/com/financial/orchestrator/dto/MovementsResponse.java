package com.financial.orchestrator.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
public class MovementsResponse {
    @JsonProperty("user_id")
    private String userId;

    @JsonProperty("account_id")
    private String accountId;

    private int total;
    private int page;

    @JsonProperty("page_size")
    private int pageSize;

    private List<MovementItem> movements;
}
