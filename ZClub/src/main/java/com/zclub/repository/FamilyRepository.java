package com.zclub.repository;

import com.zclub.model.Family;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface FamilyRepository extends JpaRepository<Family, UUID> {
}