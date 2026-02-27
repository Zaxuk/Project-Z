package com.zclub.controller;

import com.zclub.model.PointBalance;
import com.zclub.repository.PointRecordRepository;
import com.zclub.service.PointService;
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
