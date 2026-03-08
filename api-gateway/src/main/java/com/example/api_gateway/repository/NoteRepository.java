package com.example.api_gateway.repository;


import com.example.api_gateway.model.MedicalNote;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface NoteRepository extends JpaRepository<MedicalNote, Long> {

    // ── Spring Data JPA auto-generates SQL for these methods ──────────────────
    // You just define the method signature — no SQL needed

    // Find all notes for a specific specialty
    // SQL: SELECT * FROM medical_notes WHERE specialty = ?
    List<MedicalNote> findBySpecialty(String specialty);

    // Find all notes with a specific status
    // SQL: SELECT * FROM medical_notes WHERE status = ?
    List<MedicalNote> findByStatus(String status);

    // Find all notes ordered by created_at descending (newest first)
    // SQL: SELECT * FROM medical_notes ORDER BY created_at DESC
    List<MedicalNote> findAllByOrderByCreatedAtDesc();

    // ── Custom query for specialty distribution stats ──────────────────────────
    // Returns count of notes per specialty
    // Used for dashboard statistics
    @Query("SELECT m.specialty, COUNT(m) FROM MedicalNote m GROUP BY m.specialty")
    List<Object[]> countBySpecialty();
}
