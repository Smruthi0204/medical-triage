package com.example.api_gateway.controller;

import com.example.api_gateway.model.MedicalNote;
import com.example.api_gateway.model.TriageRequest;
import com.example.api_gateway.model.TriageResponse;
import com.example.api_gateway.service.NoteService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")  // allows frontend to call this API
                              // in production restrict this to specific domain
public class TriageController {

    private final NoteService noteService;

    // ── POST /api/analyze ─────────────────────────────────────────────────────
    // Receives clinical note, classifies it, saves to DB, returns result
    @PostMapping("/analyze")
    public ResponseEntity<TriageResponse> analyze(
            @RequestBody TriageRequest request) {

        log.info("Received analyze request");

        // Validate input
        if (request.getNote() == null || request.getNote().trim().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }

        TriageResponse response = noteService.classifyAndSave(request);
        return ResponseEntity.ok(response);
    }

    // ── GET /api/notes ────────────────────────────────────────────────────────
    // Returns all classified notes from database
    @GetMapping("/notes")
    public ResponseEntity<List<MedicalNote>> getAllNotes() {
        log.info("Fetching all notes");
        return ResponseEntity.ok(noteService.getAllNotes());
    }

    // ── GET /api/notes/specialty/{specialty} ──────────────────────────────────
    // Returns notes filtered by specialty
    @GetMapping("/notes/specialty/{specialty}")
    public ResponseEntity<List<MedicalNote>> getNotesBySpecialty(
            @PathVariable String specialty) {
        log.info("Fetching notes for specialty: {}", specialty);
        return ResponseEntity.ok(noteService.getNotesBySpecialty(specialty));
    }

    // ── GET /api/notes/status/{status} ────────────────────────────────────────
    // Returns notes filtered by status
    @GetMapping("/notes/status/{status}")
    public ResponseEntity<List<MedicalNote>> getNotesByStatus(
            @PathVariable String status) {
        log.info("Fetching notes with status: {}", status);
        return ResponseEntity.ok(noteService.getNotesByStatus(status));
    }

    // ── GET /api/stats ────────────────────────────────────────────────────────
    // Returns specialty distribution for dashboard
    @GetMapping("/stats")
    public ResponseEntity<List<Object[]>> getStats() {
        log.info("Fetching specialty stats");
        return ResponseEntity.ok(noteService.getStats());
    }

    // ── PATCH /api/notes/{id}/status ──────────────────────────────────────────
    // Updates the review status of a note
    @PatchMapping("/notes/{id}/status")
    public ResponseEntity<MedicalNote> updateStatus(
            @PathVariable Long id,
            @RequestParam String status) {
        log.info("Updating status for note id: {} to: {}", id, status);
        return ResponseEntity.ok(noteService.updateStatus(id, status));
    }

    // ── GET /api/health ───────────────────────────────────────────────────────
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("API Gateway is running");
    }
}


