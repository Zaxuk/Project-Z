package com.zclub.controller;

import com.zclub.model.Reward;
import com.zclub.service.RewardService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/rewards")
public class RewardController {
    @Autowired
    private RewardService rewardService;

    @PostMapping
    public ResponseEntity<?> createReward(@RequestBody Reward reward) {
        try {
            Reward createdReward = rewardService.createReward(reward);
            return new ResponseEntity<>(createdReward, HttpStatus.CREATED);
        } catch (Exception e) {
            Map<String, String> errorMap = new HashMap<>();
            errorMap.put("error", e.getMessage());
            return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
        }
    }

    @GetMapping("/family/{familyId}")
    public ResponseEntity<?> getRewardsByFamilyId(@PathVariable UUID familyId) {
        return new ResponseEntity<>(rewardService.getRewardsByFamilyId(familyId), HttpStatus.OK);
    }

    @GetMapping("/default")
    public ResponseEntity<?> getDefaultRewards() {
        return new ResponseEntity<>(rewardService.getDefaultRewards(), HttpStatus.OK);
    }

    @PostMapping("/{id}/redeem")
    public ResponseEntity<?> redeemReward(@PathVariable UUID id, @RequestBody Map<String, UUID> request) {
        UUID userId = request.get("userId");
        try {
            boolean success = rewardService.redeemReward(userId, id);
            if (success) {
                Map<String, Boolean> successMap = new HashMap<>();
                successMap.put("success", true);
                return new ResponseEntity<>(successMap, HttpStatus.OK);
            } else {
                Map<String, String> errorMap = new HashMap<>();
                errorMap.put("error", "Insufficient points");
                return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
            }
        } catch (Exception e) {
            Map<String, String> errorMap = new HashMap<>();
            errorMap.put("error", e.getMessage());
            return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
        }
    }

    @GetMapping("/redemptions/{userId}")
    public ResponseEntity<?> getRedemptionsByUserId(@PathVariable UUID userId) {
        return new ResponseEntity<>(rewardService.getRedemptionsByUserId(userId), HttpStatus.OK);
    }
}
