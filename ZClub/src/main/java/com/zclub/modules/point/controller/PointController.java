package com.zclub.modules.point.controller;

import com.zclub.modules.point.entity.PointBalance;
import com.zclub.modules.point.repository.PointRecordRepository;
import com.zclub.modules.point.service.PointService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;

@RestController
@RequestMapping("/api/points")
public class PointController {
    @Autowired
    private PointService pointService;

    @Autowired
    private PointRecordRepository pointRecordRepository;

    @GetMapping("/balance/{userId}")
    public ResponseEntity<?> getBalance(@PathVariable UUID userId) {
        PointBalance balance = pointService.getBalance(userId);
        return new ResponseEntity<>(balance, HttpStatus.OK);
    }

    @GetMapping("/records/{userId}")
    public ResponseEntity<?> getRecords(@PathVariable UUID userId) {
        return new ResponseEntity<>(pointRecordRepository.findByUserId(userId), HttpStatus.OK);
    }
}
