package com.zclub.service;

import com.zclub.model.Notification;
import com.zclub.repository.NotificationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.UUID;

@Service
public class NotificationService {
    @Autowired
    private NotificationRepository notificationRepository;

    public Notification sendNotification(UUID userId, String type, String title, String message, UUID relatedId, String relatedType) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setType(type);
        notification.setTitle(title);
        notification.setMessage(message);
        notification.setReadStatus("unread");
        notification.setRelatedId(relatedId);
        notification.setRelatedType(relatedType);
        return notificationRepository.save(notification);
    }

    public Iterable<Notification> getNotificationsByUserId(UUID userId) {
        return notificationRepository.findByUserId(userId);
    }

    public Iterable<Notification> getUnreadNotificationsByUserId(UUID userId) {
        return notificationRepository.findByUserIdAndReadStatus(userId, "unread");
    }

    public void markAsRead(UUID notificationId) {
        Notification notification = notificationRepository.findById(notificationId).orElse(null);
        if (notification != null) {
            notification.setReadStatus("read");
            notificationRepository.save(notification);
        }
    }
}