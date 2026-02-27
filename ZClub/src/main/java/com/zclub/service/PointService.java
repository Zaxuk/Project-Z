package com.zclub.service;

import com.zclub.model.PointBalance;
import com.zclub.model.PointRecord;
import com.zclub.repository.PointBalanceRepository;
import com.zclub.repository.PointRecordRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.UUID;

@Service
public class PointService {
    @Autowired
    private PointBalanceRepository pointBalanceRepository;

    @Autowired
    private PointRecordRepository pointRecordRepository;

    @Transactional
    public void addPoints(UUID userId, Integer amount, UUID relatedId, String relatedType, String description) {
        // 获取或创建积分余额
        PointBalance balance = pointBalanceRepository.findByUserId(userId)
                .orElseGet(() -> {
                    PointBalance newBalance = new PointBalance();
                    newBalance.setUserId(userId);
                    newBalance.setBalance(0);
                    return pointBalanceRepository.save(newBalance);
                });

        // 更新余额
        balance.setBalance(balance.getBalance() + amount);
        pointBalanceRepository.save(balance);

        // 记录积分变动
        PointRecord record = new PointRecord();
        record.setUserId(userId);
        record.setType("earned");
        record.setAmount(amount);
        record.setRelatedId(relatedId);
        record.setRelatedType(relatedType);
        record.setDescription(description);
        pointRecordRepository.save(record);
    }

    @Transactional
    public boolean deductPoints(UUID userId, Integer amount, UUID relatedId, String relatedType, String description) {
        // 获取积分余额
        PointBalance balance = pointBalanceRepository.findByUserId(userId)
                .orElseGet(() -> {
                    PointBalance newBalance = new PointBalance();
                    newBalance.setUserId(userId);
                    newBalance.setBalance(0);
                    return pointBalanceRepository.save(newBalance);
                });

        // 检查余额是否足够
        if (balance.getBalance() < amount) {
            return false;
        }

        // 更新余额
        balance.setBalance(balance.getBalance() - amount);
        pointBalanceRepository.save(balance);

        // 记录积分变动
        PointRecord record = new PointRecord();
        record.setUserId(userId);
        record.setType("spent");
        record.setAmount(amount);
        record.setRelatedId(relatedId);
        record.setRelatedType(relatedType);
        record.setDescription(description);
        pointRecordRepository.save(record);

        return true;
    }

    public PointBalance getBalance(UUID userId) {
        return pointBalanceRepository.findByUserId(userId)
                .orElseGet(() -> {
                    PointBalance newBalance = new PointBalance();
                    newBalance.setUserId(userId);
                    newBalance.setBalance(0);
                    return pointBalanceRepository.save(newBalance);
                });
    }
}