#!/usr/bin/env python3
"""测试需求#11460的任务数量查询"""

import sys
sys.path.insert(0, '.')

from src.zentao.api_client import ZentaoApiClient
from src.utils.config_loader import get_config
import json

def main():
    # 创建API客户端（从配置加载）
    client = ZentaoApiClient()
    config = get_config()
    base_url = config.get_zentao_config().get('base_url', '').rstrip('/')
    
    # 检查会话状态
    print('=' * 60)
    print('检查会话状态:')
    print('=' * 60)
    
    # 尝试访问我的首页
    url = f"{base_url}/my-index.html"
    response = client.session.get(url, timeout=30, allow_redirects=False)
    print(f"访问 my-index.html 状态码: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        if 'user-login' in response.url:
            print("会话已过期，需要重新登录")
        else:
            print("会话有效")
            # 检查cookies
            print(f"\n当前cookies: {dict(client.session.cookies)}")
    
    # 尝试重新登录
    print('\n' + '=' * 60)
    print('尝试重新登录:')
    print('=' * 60)
    
    username = config.get_zentao_config().get('username')
    password = config.get_zentao_config().get('password')
    
    # 先获取登录页面
    login_url = f"{base_url}/user-login.html"
    response = client.session.get(login_url, timeout=30)
    print(f"获取登录页面状态码: {response.status_code}")
    
    # 提交登录
    login_post_url = f"{base_url}/user-login.html"
    data = {
        'account': username,
        'password': password,
        'keepLogin': 'on'
    }
    response = client.session.post(login_post_url, data=data, timeout=30)
    print(f"登录提交状态码: {response.status_code}")
    print(f"登录后URL: {response.url}")
    
    if 'user-login' not in response.url:
        print("登录成功！")
        
        # 再次尝试获取需求详情
        print('\n' + '=' * 60)
        print('再次获取需求#11460详情:')
        print('=' * 60)
        
        url = f"{base_url}/story-view-11460.json"
        response = client.session.get(url, timeout=30)
        response.encoding = 'utf-8'
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"响应状态: {result.get('status')}")
                
                if result.get('status') == 'success' and 'data' in result:
                    story_data = json.loads(result['data'])
                    print(f"数据键: {list(story_data.keys())}")
                    print(f"\n完整数据:\n{json.dumps(story_data, ensure_ascii=False, indent=2)[:2000]}")
            except Exception as e:
                print(f"解析失败: {e}")
                print(f"响应内容: {response.text[:500]}")
    else:
        print("登录失败")

if __name__ == '__main__':
    main()
