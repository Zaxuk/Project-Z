package com.zclub.modules.notification.repository;

import com.zclub.modules.notification.entity.Notification;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface NotificationRepository extends JpaRepository<Notification, UUID> {
    Iterable<Notification> findByUserId(UUID userId);
    Iterable<Notification> findByUserIdAndReadStatus(UUID userId, String readStatus);
}