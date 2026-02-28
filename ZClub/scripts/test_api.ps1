# Test API script

# 1. Register new user
Write-Host "=== Testing Register API ===" -ForegroundColor Green
$registerBody = @{
    name = "Test User"
    email = "test3@example.com"
    password = "123456"
    role = "admin"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8081/api/auth/register" -Method POST -ContentType "application/json" -Body $registerBody
    Write-Host "Register success!" -ForegroundColor Green
    Write-Host "User ID: $($registerResponse.user.id)"
    Write-Host "FamilyID: $($registerResponse.user.familyId)"
    Write-Host "Token: $($registerResponse.token)"
    $token = $registerResponse.token
    $familyId = $registerResponse.user.familyId
} catch {
    Write-Host "Register failed: $_" -ForegroundColor Red
    exit
}

# 2. Create task
Write-Host "`n=== Testing Create Task API ===" -ForegroundColor Green
$taskBody = @{
    title = "Test Task"
    description = "This is a test task"
    pointsReward = 10
    taskType = "daily"
    status = "active"
    recurrenceStatus = "one_time"
    familyId = $familyId
    createdBy = $registerResponse.user.id
} | ConvertTo-Json

try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $taskResponse = Invoke-RestMethod -Uri "http://localhost:8081/api/tasks" -Method POST -ContentType "application/json" -Body $taskBody -Headers $headers
    Write-Host "Create task success!" -ForegroundColor Green
    Write-Host "Task ID: $($taskResponse.id)"
    Write-Host "Task Title: $($taskResponse.title)"
} catch {
    Write-Host "Create task failed: $_" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}

# 3. Get task list
Write-Host "`n=== Testing Get Task List API ===" -ForegroundColor Green
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $tasksResponse = Invoke-RestMethod -Uri "http://localhost:8081/api/tasks/family/$familyId" -Method GET -Headers $headers
    Write-Host "Get task list success!" -ForegroundColor Green
    Write-Host "Task count: $($tasksResponse.Count)"
} catch {
    Write-Host "Get task list failed: $_" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
