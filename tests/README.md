# API 接口测试

本目录包含 Sora2API 项目的接口测试文件。

## 安装测试依赖

```bash
pip install -r requirements-test.txt
```

或者直接安装：

```bash
pip install pytest pytest-asyncio httpx
```

## 运行测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定测试文件

```bash
pytest tests/test_api.py -v
```

### 运行特定测试用例

```bash
pytest tests/test_api.py::TestAPI::test_list_models -v
```

### 显示详细输出

```bash
pytest tests/ -v -s
```

## 测试前准备

1. **确保服务已启动**：测试需要服务运行在 `http://localhost:8000`

```bash
python main.py
```

2. **检查 API Key**：默认使用 `han1234`，如需修改请编辑 `tests/test_api.py` 中的 `API_KEY` 变量

## 测试覆盖

### 已测试的接口

- ✅ `/v1/models` - 列出所有模型
- ✅ `/v1/chat/completions` - 聊天完成接口
  - ✅ 文生图
  - ✅ 图生图
  - ✅ 文生视频
  - ✅ 图生视频
  - ✅ 视频 Remix
  - ✅ 视频分镜
  - ✅ 不同模型测试
  - ✅ 流式和非流式响应

### 认证测试

- ✅ 有效 API Key
- ✅ 无效 API Key
- ✅ 缺少 API Key

### 错误处理测试

- ✅ 无效模型
- ✅ 空消息列表
- ✅ 格式验证

## 注意事项

1. **流式响应测试**：某些测试会检查流式响应的格式，但不会等待完整响应（因为生成可能需要较长时间）

2. **实际生成测试**：由于实际生成图片/视频需要真实的 Token 和较长时间，测试主要验证：
   - 接口可访问性
   - 请求格式正确性
   - 响应格式正确性
   - 错误处理

3. **集成测试**：如需测试完整的生成流程，需要：
   - 配置有效的 Token
   - 增加超时时间
   - 可能需要 Mock 外部服务

## 持续集成

可以在 CI/CD 流程中运行测试：

```yaml
# 示例 GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    python main.py &
    sleep 5
    pytest tests/ -v
```

