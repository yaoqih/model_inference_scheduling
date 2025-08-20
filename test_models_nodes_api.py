# -*- coding: utf-8 -*-
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_models_api():
    print("Testing Models API...")
    
    # First create an environment for testing
    import time
    timestamp = str(int(time.time()))
    env_data = {
        "name": f"Test Environment for Models {timestamp}",
        "description": "Test environment"
    }
    
    try:
        env_response = requests.post(f"{BASE_URL}/environments/", json=env_data)
        if env_response.status_code == 200:
            env_result = env_response.json()
            if env_result.get('success'):
                env_id = env_result['data']['id']
                print(f"Created test environment with ID: {env_id}")
            else:
                print("Failed to create test environment")
                return False
        else:
            print(f"Failed to create environment: {env_response.text}")
            return False
    except Exception as e:
        print(f"Error creating environment: {e}")
        return False
    
    # Test create model
    model_data = {
        "environment_id": env_id,
        "model_name": "Test Model",
        "inference_time": 1.5,
        "username": "test_user",
        "password": "test_pass",
        "port": 8080,
        "queue_name": "test_model_queue",
        "rabbitmq_host": "localhost",
        "rabbitmq_port": 5672,
        "rabbitmq_username": "guest",
        "rabbitmq_password": "guest",
        "rabbitmq_vhost": "/"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/models/", json=model_data)
        print(f"Create model status: {response.status_code}")
        
        if response.status_code == 200:
            model_result = response.json()
            print(f"Created model: {model_result}")
            
            if model_result.get('success'):
                model_id = model_result['data']['id']
                
                # Test get all models
                get_response = requests.get(f"{BASE_URL}/models/")
                print(f"Get all models status: {get_response.status_code}")
                
                # Test get model by ID
                get_one_response = requests.get(f"{BASE_URL}/models/{model_id}")
                print(f"Get model by ID status: {get_one_response.status_code}")
                
                # Test update model
                update_data = {
                    "model_name": "Updated Test Model",
                    "inference_time": 2.0,
                    "username": "updated_user",
                    "password": "updated_pass",
                    "port": 8081,
                    "queue_name": "updated_test_queue",
                    "rabbitmq_host": "localhost",
                    "rabbitmq_port": 5672,
                    "rabbitmq_username": "guest",
                    "rabbitmq_password": "guest",
                    "rabbitmq_vhost": "/"
                }
                update_response = requests.put(f"{BASE_URL}/models/{model_id}", json=update_data)
                print(f"Update model status: {update_response.status_code}")
                
                # Test delete model
                delete_response = requests.delete(f"{BASE_URL}/models/{model_id}")
                print(f"Delete model status: {delete_response.status_code}")
                
                # Clean up environment
                requests.delete(f"{BASE_URL}/environments/{env_id}")
                
                return True
        else:
            print(f"Create model failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error in model operations: {e}")
        return False

def test_nodes_api():
    print("Testing Nodes API...")
    
    # First create an environment for testing
    import time
    timestamp = str(int(time.time()))
    env_data = {
        "name": f"Test Environment for Nodes {timestamp}",
        "description": "Test environment"
    }
    
    try:
        env_response = requests.post(f"{BASE_URL}/environments/", json=env_data)
        if env_response.status_code == 200:
            env_result = env_response.json()
            if env_result.get('success'):
                env_id = env_result['data']['id']
                print(f"Created test environment with ID: {env_id}")
            else:
                print("Failed to create test environment")
                return False
        else:
            print(f"Failed to create environment: {env_response.text}")
            return False
    except Exception as e:
        print(f"Error creating environment: {e}")
        return False
    
    # Test create node
    node_data = {
        "environment_id": env_id,
        "node_ip": "192.168.1.100",
        "node_port": 6004,
        "available_gpu_ids": ["0", "1"],
        "available_models": ["test_model"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/nodes/", json=node_data)
        print(f"Create node status: {response.status_code}")
        
        if response.status_code == 200:
            node_result = response.json()
            print(f"Created node: {node_result}")
            
            if node_result.get('success'):
                node_id = node_result['data']['id']
                
                # Test get all nodes
                get_response = requests.get(f"{BASE_URL}/nodes/")
                print(f"Get all nodes status: {get_response.status_code}")
                
                # Test get node by ID
                get_one_response = requests.get(f"{BASE_URL}/nodes/{node_id}")
                print(f"Get node by ID status: {get_one_response.status_code}")
                
                # Test update node
                update_data = {
                    "node_ip": "192.168.1.101",
                    "node_port": 6005,
                    "available_gpu_ids": ["0"],
                    "available_models": ["updated_model"]
                }
                update_response = requests.put(f"{BASE_URL}/nodes/{node_id}", json=update_data)
                print(f"Update node status: {update_response.status_code}")
                
                # Test delete node
                delete_response = requests.delete(f"{BASE_URL}/nodes/{node_id}")
                print(f"Delete node status: {delete_response.status_code}")
                
                # Clean up environment
                requests.delete(f"{BASE_URL}/environments/{env_id}")
                
                return True
        else:
            print(f"Create node failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error in node operations: {e}")
        return False

if __name__ == "__main__":
    print("Starting Models and Nodes API tests...")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/environments/")
        print("Backend is running")
    except Exception as e:
        print(f"Backend not accessible: {e}")
        exit(1)
    
    success1 = test_models_api()
    success2 = test_nodes_api()
    
    if success1 and success2:
        print("All tests passed!")
    else:
        print("Some tests failed!")