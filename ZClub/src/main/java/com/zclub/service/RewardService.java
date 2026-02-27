package com.zclub.service;

import com.zclub.model.DefaultReward;
import com.zclub.model.Reward;
import com.zclub.model.RewardRedemption;
import com.zclub.repository.DefaultRewardRepository;
import com.zclub.repository.RewardRepository;
import com.zclub.repository.RewardRedemptionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.UUID;

@Service
public class RewardService {
    @Autowired
    private RewardRepository rewardRepository;

    @Autowired
    private DefaultRewardRepository defaultRewardRepository;

    @Autowired
    private RewardRedemptionRepository rewardRedemptionRepository;

    @Autowired
    private PointService pointService;

    public Reward createReward(Reward reward) {
        return rewardRepository.save(reward);
    }

    public Iterable<Reward> getRewardsByFamilyId(UUID familyId) {
        return rewardRepository.findByFamilyIdAndStatus(familyId, "active");
    }

    public Iterable<DefaultReward> getDefaultRewards() {
        return defaultRewardRepository.findByStatus("active");
    }

    @Transactional
    public boolean redeemReward(UUID userId, UUID rewardId) {
        // 检查奖励是否存在
        Reward reward = rewardRepository.findById(rewardId).orElse(null);
        if (reward == null) {
            return false;
        }

        // 检查积分是否足够
        boolean success = pointService.deductPoints(
                userId,
                reward.getPointsRequired(),
                rewardId,
                "reward",
                "兑换奖励: " + reward.getName()
        );

        if (success) {
            // 创建兑换记录
            RewardRedemption redemption = new RewardRedemption();
            redemption.setUserId(userId);
            redemption.setRewardId(rewardId);
            redemption.setStatus("completed");
            rewardRedemptionRepository.save(redemption);

            // 减少库存（如果有）
            if (reward.getStock() != null && reward.getStock() > 0) {
                reward.setStock(reward.getStock() - 1);
                rewardRepository.save(reward);
            }

            return true;
        }

        return false;
    }

    public Iterable<RewardRedemption> getRedemptionsByUserId(UUID userId) {
        return rewardRedemptionRepository.findByUserId(userId);
    }
}