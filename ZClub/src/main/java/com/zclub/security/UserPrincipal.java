package com.zclub.security;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.UUID;

/**
 * 自定义用户认证信息类
 * 存储在SecurityContext中，方便在整个请求生命周期中获取用户信息
 */
public class UserPrincipal implements UserDetails {
    
    private final UUID userId;
    private final String email;
    private final String role;
    private final UUID familyId;
    private final Collection<? extends GrantedAuthority> authorities;
    
    public UserPrincipal(UUID userId, String email, String role, UUID familyId, 
                         Collection<? extends GrantedAuthority> authorities) {
        this.userId = userId;
        this.email = email;
        this.role = role;
        this.familyId = familyId;
        this.authorities = authorities;
    }
    
    public UUID getUserId() {
        return userId;
    }
    
    public String getEmail() {
        return email;
    }
    
    public String getRole() {
        return role;
    }
    
    public UUID getFamilyId() {
        return familyId;
    }
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return authorities;
    }
    
    @Override
    public String getPassword() {
        return null; // JWT认证不需要密码
    }
    
    @Override
    public String getUsername() {
        return email;
    }
    
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }
    
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }
    
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }
    
    @Override
    public boolean isEnabled() {
        return true;
    }
}
