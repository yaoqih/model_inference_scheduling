"""
节点API客户端
用于与Model Inference Client API进行通信
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from ..schemas.node import GPUInfo, ModelInstanceInfo
import logging

logger = logging.getLogger(__name__)

class NodeAPIClient:
    """节点API客户端"""
    
    def __init__(self, node_ip: str, node_port: int = 6004, timeout: float = 30.0):
        self.node_ip = node_ip
        self.node_port = node_port
        self.base_url = f"http://{node_ip}:{node_port}"
        self.timeout = timeout
        self._client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """关闭客户端连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def health_check(self) -> bool:
        """节点健康检查"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"节点 {self.node_ip}:{self.node_port} 健康检查失败: {e}")
            return False
    
    async def get_gpu_status(self) -> List[Dict[str, Any]]:
        """获取GPU状态信息"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/v1/gpus")
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.warning(f"获取节点 {self.node_ip}:{self.node_port} GPU状态失败或不支持: {e}")
            # 即使失败，也返回一个带默认值的结构，以便前端处理
            return []
        except Exception as e:
            logger.error(f"获取节点 {self.node_ip}:{self.node_port} GPU状态时发生未知错误: {e}")
            return []
    
    async def get_model_status(self) -> List[Dict[str, Any]]:
        """获取所有运行中模型的状态"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/v1/models/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取节点 {self.node_ip}:{self.node_port} 模型状态失败: {e}")
            raise
    
    async def get_model_status_by_name(self, model_name: str) -> List[Dict[str, Any]]:
        """获取指定模型的状态"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/v1/models/status/{model_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取节点 {self.node_ip}:{self.node_port} 模型 {model_name} 状态失败: {e}")
            raise
    
    async def start_model(self, model_name: str, gpu_id: int, config: Optional[Dict] = None) -> Dict[str, Any]:
        """在指定GPU上启动模型"""
        try:
            client = await self._get_client()
            payload = {
                "model_name": model_name,
                "gpu_id": gpu_id,
                "config": config or {}
            }
            response = await client.post(
                f"{self.base_url}/api/v1/models/start",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"在节点 {self.node_ip}:{self.node_port} 启动模型 {model_name} 失败: {e}")
            raise
    
    async def stop_model(self, model_name: str, gpu_id: int) -> Dict[str, Any]:
        """在指定GPU上停止模型"""
        try:
            client = await self._get_client()
            payload = {
                "model_name": model_name,
                "gpu_id": gpu_id
            }
            response = await client.post(
                f"{self.base_url}/api/v1/models/stop",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"在节点 {self.node_ip}:{self.node_port} 停止模型 {model_name} 失败: {e}")
            raise
    
    async def kill_process(self, pid: int) -> Dict[str, Any]:
        """通过PID终止进程"""
        try:
            client = await self._get_client()
            response = await client.delete(f"{self.base_url}/api/v1/processes/{pid}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"在节点 {self.node_ip}:{self.node_port} 终止进程 {pid} 失败: {e}")
            raise

    async def get_supported_models(self) -> Dict[str, str]:
        """获取节点支持的模型列表"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/v1/models/supported")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取节点 {self.node_ip}:{self.node_port} 支持的模型列表失败: {e}")
            raise

class NodeManager:
    """节点管理器"""
    
    def __init__(self):
        self._clients: Dict[str, NodeAPIClient] = {}
    
    def get_client(self, node_ip: str, node_port: int = 6004) -> NodeAPIClient:
        """获取节点客户端"""
        key = f"{node_ip}:{node_port}"
        if key not in self._clients:
            self._clients[key] = NodeAPIClient(node_ip, node_port)
        return self._clients[key]
    
    async def close_all(self):
        """关闭所有客户端连接"""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()
    
    async def batch_health_check(self, nodes: List[Dict[str, Any]]) -> Dict[str, bool]:
        """批量健康检查"""
        tasks = []
        node_keys = []
        
        for node in nodes:
            node_ip = node["node_ip"]
            node_port = node.get("node_port", 6004)
            client = self.get_client(node_ip, node_port)
            tasks.append(client.health_check())
            node_keys.append(f"{node_ip}:{node_port}")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_status = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                health_status[node_keys[i]] = False
            else:
                health_status[node_keys[i]] = result
        
        return health_status
    
    async def batch_get_gpu_status(self, nodes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """批量获取GPU状态"""
        tasks = []
        node_keys = []
        
        for node in nodes:
            node_ip = node["node_ip"]
            node_port = node.get("node_port", 6004)
            client = self.get_client(node_ip, node_port)
            tasks.append(client.get_gpu_status())
            node_keys.append(f"{node_ip}:{node_port}")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        gpu_status = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                gpu_status[node_keys[i]] = []
            else:
                gpu_status[node_keys[i]] = result
        
        return gpu_status
    
    async def batch_get_model_status(self, nodes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """批量获取模型状态"""
        tasks = []
        node_keys = []
        
        for node in nodes:
            node_ip = node["node_ip"]
            node_port = node.get("node_port", 6004)
            client = self.get_client(node_ip, node_port)
            tasks.append(client.get_model_status())
            node_keys.append(f"{node_ip}:{node_port}")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        model_status = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                model_status[node_keys[i]] = []
            else:
                model_status[node_keys[i]] = result
        
        return model_status

    async def batch_get_status(self, nodes: List[Dict[str, Any]]) -> (Dict[str, list], Dict[str, list]):
        """批量获取模型和GPU状态"""
        model_tasks = []
        gpu_tasks = []
        node_keys = []

        for node in nodes:
            node_ip = node["node_ip"]
            node_port = node.get("node_port", 6004)
            client = self.get_client(node_ip, node_port)
            model_tasks.append(client.get_model_status())
            gpu_tasks.append(client.get_gpu_status())
            node_keys.append(f"{node_ip}:{node_port}")

        model_results = await asyncio.gather(*model_tasks, return_exceptions=True)
        gpu_results = await asyncio.gather(*gpu_tasks, return_exceptions=True)

        model_status_map = {}
        gpu_status_map = {}

        for i, key in enumerate(node_keys):
            model_status_map[key] = model_results[i] if not isinstance(model_results[i], Exception) else []
            gpu_status_map[key] = gpu_results[i] if not isinstance(gpu_results[i], Exception) else []
            
        return model_status_map, gpu_status_map

# 全局节点管理器实例
node_manager = NodeManager()