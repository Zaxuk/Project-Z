package com.zclub.repository;

import com.zclub.model.RewardRedemption;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface RewardRedemptionRepository extends JpaRepository<RewardRedemption, UUID> {
    Iterable<RewardRedemption> findByUserId(UUID userId);
    Iterable<RewardRedemption> findByRewardId(UUID rewardId);
}