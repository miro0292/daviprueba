package com.financial.orchestrator.exception;

import lombok.Getter;

@Getter
public class ServiceException extends RuntimeException {
    private final int statusCode;
    private final String body;

    public ServiceException(int statusCode, String body) {
        super("Error desde servicio core: " + statusCode);
        this.statusCode = statusCode;
        this.body = body;
    }
}
