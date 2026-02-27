package com.zclub.repository;

import com.zclub.model.Reward;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface RewardRepository extends JpaRepository<Reward, UUID> {
    Iterable<Reward> findByFamilyId(UUID familyId);
    Iterable<Reward> findByFamilyIdAndStatus(UUID familyId, String status);
}