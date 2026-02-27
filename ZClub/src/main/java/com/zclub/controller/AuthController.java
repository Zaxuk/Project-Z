package com.zclub.controller;

import com.zclub.model.User;
import com.zclub.service.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    @Autowired
    private AuthService authService;

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody User user) {
        try {
            User registeredUser = authService.register(user);
            return new ResponseEntity<>(registeredUser, HttpStatus.CREATED);
        } catch (Exception e) {
            Map<String, String> errorMap = new HashMap<>();
            errorMap.put("error", e.getMessage());
            return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> credentials) {
        String email = credentials.get("email");
        String password = credentials.get("password");

        return authService.login(email, password)
                .map(user -> {
                    Map<String, Object> userMap = new HashMap<>();
                    userMap.put("user", user);
                    return new ResponseEntity<>(userMap, HttpStatus.OK);
                })
                .orElseGet(() -> {
                    Map<String, Object> errorMap = new HashMap<>();
                    errorMap.put("error", "Invalid credentials");
                    return new ResponseEntity<>(errorMap, HttpStatus.UNAUTHORIZED);
                });
    }
}
