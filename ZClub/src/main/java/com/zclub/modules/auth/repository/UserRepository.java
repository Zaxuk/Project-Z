package com.zclub.modules.auth.repository;

import com.zclub.modules.auth.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByEmail(String email);
    Optional<User> findByPhone(String phone);
    Iterable<User> findByFamilyId(UUID familyId);
}