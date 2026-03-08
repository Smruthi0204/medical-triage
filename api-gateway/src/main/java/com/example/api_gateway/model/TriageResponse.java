package com.example.api_gateway.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TriageResponse {

    private Long id;
    private String specialty;
    private Double confidence;
    private String cleanText;
    private List<Map<String, Object>> allProbabilities;
    private List<Map<String, String>> entities;
    private String status;
    private String message;
}
