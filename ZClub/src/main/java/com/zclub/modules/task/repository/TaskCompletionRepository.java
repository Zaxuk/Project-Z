package com.zclub.modules.task.repository;

import com.zclub.modules.task.entity.TaskCompletion;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface TaskCompletionRepository extends JpaRepository<TaskCompletion, UUID> {
    Iterable<TaskCompletion> findByTaskId(UUID taskId);
    Iterable<TaskCompletion> findByUserId(UUID userId);
    Iterable<TaskCompletion> findByStatus(String status);
}