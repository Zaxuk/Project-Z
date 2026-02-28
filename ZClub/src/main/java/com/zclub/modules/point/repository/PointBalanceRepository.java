package com.zclub.modules.point.repository;

import com.zclub.modules.point.entity.PointBalance;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.UUID;

public interface PointBalanceRepository extends JpaRepository<PointBalance, UUID> {
    Optional<PointBalance> findByUserId(UUID userId);
}