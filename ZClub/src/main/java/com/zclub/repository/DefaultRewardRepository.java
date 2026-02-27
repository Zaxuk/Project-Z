package com.zclub.repository;

import com.zclub.model.DefaultReward;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface DefaultRewardRepository extends JpaRepository<DefaultReward, UUID> {
    Iterable<DefaultReward> findByStatus(String status);
}