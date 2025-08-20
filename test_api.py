#!/usr/bin/env python3
"""
API测试脚本
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("[TEST] 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] 健康检查失败: {e}")
        return False

def test_get_environments():
    """测试获取环境列表"""
    print("\n[TEST] 测试获取环境列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/environments/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] 获取环境列表失败: {e}")
        return False

def test_create_environment():
    """测试创建环境"""
    print("\n[TEST] 测试创建环境...")
    try:
        data = {
            "name": "测试环境",
            "description": "这是一个测试环境"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/environments/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] 创建环境失败: {e}")
        return False

def test_get_models():
    """测试获取模型列表"""
    print("\n[TEST] 测试获取模型列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/models/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] 获取模型列表失败: {e}")
        return False

def test_get_nodes():
    """测试获取节点列表"""
    print("\n[TEST] 测试获取节点列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/nodes/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] 获取节点列表失败: {e}")
        return False

def test_batch_health_check():
    """测试批量健康检查"""
    print("\n[TEST] 测试批量健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/node-operations/batch/health-check")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] 批量健康检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("[START] 开始API测试...")
    
    tests = [
        ("健康检查", test_health),
        ("获取环境列表", test_get_environments),
        ("创建环境", test_create_environment),
        ("获取模型列表", test_get_models),
        ("获取节点列表", test_get_nodes),
        ("批量健康检查", test_batch_health_check),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"[PASS] {test_name} - 通过")
                passed += 1
            else:
                print(f"[FAIL] {test_name} - 失败")
        except Exception as e:
            print(f"[ERROR] {test_name} - 异常: {e}")
    
    print(f"\n[RESULT] 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("[SUCCESS] 所有测试通过！")
        return 0
    else:
        print("[WARNING] 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())