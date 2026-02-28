package com.zclub.libs;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.UUID;

@Component
public class JwtUtil {
    
    // JWT密钥，实际项目中应该从配置文件读取
    private static final String SECRET = "zclub-secret-key-for-jwt-authentication-2024";
    private static final SecretKey KEY = Keys.hmacShaKeyFor(SECRET.getBytes());
    
    // Token有效期：7天
    private static final long EXPIRATION = 7 * 24 * 60 * 60 * 1000;
    
    /**
     * 生成JWT Token
     */
    public String generateToken(UUID userId, String email, String role) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + EXPIRATION);
        
        return Jwts.builder()
                .setSubject(userId.toString())
                .claim("email", email)
                .claim("role", role)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(KEY, SignatureAlgorithm.HS256)
                .compact();
    }
    
    /**
     * 从Token中获取用户ID
     */
    public UUID getUserIdFromToken(String token) {
        Claims claims = parseToken(token);
        return UUID.fromString(claims.getSubject());
    }
    
    /**
     * 从Token中获取用户邮箱
     */
    public String getEmailFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.get("email", String.class);
    }
    
    /**
     * 从Token中获取用户角色
     */
    public String getRoleFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.get("role", String.class);
    }
    
    /**
     * 验证Token是否有效
     */
    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (ExpiredJwtException e) {
            System.err.println("Token已过期: " + e.getMessage());
        } catch (UnsupportedJwtException e) {
            System.err.println("不支持的Token: " + e.getMessage());
        } catch (MalformedJwtException e) {
            System.err.println("Token格式错误: " + e.getMessage());
        } catch (SignatureException e) {
            System.err.println("Token签名验证失败: " + e.getMessage());
        } catch (IllegalArgumentException e) {
            System.err.println("Token为空或非法: " + e.getMessage());
        }
        return false;
    }
    
    /**
     * 解析Token
     */
    private Claims parseToken(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(KEY)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }
    
    /**
     * 检查Token是否即将过期（1天内）
     */
    public boolean isTokenExpiringSoon(String token) {
        Claims claims = parseToken(token);
        Date expiration = claims.getExpiration();
        // 如果过期时间小于1天，则认为即将过期
        return expiration.getTime() - System.currentTimeMillis() < 24 * 60 * 60 * 1000;
    }
}