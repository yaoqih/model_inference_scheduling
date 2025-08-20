# -*- coding: utf-8 -*-
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_environment_api():
    print("Testing Environment API...")
    
    # Test create environment
    create_data = {
        "name": "Test Environment",
        "description": "Test description"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/environments/", json=create_data)
        print(f"Create status: {response.status_code}")
        
        if response.status_code == 200:
            env_data = response.json()
            print(f"Created environment: {env_data}")
            env_id = env_data.get('id')
            
            if env_id:
                # Test get environment
                get_response = requests.get(f"{BASE_URL}/environments/{env_id}")
                print(f"Get status: {get_response.status_code}")
                
                # Test update environment
                update_data = {"name": "Updated Environment", "description": "Updated description"}
                update_response = requests.put(f"{BASE_URL}/environments/{env_id}", json=update_data)
                print(f"Update status: {update_response.status_code}")
                
                # Test delete environment
                delete_response = requests.delete(f"{BASE_URL}/environments/{env_id}")
                print(f"Delete status: {delete_response.status_code}")
                
                return True
        else:
            print(f"Create failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_all_environments():
    print("Testing get all environments...")
    try:
        response = requests.get(f"{BASE_URL}/environments/")
        print(f"Get all status: {response.status_code}")
        if response.status_code == 200:
            envs = response.json()
            print(f"Found {len(envs)} environments")
            return True
        else:
            print(f"Failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting API tests...")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/environments/")
        print("Backend is running")
    except Exception as e:
        print(f"Backend not accessible: {e}")
        exit(1)
    
    success1 = test_get_all_environments()
    success2 = test_environment_api()
    
    if success1 and success2:
        print("All tests passed!")
    else:
        print("Some tests failed!")