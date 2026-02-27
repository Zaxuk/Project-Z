package com.zclub.controller;

import com.zclub.model.Task;
import com.zclub.model.TaskCompletion;
import com.zclub.repository.TaskRepository;
import com.zclub.repository.TaskCompletionRepository;
import com.zclub.security.UserPrincipal;
import com.zclub.service.PointService;
import com.zclub.service.NotificationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {
    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private TaskCompletionRepository taskCompletionRepository;

    @Autowired
    private PointService pointService;

    @Autowired
    private NotificationService notificationService;

    @PostMapping
    public ResponseEntity<?> createTask(@RequestBody Task task) {
        try {
            System.out.println("TaskController - createTask called");
            System.out.println("TaskController - Received task: title=" + task.getTitle() + ", description=" + task.getDescription());
            
            // 从SecurityContext获取当前登录用户信息
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            System.out.println("TaskController - Authentication: " + authentication);
            if (authentication != null) {
                System.out.println("TaskController - Principal: " + authentication.getPrincipal());
                System.out.println("TaskController - Principal type: " + (authentication.getPrincipal() != null ? authentication.getPrincipal().getClass().getName() : "null"));
                System.out.println("TaskController - Is authenticated: " + authentication.isAuthenticated());
            }
            
            if (authentication != null && authentication.getPrincipal() instanceof UserPrincipal) {
                UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();
                System.out.println("TaskController - UserPrincipal found - userId: " + userPrincipal.getUserId() + ", familyId: " + userPrincipal.getFamilyId());
                
                // 自动设置familyId和createdBy
                UUID familyId = userPrincipal.getFamilyId();
                UUID userId = userPrincipal.getUserId();
                
                System.out.println("TaskController - Setting familyId: " + familyId);
                System.out.println("TaskController - Setting createdBy: " + userId);
                
                if (familyId == null) {
                    System.out.println("TaskController - ERROR: familyId is null! Cannot create task.");
                    Map<String, String> errorMap = new HashMap<>();
                    errorMap.put("error", "User familyId is null. Please contact administrator.");
                    return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
                }
                
                task.setFamilyId(familyId);
                task.setCreatedBy(userId);
            } else {
                System.out.println("TaskController - ERROR: UserPrincipal not found in SecurityContext");
                Map<String, String> errorMap = new HashMap<>();
                errorMap.put("error", "User not authenticated");
                return new ResponseEntity<>(errorMap, HttpStatus.UNAUTHORIZED);
            }
            
            // 设置默认值
            if (task.getStatus() == null) {
                task.setStatus("pending");
            }
            if (task.getRecurrenceStatus() == null) {
                task.setRecurrenceStatus("non_recurring");
            }
            Task createdTask = taskRepository.save(task);
            return new ResponseEntity<>(createdTask, HttpStatus.CREATED);
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, String> errorMap = new HashMap<>();
            errorMap.put("error", e.getMessage());
            return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
        }
    }

    @GetMapping("/family/{familyId}")
    public ResponseEntity<?> getTasksByFamilyId(@PathVariable UUID familyId) {
        return new ResponseEntity<>(taskRepository.findByFamilyId(familyId), HttpStatus.OK);
    }

    @PostMapping("/{id}/complete")
    public ResponseEntity<?> completeTask(@PathVariable UUID id, @RequestBody Map<String, UUID> request) {
        UUID userId = request.get("userId");
        try {
            Task task = taskRepository.findById(id).orElse(null);
            if (task == null) {
                Map<String, String> errorMap = new HashMap<>();
                errorMap.put("error", "Task not found");
                return new ResponseEntity<>(errorMap, HttpStatus.NOT_FOUND);
            }

            // 创建任务完成记录
            TaskCompletion completion = new TaskCompletion();
            completion.setTaskId(id);
            completion.setUserId(userId);
            completion.setStatus("pending_approval");
            completion.setPointsEarned(task.getPointsReward());
            taskCompletionRepository.save(completion);

            // 发送通知给家长
            // 这里简化处理，实际应该获取家庭中的家长用户
            notificationService.sendNotification(
                    task.getCreatedBy(),
                    "task_completed",
                    "任务完成申请",
                    "有新的任务完成申请需要审批",
                    id,
                    "task"
            );

            return new ResponseEntity<>(completion, HttpStatus.CREATED);
        } catch (Exception e) {
            Map<String, String> errorMap = new HashMap<>();
            errorMap.put("error", e.getMessage());
            return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
        }
    }

    @PostMapping("/completions/{id}/approve")
    public ResponseEntity<?> approveTaskCompletion(@PathVariable UUID id, @RequestBody Map<String, Object> request) {
        UUID approvalLevelId = (UUID) request.get("approvalLevelId");
        Double multiplier = (Double) request.get("multiplier");
        UUID approvedBy = (UUID) request.get("approvedBy");

        try {
            TaskCompletion completion = taskCompletionRepository.findById(id).orElse(null);
            if (completion == null) {
                Map<String, String> errorMap = new HashMap<>();
                errorMap.put("error", "Task completion not found");
                return new ResponseEntity<>(errorMap, HttpStatus.NOT_FOUND);
            }

            // 更新任务完成状态
            completion.setStatus("completed");
            completion.setApprovalLevelId(approvalLevelId);
            completion.setApprovedBy(approvedBy);

            // 计算最终积分
            Task task = taskRepository.findById(completion.getTaskId()).orElse(null);
            if (task != null) {
                int finalPoints = (int) (task.getPointsReward() * multiplier);
                completion.setPointsEarned(finalPoints);
            }

            taskCompletionRepository.save(completion);

            // 发放积分
            pointService.addPoints(
                    completion.getUserId(),
                    completion.getPointsEarned(),
                    completion.getId(),
                    "task_completion",
                    "任务完成奖励"
            );

            // 发送通知给孩子
            notificationService.sendNotification(
                    completion.getUserId(),
                    "point_earned",
                    "积分到账",
                    "任务审批通过，获得 " + completion.getPointsEarned() + " 积分",
                    completion.getId(),
                    "task_completion"
            );

            return new ResponseEntity<>(completion, HttpStatus.OK);
        } catch (Exception e) {
            Map<String, String> errorMap = new HashMap<>();
            errorMap.put("error", e.getMessage());
            return new ResponseEntity<>(errorMap, HttpStatus.BAD_REQUEST);
        }
    }
}
