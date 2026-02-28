@echo off
chcp 65001 >nul
echo Testing API...

echo.
echo 1. Register new user
curl -s -X POST http://localhost:8081/api/auth/register -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"email\":\"testuser@example.com\",\"password\":\"password123\",\"role\":\"parent\"}"

echo.
echo.
echo 2. Login
curl -s -X POST http://localhost:8081/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"testuser@example.com\",\"password\":\"password123\"}"

echo.
echo.
echo Done!
pause
