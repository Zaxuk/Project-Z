package com.zclub.modules.auth.controller;

import com.zclub.modules.auth.entity.User;
import com.zclub.modules.auth.service.AuthService;
import com.zclub.libs.JwtUtil;
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

    @Autowired
    private JwtUtil jwtUtil;

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody User user) {
        try {
            User registeredUser = authService.register(user);
            
            // 生成JWT Token
            String token = jwtUtil.generateToken(
                registeredUser.getId(), 
                registeredUser.getEmail(), 
                registeredUser.getRole()
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("user", registeredUser);
            response.put("token", token);
            
            return new ResponseEntity<>(response, HttpStatus.CREATED);
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
                    // 生成JWT Token
                    String token = jwtUtil.generateToken(
                        user.getId(), 
                        user.getEmail(), 
                        user.getRole()
                    );
                    
                    Map<String, Object> response = new HashMap<>();
                    response.put("user", user);
                    response.put("token", token);
                    
                    return new ResponseEntity<>(response, HttpStatus.OK);
                })
                .orElseGet(() -> {
                    Map<String, Object> errorMap = new HashMap<>();
                    errorMap.put("error", "Invalid credentials");
                    return new ResponseEntity<>(errorMap, HttpStatus.UNAUTHORIZED);
                });
    }
    
    @GetMapping("/verify")
    public ResponseEntity<?> verifyToken(@RequestHeader("Authorization") String authHeader) {
        try {
            String token = authHeader.replace("Bearer ", "");
            if (jwtUtil.validateToken(token)) {
                Map<String, Object> response = new HashMap<>();
                response.put("valid", true);
                response.put("userId", jwtUtil.getUserIdFromToken(token));
                response.put("email", jwtUtil.getEmailFromToken(token));
                response.put("role", jwtUtil.getRoleFromToken(token));
                return new ResponseEntity<>(response, HttpStatus.OK);
            } else {
                Map<String, Object> errorMap = new HashMap<>();
                errorMap.put("error", "Invalid token");
                return new ResponseEntity<>(errorMap, HttpStatus.UNAUTHORIZED);
            }
        } catch (Exception e) {
            Map<String, Object> errorMap = new HashMap<>();
            errorMap.put("error", "Token verification failed");
            return new ResponseEntity<>(errorMap, HttpStatus.UNAUTHORIZED);
        }
    }
}
