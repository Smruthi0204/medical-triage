package com.example.api_gateway.service;


import com.example.api_gateway.model.MedicalNote;
import com.example.api_gateway.model.TriageRequest;
import com.example.api_gateway.model.TriageResponse;
import com.example.api_gateway.repository.NoteRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor  // Lombok: generates constructor for all final fields
                          // Spring uses this constructor for dependency injection
public class NoteService {

    // Spring automatically injects these — no new keyword needed
    // This is called Dependency Injection
    private final MLService mlService;
    private final NoteRepository noteRepository;

    // ── Classify a new note and save to database ──────────────────────────────
    public TriageResponse classifyAndSave(TriageRequest request) {

        log.info("Classifying note of length: {}", request.getNote().length());

        // Step 1: Call FastAPI ML service
        Map mlResponse = mlService.predict(request.getNote());
        log.debug("ML response: {}", mlResponse);

        // Step 2: Extract values from ML response
        String specialty    = (String) mlResponse.get("specialty");
        Double confidence   = ((Number) mlResponse.get("confidence")).doubleValue();
        List<Map<String, String>> entities =
                (List<Map<String, String>>) mlResponse.get("entities");
        List<Map<String, Object>> allProbabilities =
                (List<Map<String, Object>>) mlResponse.get("all_probabilities");

        // Step 3: Build MedicalNote entity to save to database
        MedicalNote note = new MedicalNote();
        note.setRawNote(request.getNote());
        note.setSpecialty(specialty);
        note.setCleanText((String) mlResponse.get("clean_text"));
        note.setConfidence(confidence);
        note.setEntities(entities);
        // createdAt and status are set automatically by @PrePersist

        // Step 4: Save to PostgreSQL via JPA repository
        MedicalNote savedNote = noteRepository.save(note);
        log.info("Note saved with id: {}", savedNote.getId());

        String cleanText = (String) mlResponse.get("clean_text");

        // Set it on the note entity
        note.setCleanText(cleanText);


        // Step 5: Build and return response to frontend
        return new TriageResponse(
                savedNote.getId(),
                specialty,
                confidence,
                cleanText,
                allProbabilities,
                entities,
                savedNote.getStatus(),
                "Note classified and saved successfully"
        );
    }

    // ── Get all notes from database ───────────────────────────────────────────
    public List<MedicalNote> getAllNotes() {
        return noteRepository.findAllByOrderByCreatedAtDesc();
    }

    // ── Get notes by specialty ────────────────────────────────────────────────
    public List<MedicalNote> getNotesBySpecialty(String specialty) {
        return noteRepository.findBySpecialty(specialty);
    }

    // ── Get notes by status ───────────────────────────────────────────────────
    public List<MedicalNote> getNotesByStatus(String status) {
        return noteRepository.findByStatus(status);
    }

    // ── Get specialty distribution stats ─────────────────────────────────────
    public List<Object[]> getStats() {
        return noteRepository.countBySpecialty();
    }

    // ── Update note status ────────────────────────────────────────────────────
    public MedicalNote updateStatus(Long id, String status) {
        MedicalNote note = noteRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Note not found with id: " + id));
        note.setStatus(status);
        return noteRepository.save(note);
    }
}
