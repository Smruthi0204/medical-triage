package com.example.api_gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Entity                          // tells JPA this class maps to a database table
@Table(name = "medical_notes")   // the actual table name in PostgreSQL
@Data                            // Lombok: generates getters, setters, toString
@NoArgsConstructor               // Lombok: generates no-args constructor
@AllArgsConstructor              // Lombok: generates all-args constructor
public class MedicalNote {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "raw_note", columnDefinition = "TEXT")
    private String rawNote;

    @Column(name = "clean_text", columnDefinition = "TEXT")
    private String cleanText;

    @Column(name = "specialty")
    private String specialty;

    @Column(name = "confidence")
    private Double confidence;

    // JSONB column — stores the entities list as JSON in PostgreSQL
    // e.g. [{"entity": "chest pain", "status": "Negated"}, ...]
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "entities", columnDefinition = "jsonb")
    private List<Map<String, String>> entities;

    @Column(name = "status")
    private String status;

    // Called automatically before saving to database
    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
        this.status = "Pending Review";
    }
}
