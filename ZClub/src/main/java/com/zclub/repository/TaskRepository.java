package com.zclub.repository;

import com.zclub.model.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface TaskRepository extends JpaRepository<Task, UUID> {
    Iterable<Task> findByFamilyId(UUID familyId);
    Iterable<Task> findByFamilyIdAndStatus(UUID familyId, String status);
}