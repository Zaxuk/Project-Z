package com.zclub.modules.point.repository;

import com.zclub.modules.point.entity.PointRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface PointRecordRepository extends JpaRepository<PointRecord, UUID> {
    Iterable<PointRecord> findByUserId(UUID userId);
}