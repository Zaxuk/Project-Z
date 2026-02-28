package com.zclub.modules.family.repository;

import com.zclub.modules.family.entity.Family;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface FamilyRepository extends JpaRepository<Family, UUID> {
}