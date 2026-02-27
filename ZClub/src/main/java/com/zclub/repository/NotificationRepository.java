package com.zclub.repository;

import com.zclub.model.Notification;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface NotificationRepository extends JpaRepository<Notification, UUID> {
    Iterable<Notification> findByUserId(UUID userId);
    Iterable<Notification> findByUserIdAndReadStatus(UUID userId, String readStatus);
}