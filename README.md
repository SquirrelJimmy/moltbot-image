# Moltbot 镜像使用指南

本仓库用于自动构建并发布上游 `moltbot/moltbot` 的 Docker 镜像到 GHCR。  
`latest` 标签始终对应上游最新 release tag（定时刷新）。

## 镜像与标签

镜像仓库：`ghcr.io/squirreljimmy/`

默认构建的镜像（对应上游 Dockerfile）：

- `ghcr.io/squirreljimmy/moltbot:<tag>`
- `ghcr.io/squirreljimmy/moltbot-sandbox:<tag>`
- `ghcr.io/squirreljimmy/moltbot-sandbox-browser:<tag>`

标签规则：

- `:<tag>` = 上游 release tag
- `:latest` = 上游最新 release tag（滚动更新）

支持架构：`linux/amd64`

## 快速开始（推荐：Docker Compose）

在任意目录创建 `docker-compose.yml`：

```yaml
services:
  moltbot-gateway:
    image: ghcr.io/squirreljimmy/moltbot:latest
    environment:
      HOME: /home/node
      TERM: xterm-256color
      CLAWDBOT_GATEWAY_TOKEN: ${CLAWDBOT_GATEWAY_TOKEN}
      CLAUDE_AI_SESSION_KEY: ${CLAUDE_AI_SESSION_KEY}
      CLAUDE_WEB_SESSION_KEY: ${CLAUDE_WEB_SESSION_KEY}
      CLAUDE_WEB_COOKIE: ${CLAUDE_WEB_COOKIE}
    volumes:
      - ${CLAWDBOT_CONFIG_DIR}:/home/node/.clawdbot
      - ${CLAWDBOT_WORKSPACE_DIR}:/home/node/clawd
    ports:
      - "${CLAWDBOT_GATEWAY_PORT:-18789}:18789"
      - "${CLAWDBOT_BRIDGE_PORT:-18790}:18790"
    init: true
    restart: unless-stopped
    command:
      [
        "node",
        "dist/index.js",
        "gateway",
        "--bind",
        "${CLAWDBOT_GATEWAY_BIND:-lan}",
        "--port",
        "${CLAWDBOT_GATEWAY_PORT:-18789}"
      ]

  moltbot-cli:
    image: ghcr.io/squirreljimmy/moltbot:latest
    environment:
      HOME: /home/node
      TERM: xterm-256color
      BROWSER: echo
      CLAUDE_AI_SESSION_KEY: ${CLAUDE_AI_SESSION_KEY}
      CLAUDE_WEB_SESSION_KEY: ${CLAUDE_WEB_SESSION_KEY}
      CLAUDE_WEB_COOKIE: ${CLAUDE_WEB_COOKIE}
    volumes:
      - ${CLAWDBOT_CONFIG_DIR}:/home/node/.clawdbot
      - ${CLAWDBOT_WORKSPACE_DIR}:/home/node/clawd
    stdin_open: true
    tty: true
    init: true
    entrypoint: ["node", "dist/index.js"]
```

创建 `.env`（建议放在 `docker-compose.yml` 同级目录）：

```bash
# 使用绝对路径（~ 在部分环境不会自动展开）
CLAWDBOT_CONFIG_DIR=/home/youruser/.clawdbot
CLAWDBOT_WORKSPACE_DIR=/home/youruser/clawd

# 必填：Gateway Token（32 字节十六进制）
CLAWDBOT_GATEWAY_TOKEN=请替换为你的随机值

# 端口与绑定
CLAWDBOT_GATEWAY_PORT=18789
CLAWDBOT_BRIDGE_PORT=18790
CLAWDBOT_GATEWAY_BIND=lan

# 可选：Claude 相关（按需填写其一）
CLAUDE_AI_SESSION_KEY=
CLAUDE_WEB_SESSION_KEY=
CLAUDE_WEB_COOKIE=
```

生成 Token 示例（任选其一）：

```bash
openssl rand -hex 32
# 或
python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
```

启动：

```bash
docker compose up -d moltbot-gateway
```

首次初始化（交互式）：

```bash
docker compose run --rm moltbot-cli onboard --no-install-daemon
```

## 环境变量说明（核心）

必填：
- `CLAWDBOT_GATEWAY_TOKEN`：Gateway 认证 Token（建议 32 字节十六进制）

建议配置：
- `CLAWDBOT_CONFIG_DIR`：配置目录（默认：`~/.clawdbot`，映射到容器 `/home/node/.clawdbot`）
- `CLAWDBOT_WORKSPACE_DIR`：工作区目录（默认：`~/clawd`，映射到容器 `/home/node/clawd`）
- `CLAWDBOT_GATEWAY_PORT`：Gateway 端口（默认：`18789`）
- `CLAWDBOT_BRIDGE_PORT`：Bridge 端口（默认：`18790`）
- `CLAWDBOT_GATEWAY_BIND`：绑定模式（默认：`lan`）

可选：
- `CLAUDE_AI_SESSION_KEY` / `CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`：按你的鉴权方式配置

## 端口

- `18789`：Gateway 服务端口
- `18790`：Bridge 端口

## 卷与持久化

至少需要持久化两个目录：

- 配置目录：`${CLAWDBOT_CONFIG_DIR}` → `/home/node/.clawdbot`
- 工作区：`${CLAWDBOT_WORKSPACE_DIR}` → `/home/node/clawd`

这两个目录保存配置和运行数据，升级镜像时也会保留。

## 配置文件

- `.env`：Compose 环境变量文件（与 `docker-compose.yml` 同目录）
- `${CLAWDBOT_CONFIG_DIR}`：运行时配置目录（容器内 `/home/node/.clawdbot`）
- `${CLAWDBOT_WORKSPACE_DIR}`：工作区目录（容器内 `/home/node/clawd`）

## 使用其他构建镜像

如果需要 sandbox 镜像，把 `image:` 替换为：

- `ghcr.io/squirreljimmy/moltbot-sandbox:latest`
- `ghcr.io/squirreljimmy/moltbot-sandbox-browser:latest`

## 可选：复用上游 docker-setup.sh

如果你仍想使用上游脚本的交互流程，可先设置：

```bash
export CLAWDBOT_IMAGE=ghcr.io/squirreljimmy/moltbot:latest
```

然后执行上游的 `docker-setup.sh`（脚本会改用你的 GHCR 镜像）。
