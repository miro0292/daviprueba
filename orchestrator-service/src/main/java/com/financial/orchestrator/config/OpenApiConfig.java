package com.financial.orchestrator.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.Components;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Orchestrator Service API")
                .version("1.0.0")
                .description("Servicio orquestador — valida sesiones y coordina los microservicios core"))
            .addSecurityItem(new SecurityRequirement().addList("sessionId"))
            .components(new Components()
                .addSecuritySchemes("sessionId", new SecurityScheme()
                    .name("X-Session-Id")
                    .type(SecurityScheme.Type.APIKEY)
                    .in(SecurityScheme.In.HEADER)
                    .description("sessionId obtenido al hacer login en el auth-service")));
    }
}
