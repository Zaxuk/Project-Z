package com.zclub.modules.auth.service;

import com.zclub.modules.family.entity.Family;
import com.zclub.modules.auth.entity.User;
import com.zclub.modules.family.repository.FamilyRepository;
import com.zclub.modules.auth.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import java.util.Optional;
import java.util.UUID;

@Service
public class AuthService {
    @Autowired
    private UserRepository userRepository;

    @Autowired
    private FamilyRepository familyRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public User register(User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        if (user.getStatus() == null) {
            user.setStatus("active");
        }
        // 如果没有familyId，自动生成一个
        if (user.getFamilyId() == null) {
            user.setFamilyId(UUID.randomUUID());
        }
        
        // 先保存用户，获取用户ID
        User savedUser = userRepository.save(user);
        
        // 创建对应的Family记录（使用保存后的用户ID）
        Family family = new Family();
        family.setId(savedUser.getFamilyId());
        family.setName(savedUser.getName() + "的家庭");
        family.setCreatedBy(savedUser.getId());
        familyRepository.save(family);
        
        return savedUser;
    }

    public Optional<User> login(String email, String password) {
        Optional<User> user = userRepository.findByEmail(email);
        if (user.isPresent() && passwordEncoder.matches(password, user.get().getPassword())) {
            return user;
        }
        return Optional.empty();
    }

    public Optional<User> findUserById(UUID id) {
        return userRepository.findById(id);
    }
}