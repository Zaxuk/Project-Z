package com.zclub.repository;

import com.zclub.model.PointBalance;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.UUID;

public interface PointBalanceRepository extends JpaRepository<PointBalance, UUID> {
    Optional<PointBalance> findByUserId(UUID userId);
}