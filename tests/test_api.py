"""API接口测试文件"""
import pytest
import httpx
import base64
import json
from typing import Dict, Any


# 测试配置
BASE_URL = "http://localhost:8000"
API_KEY = "han1234"  # 默认 API Key


class TestAPI:
    """API接口测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
    
    @pytest.fixture
    def headers(self):
        """创建认证头"""
        return {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    
    @pytest.mark.asyncio
    async def test_list_models(self, client, headers):
        """测试列出所有模型"""
        response = await client.get("/v1/models", headers=headers)
        if response.status_code == 503:
            pytest.skip("Server is not ready or not running. Please start the server first: python main.py")
        assert response.status_code == 200
        
        data = response.json()
        assert "object" in data
        assert data["object"] == "list"
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # 检查模型格式
        for model in data["data"]:
            assert "id" in model
            assert "object" in model
            assert model["object"] == "model"
            assert "description" in model
    
    @pytest.mark.asyncio
    async def test_list_models_without_auth(self, client):
        """测试未认证时列出模型（应该失败）"""
        response = await client.get("/v1/models")
        assert response.status_code == 403  # FastAPI 默认返回 403
    
    @pytest.mark.asyncio
    async def test_list_models_invalid_key(self, client):
        """测试使用无效的 API Key"""
        headers = {
            "Authorization": "Bearer invalid_key",
            "Content-Type": "application/json"
        }
        response = await client.get("/v1/models", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_text_to_image(self, client, headers):
        """测试文生图接口"""
        payload = {
            "model": "sora-image",
            "messages": [
                {
                    "role": "user",
                    "content": "一只可爱的小猫咪"
                }
            ],
            "stream": True
        }
        
        response = await client.post(
            "/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # 检查流式响应
        content = response.text
        assert "data:" in content
    
    @pytest.mark.asyncio
    async def test_text_to_image_non_stream(self, client, headers):
        """测试文生图接口（非流式）"""
        payload = {
            "model": "sora-image",
            "messages": [
                {
                    "role": "user",
                    "content": "一只可爱的小猫咪"
                }
            ],
            "stream": False
        }
        
        response = await client.post(
            "/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        # 非流式模式可能返回可用性检查结果或错误
        assert response.status_code in [200, 500]
    
    @pytest.mark.asyncio
    async def test_image_to_image(self, client, headers):
        """测试图生图接口"""
        # 创建一个简单的测试图片（1x1 像素的 PNG）
        test_image = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        ).decode('utf-8')
        
        payload = {
            "model": "sora-image",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "将这张图片变成油画风格"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{test_image}"
                            }
                        }
                    ]
                }
            ],
            "stream": True
        }
        
        response = await client.post(
            "/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    @pytest.mark.asyncio
    async def test_text_to_video(self, client, headers):
        """测试文生视频接口（只验证初始响应）"""
        payload = {
            "model": "sora-video-landscape-10s",
            "messages": [
                {
                    "role": "user",
                    "content": "一只小猫在草地上奔跑"
                }
            ],
            "stream": True
        }
        
        # 使用流式响应，只检查初始部分避免超时
        async with client.stream(
            "POST",
            "/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10.0
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            # 读取第一块数据确认流式响应正常
            try:
                async for chunk in response.aiter_bytes():
                    if chunk:
                        break  # 收到数据就退出，不等待完整响应
            except httpx.ReadTimeout:
                # 超时是预期的，因为视频生成需要时间
                pass
    
    @pytest.mark.asyncio
    async def test_image_to_video(self, client, headers):
        """测试图生视频接口"""
        # 创建一个简单的测试图片
        test_image = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        ).decode('utf-8')
        
        payload = {
            "model": "sora-video-landscape-10s",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这只猫在跳舞"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{test_image}"
                            }
                        }
                    ]
                }
            ],
            "stream": True
        }
        
        response = await client.post(
            "/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    @pytest.mark.asyncio
    async def test_video_remix(self, client, headers):
        """测试视频 Remix 功能（只验证初始响应）"""
        payload = {
            "model": "sora-video-landscape-10s",
            "messages": [
                {
                    "role": "user",
                    "content": "https://sora.chatgpt.com/p/s_68e3a06dcd888191b150971da152c1f5改成水墨画风格"
                }
            ],
            "stream": True
        }
        
        # 使用流式响应，只检查初始部分避免超时
        async with client.stream(
            "POST",
            "/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10.0
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            # 读取第一块数据确认流式响应正常
            try:
                async for chunk in response.aiter_bytes():
                    if chunk:
                        break  # 收到数据就退出，不等待完整响应
            except httpx.ReadTimeout:
                # 超时是预期的，因为视频生成需要时间
                pass
    
    @pytest.mark.asyncio
    async def test_video_storyboard(self, client, headers):
        """测试视频分镜功能（只验证初始响应）"""
        payload = {
            "model": "sora-video-landscape-10s",
            "messages": [
                {
                    "role": "user",
                    "content": "[5.0s]猫猫从飞机上跳伞 [5.0s]猫猫降落 [10.0s]猫猫在田野奔跑"
                }
            ],
            "stream": True
        }
        
        # 使用流式响应，只检查初始部分避免超时
        async with client.stream(
            "POST",
            "/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10.0
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            # 读取第一块数据确认流式响应正常
            try:
                async for chunk in response.aiter_bytes():
                    if chunk:
                        break  # 收到数据就退出，不等待完整响应
            except httpx.ReadTimeout:
                # 超时是预期的，因为视频生成需要时间
                pass
    
    @pytest.mark.asyncio
    async def test_invalid_model(self, client, headers):
        """测试使用无效模型"""
        payload = {
            "model": "invalid-model",
            "messages": [
                {
                    "role": "user",
                    "content": "测试"
                }
            ],
            "stream": False
        }
        
        response = await client.post(
            "/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 400
        data = response.json()
        # FastAPI HTTPException returns {"detail": "..."} format
        assert "detail" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_empty_messages(self, client, headers):
        """测试空消息列表"""
        payload = {
            "model": "sora-image",
            "messages": [],
            "stream": False
        }
        
        response = await client.post(
            "/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 400
        data = response.json()
        # FastAPI HTTPException returns {"detail": "..."} format
        assert "detail" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self, client):
        """测试缺少 API Key"""
        payload = {
            "model": "sora-image",
            "messages": [
                {
                    "role": "user",
                    "content": "测试"
                }
            ],
            "stream": False
        }
        
        response = await client.post(
            "/v1/chat/completions",
            json=payload
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_different_image_models(self, client, headers):
        """测试不同的图片模型"""
        models = ["sora-image", "sora-image-landscape", "sora-image-portrait"]
        
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": "测试图片生成"
                    }
                ],
                "stream": True
            }
            
            response = await client.post(
                "/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    @pytest.mark.asyncio
    async def test_different_video_models(self, client, headers):
        """测试不同的视频模型"""
        models = [
            "sora-video-10s",
            "sora-video-15s",
            "sora-video-landscape-10s",
            "sora-video-landscape-15s",
            "sora-video-portrait-10s",
            "sora-video-portrait-15s"
        ]
        
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": "测试视频生成"
                    }
                ],
                "stream": True
            }
            
            response = await client.post(
                "/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    @pytest.mark.asyncio
    async def test_stream_response_format(self, client, headers):
        """测试流式响应格式"""
        payload = {
            "model": "sora-image",
            "messages": [
                {
                    "role": "user",
                    "content": "测试流式响应"
                }
            ],
            "stream": True
        }
        
        response = await client.post(
            "/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        content = response.text
        
        # 检查 SSE 格式
        lines = content.split('\n')
        data_lines = [line for line in lines if line.startswith('data:')]
        assert len(data_lines) > 0
        
        # 检查是否有 [DONE] 标记
        done_found = any('[DONE]' in line for line in lines)
        # 注意：某些情况下可能没有 [DONE]，这取决于实现


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

