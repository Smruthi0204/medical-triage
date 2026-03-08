package com.example.api_gateway.service;

import com.example.api_gateway.model.TriageRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import lombok.extern.slf4j.Slf4j;
import java.util.Map;

@Service   // tells Spring this is a service bean — managed by Spring container
@Slf4j     // Lombok: generates a logger called 'log' automatically
public class MLService {

    private final WebClient webClient;

    // @Value reads from application.properties
    // ml.service.url=http://localhost:8000
    // Spring injects this value automatically
    public MLService(@Value("${ml.service.url}") String mlServiceUrl) {
        this.webClient = WebClient.builder()
                .baseUrl(mlServiceUrl)
                .build();
    }

    // ── Call FastAPI /predict endpoint ────────────────────────────────────────
    public Map predict(String note) {

        log.debug("Calling ML service with note of length: {}", note.length());

        try {
            // Build and send POST request to FastAPI
            // This is equivalent to Postman sending:
            // POST http://localhost:8000/predict
            // { "note": "..." }
            Map response = webClient
                    .post()
                    .uri("/predict")
                    .bodyValue(Map.of("note", note))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block(); // block() waits for response synchronously

            log.debug("ML service response received: {}", response);
            return response;

        } catch (WebClientResponseException e) {
            log.error("ML service returned error: {} - {}",
                    e.getStatusCode(), e.getResponseBodyAsString());
            throw new RuntimeException(
                    "ML service error: " + e.getResponseBodyAsString()
            );
        } catch (Exception e) {
            log.error("Failed to call ML service: {}", e.getMessage());
            throw new RuntimeException(
                    "Failed to connect to ML service: " + e.getMessage()
            );
        }
    }
}

