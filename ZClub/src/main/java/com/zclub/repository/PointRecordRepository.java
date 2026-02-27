package com.zclub.repository;

import com.zclub.model.PointRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface PointRecordRepository extends JpaRepository<PointRecord, UUID> {
    Iterable<PointRecord> findByUserId(UUID userId);
}