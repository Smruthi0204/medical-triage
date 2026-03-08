package com.example.api_gateway.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TriageRequest {

    // This is what the frontend sends to Spring Boot
    // {
    //   "note": "Patient presents with chest pain..."
    // }

    private String note;
}