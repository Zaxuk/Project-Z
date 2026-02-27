# Test API script - 测试后端自动获取familyId

# 1. Register new user
Write-Host "=== Testing Register API ===" -ForegroundColor Green
$registerBody = @{
    name = "Test User2"
    email = "test4@example.com"
    password = "123456"
    role = "admin"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8081/api/auth/register" -Method POST -ContentType "application/json" -Body $registerBody
    Write-Host "Register success!" -ForegroundColor Green
    Write-Host "User ID: $($registerResponse.user.id)"
    Write-Host "FamilyID: $($registerResponse.user.familyId)"
    $token = $registerResponse.token
    $userFamilyId = $registerResponse.user.familyId
} catch {
    Write-Host "Register failed: $_" -ForegroundColor Red
    exit
}

# 2. Create task - 不传递familyId和createdBy，由后端自动获取
Write-Host "`n=== Testing Create Task API (without familyId) ===" -ForegroundColor Green
$taskBody = @{
    title = "Test Task Without FamilyId"
    description = "This task is created without passing familyId"
    pointsReward = 20
    taskType = "daily"
    status = "active"
    recurrenceStatus = "one_time"
    # 注意：没有传递familyId和createdBy
} | ConvertTo-Json

try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $taskResponse = Invoke-RestMethod -Uri "http://localhost:8081/api/tasks" -Method POST -ContentType "application/json" -Body $taskBody -Headers $headers
    Write-Host "Create task success!" -ForegroundColor Green
    Write-Host "Task ID: $($taskResponse.id)"
    Write-Host "Task Title: $($taskResponse.title)"
    Write-Host "Task FamilyId (auto-set by backend): $($taskResponse.familyId)"
    
    # 验证后端设置的familyId是否正确
    if ($taskResponse.familyId -eq $userFamilyId) {
        Write-Host "✓ FamilyId correctly set by backend!" -ForegroundColor Green
    } else {
        Write-Host "✗ FamilyId mismatch! Expected: $userFamilyId, Got: $($taskResponse.familyId)" -ForegroundColor Red
    }
} catch {
    Write-Host "Create task failed: $_" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
