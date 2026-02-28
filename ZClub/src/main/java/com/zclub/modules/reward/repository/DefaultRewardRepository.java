package com.zclub.modules.reward.repository;

import com.zclub.modules.reward.entity.DefaultReward;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface DefaultRewardRepository extends JpaRepository<DefaultReward, UUID> {
    Iterable<DefaultReward> findByStatus(String status);
}