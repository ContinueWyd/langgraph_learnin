Docker 部署指南
本文档记录了将 LangGraph Agent 封装为 API 并通过 Docker 容器化部署的完整流程与踩坑记录。

1. 准备工作
1.1 代码封装 (FastAPI)
为了让 Agent 能被外部调用，使用 FastAPI 创建 main.py。核心逻辑如下：

定义 ChatRequest 接收用户输入和 thread_id。

使用 InMemorySaver 初始化图（生产环境建议换成持久化存储）。

暴露 POST /chat 接口，调用 graph_app.invoke()。

注意：接口函数建议用普通的 def，而非 async def，防止同步调用大模型时卡死事件循环。

1.2 环境依赖 (requirements.txt)
在本地虚拟环境生成依赖时，一定要剔除 Windows 专属包。
踩坑：直接在 Windows 下执行 pip freeze 会导出 pywin32，导致 Linux 容器构建失败。必须手动删除该行。

1.3 忽略文件 (.dockerignore)
为了避免把本地巨型文件（如 .venv、本地数据库）打包进镜像，需要在根目录创建 .dockerignore，内容如下：

text
.venv/
__pycache__/
*.pyc
.git/
.idea/
checkpoints.db
store.db
hitl.db
untracked.db
chroma_db*/
2. 编写 Dockerfile
在项目根目录新建 Dockerfile（无后缀），内容如下：

dockerfile
# 使用轻量级 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存层
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制剩下的所有代码文件
COPY . .

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 启动 FastAPI 服务 
# 踩坑注意：uvicorn 的模块名不能带 .py 后缀
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
3. 构建与运行
在终端（宿主机）执行以下命令：

bash
# 1. 构建镜像
docker build -t langgraph-agent .

# 2. 运行容器（使用 .env 传入环境变量）
docker run -d --name my-agent -p 8000:8000 --env-file .env langgraph-agent

# 3. 查看容器运行状态
docker ps
4. 接口测试
4.1 宿主机请求（可能遇到的网络问题）
在 Windows PowerShell 中测试：

powershell
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -ContentType "application/json" -Body '{"message": "北京天气怎么样？", "thread_id": "user-123"}'
踩坑记录：

代理软件（如 Clash）可能劫持本地端口，导致连接意外关闭。可通过 -Proxy $null 参数或使用 localhost 替代 127.0.0.1 解决。

PowerShell 显示中文可能乱码，这是控制台编码问题，不影响实际 JSON 返回的 UTF-8 内容。

4.2 容器内部请求（排除网络干扰）
如果宿主机请求失败，可进入容器内部测试以验证服务本身是否正常：

bash
# 进入容器
docker exec -it my-agent /bin/bash

# 在容器内部执行
python -c "import requests; print(requests.post('http://127.0.0.1:8000/chat', json={'message':'北京天气','thread_id':'123'}).text)"
如果内部返回 {"status": "success", ...}，则说明代码完全没问题，故障出在宿主机的网络环境。

5. 常见问题排查
日志闪退：使用 docker logs my-agent 查看报错。

清理旧容器：使用 docker rm -f my-agent 强制删除旧容器，再重新运行。

