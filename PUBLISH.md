# 发布到 PyPI 指南

## 一、前置准备

### 1. 注册 PyPI 账号

- **PyPI 正式环境**：https://pypi.org/account/register/
- **TestPyPI 测试环境**：https://test.pypi.org/account/register/

建议先在 TestPyPI 测试发布流程。

### 2. 安装构建工具

```bash
pip install build twine
```

或使用项目 dev 依赖：

```bash
pip install -e ".[dev]"
```

### 3. 配置 API Token（推荐）

1. 登录 PyPI → Account settings → API tokens
2. 创建 Token，勾选 scope（如整个项目或单个项目）
3. 本地配置 `~/.pypirc`：

```ini
[pypi]
username = __token__
password = pypi-你的PyPI-token

[testpypi]
username = __token__
password = pypi-你的TestPyPI-token
```

> 或使用环境变量：`TWINE_USERNAME=__token__`、`TWINE_PASSWORD=pypi-xxx`

## 二、发布流程

### 1. 构建包

```bash
cd /Users/beisen/PycharmProjects/apollo-mcp
python -m build
```

生成 `dist/apollo_mcp_server-1.0.0-py3-none-any.whl` 和 `dist/apollo-mcp-server-1.0.0.tar.gz`。

### 2. 检查包（可选）

```bash
twine check dist/*
```

### 3. 上传到 TestPyPI（测试）

```bash
twine upload --repository testpypi dist/*
```

测试安装：

```bash
pip install -i https://test.pypi.org/simple/ apollo-mcp-server
```

### 4. 上传到 PyPI（正式）

```bash
twine upload dist/*
```

### 5. 验证安装

```bash
pip install apollo-mcp-server
apollo-mcp-server --url http://your-apollo:8070 --token your_token
```

## 三、版本更新

1. 修改 `pyproject.toml` 中的 `version`
2. 重新执行 `python -m build` 和 `twine upload`

## 四、常见问题

| 问题 | 处理 |
|------|------|
| 包名冲突 | 包名 `apollo-mcp-server` 需在 PyPI 唯一，若已存在需改名为 `apollo-mcp-server-iceycn` 等 |
| 403 | 检查 Token 权限和 scope |
| 409 | 该版本已存在，需升级版本号 |
