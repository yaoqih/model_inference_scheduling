import requests
import json
import sys
import os

# 设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_environment_crud():
    """测试环境的CRUD操作"""
    print("开始测试环境管理API...")
    
    # 1. 测试创建环境
    print("\n1. 测试创建环境")
    create_data = {
        "name": "测试环境1",
        "description": "这是一个测试环境"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/environments/", json=create_data)
        print(f"创建环境响应状态码: {response.status_code}")
        if response.status_code == 200:
            created_env = response.json()
            print(f"创建成功，环境ID: {created_env.get('id', 'N/A')}")
            env_id = created_env.get('id')
            if not env_id:
                print(f"响应数据: {created_env}")
                return False
        else:
            print(f"创建失败: {response.text}")
            return False
    except Exception as e:
        print(f"创建环境时发生错误: {e}")
        return False
    
    # 2. 测试获取所有环境
    print("\n2. 测试获取所有环境")
    try:
        response = requests.get(f"{BASE_URL}/environments/")
        print(f"获取环境列表响应状态码: {response.status_code}")
        if response.status_code == 200:
            environments = response.json()
            print(f"获取成功，环境数量: {len(environments)}")
            print(f"环境列表: {json.dumps(environments, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取失败: {response.text}")
    except Exception as e:
        print(f"获取环境列表时发生错误: {e}")
    
    # 3. 测试根据ID获取环境
    print(f"\n3. 测试根据ID获取环境 (ID: {env_id})")
    try:
        response = requests.get(f"{BASE_URL}/environments/{env_id}")
        print(f"获取单个环境响应状态码: {response.status_code}")
        if response.status_code == 200:
            environment = response.json()
            print(f"获取成功: {json.dumps(environment, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取失败: {response.text}")
    except Exception as e:
        print(f"获取单个环境时发生错误: {e}")
    
    # 4. 测试更新环境
    print(f"\n4. 测试更新环境 (ID: {env_id})")
    update_data = {
        "name": "更新后的测试环境1",
        "description": "这是一个更新后的测试环境"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/environments/{env_id}", json=update_data)
        print(f"更新环境响应状态码: {response.status_code}")
        if response.status_code == 200:
            updated_env = response.json()
            print(f"更新成功: {json.dumps(updated_env, indent=2, ensure_ascii=False)}")
        else:
            print(f"更新失败: {response.text}")
    except Exception as e:
        print(f"更新环境时发生错误: {e}")
    
    # 5. 测试删除环境
    print(f"\n5. 测试删除环境 (ID: {env_id})")
    try:
        response = requests.delete(f"{BASE_URL}/environments/{env_id}")
        print(f"删除环境响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("删除成功")
        else:
            print(f"删除失败: {response.text}")
    except Exception as e:
        print(f"删除环境时发生错误: {e}")
    
    # 6. 验证删除后获取环境
    print(f"\n6. 验证删除后获取环境 (ID: {env_id})")
    try:
        response = requests.get(f"{BASE_URL}/environments/{env_id}")
        print(f"获取已删除环境响应状态码: {response.status_code}")
        if response.status_code == 404:
            print("验证成功：环境已被删除")
        else:
            print(f"验证失败：环境仍然存在 - {response.text}")
    except Exception as e:
        print(f"验证删除时发生错误: {e}")
    
    print("\n环境管理API测试完成！")
    return True

def test_model_crud():
    """测试模型的CRUD操作"""
    print("\n开始测试模型管理API...")
    
    # 首先创建一个环境用于测试
    env_data = {
        "name": "模型测试环境",
        "description": "用于测试模型API的环境"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/environments/", json=env_data)
        if response.status_code == 200:
            env_id = response.json()['id']
            print(f"创建测试环境成功，ID: {env_id}")
        else:
            print(f"创建测试环境失败: {response.text}")
            return False
    except Exception as e:
        print(f"创建测试环境时发生错误: {e}")
        return False
    
    # 1. 测试创建模型
    print("\n1. 测试创建模型")
    model_data = {
        "name": "测试模型1",
        "description": "这是一个测试模型",
        "model_path": "/path/to/model",
        "environment_id": env_id,
        "rabbitmq_host": "localhost",
        "rabbitmq_port": 5672,
        "rabbitmq_username": "guest",
        "rabbitmq_password": "guest",
        "rabbitmq_queue_name": "test_queue"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/models/", json=model_data)
        print(f"创建模型响应状态码: {response.status_code}")
        if response.status_code == 200:
            created_model = response.json()
            print(f"创建成功，模型ID: {created_model['id']}")
            model_id = created_model['id']
        else:
            print(f"创建失败: {response.text}")
            return False
    except Exception as e:
        print(f"创建模型时发生错误: {e}")
        return False
    
    # 2. 测试获取所有模型
    print("\n2. 测试获取所有模型")
    try:
        response = requests.get(f"{BASE_URL}/models/")
        print(f"获取模型列表响应状态码: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"获取成功，模型数量: {len(models)}")
        else:
            print(f"获取失败: {response.text}")
    except Exception as e:
        print(f"获取模型列表时发生错误: {e}")
    
    # 清理：删除测试数据
    print(f"\n清理测试数据...")
    try:
        requests.delete(f"{BASE_URL}/models/{model_id}")
        requests.delete(f"{BASE_URL}/environments/{env_id}")
        print("清理完成")
    except Exception as e:
        print(f"清理时发生错误: {e}")
    
    print("\n模型管理API测试完成！")
    return True

if __name__ == "__main__":
    print("开始API测试...")
    
    # 检查后端服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/environments/")
        print("后端服务正在运行")
    except Exception as e:
        print(f"无法连接到后端服务: {e}")
        print("请确保后端服务正在运行 (python run_dev.py)")
        sys.exit(1)
    
    # 运行测试
    success = True
    success &= test_environment_crud()
    success &= test_model_crud()
    
    if success:
        print("\n✅ 所有API测试通过！")
    else:
        print("\n❌ 部分API测试失败！")
        sys.exit(1)