package com.zclub.security;

import com.zclub.model.User;
import com.zclub.service.AuthService;
import com.zclub.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Collections;
import java.util.Optional;
import java.util.UUID;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private AuthService authService;

    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                    HttpServletResponse response, 
                                    FilterChain filterChain) throws ServletException, IOException {
        
        // 获取请求头中的Authorization
        String authHeader = request.getHeader("Authorization");
        System.out.println("JWT Filter - Request URI: " + request.getRequestURI());
        System.out.println("JWT Filter - Authorization Header: " + (authHeader != null ? authHeader.substring(0, Math.min(50, authHeader.length())) + "..." : "null"));
        
        // 如果没有Authorization头，或者不是Bearer token，直接放行
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            System.out.println("JWT Filter - No Bearer token found, skipping");
            filterChain.doFilter(request, response);
            return;
        }
        
        // 提取token
        String token = authHeader.substring(7);
        
        try {
            // 验证token
            boolean isValid = jwtUtil.validateToken(token);
            System.out.println("JWT Filter - Token valid: " + isValid);
            
            if (isValid) {
                // 从token中获取用户ID
                UUID userId = jwtUtil.getUserIdFromToken(token);
                String email = jwtUtil.getEmailFromToken(token);
                String role = jwtUtil.getRoleFromToken(token);
                
                System.out.println("JWT Filter - UserId from token: " + userId);
                System.out.println("JWT Filter - Email from token: " + email);
                System.out.println("JWT Filter - Role from token: " + role);
                
                // 从数据库查询用户获取完整的用户信息（包括familyId）
                System.out.println("JWT Filter - Querying user from DB with userId: " + userId);
                Optional<User> userOpt = authService.findUserById(userId);
                System.out.println("JWT Filter - User found: " + userOpt.isPresent());
                
                if (!userOpt.isPresent()) {
                    System.out.println("JWT Filter - WARNING: User not found in database for userId: " + userId);
                    System.out.println("JWT Filter - Clearing SecurityContext and returning 401");
                    SecurityContextHolder.clearContext();
                    response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                    response.getWriter().write("{\"error\":\"User not found. Please login again.\"}");
                    return;
                }
                
                User user = userOpt.get();
                System.out.println("JWT Filter - User from DB: id=" + user.getId() + ", email=" + user.getEmail() + ", familyId=" + user.getFamilyId());
                
                UUID familyId = user.getFamilyId();
                System.out.println("JWT Filter - FamilyId from DB: " + familyId);
                
                if (familyId == null) {
                    System.out.println("JWT Filter - WARNING: familyId is null! This will cause Task creation to fail.");
                }
                
                // 创建UserPrincipal
                UserPrincipal userPrincipal = new UserPrincipal(
                    userId,
                    email,
                    role,
                    familyId,
                    Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role.toUpperCase()))
                );
                
                // 创建认证对象
                UsernamePasswordAuthenticationToken authentication = 
                    new UsernamePasswordAuthenticationToken(
                        userPrincipal, 
                        null, 
                        userPrincipal.getAuthorities()
                    );
                
                authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                
                // 设置安全上下文
                SecurityContextHolder.getContext().setAuthentication(authentication);
                System.out.println("JWT Filter - Authentication set in SecurityContext");
            }
        } catch (Exception e) {
            System.out.println("JWT Filter - Token validation failed: " + e.getMessage());
            logger.error("JWT Token验证失败: " + e.getMessage());
        }
        
        filterChain.doFilter(request, response);
    }
}
