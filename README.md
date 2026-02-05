# Openclaw 镜像使用指南

本仓库用于自动构建并发布上游 `openclaw/openclaw` 的 Docker 镜像到 GHCR。  
`latest` 标签始终对应上游最新 release tag（定时刷新）。

## 镜像与标签

镜像仓库：`ghcr.io/squirreljimmy/`

默认构建的镜像（对应上游 Dockerfile）：

- `ghcr.io/squirreljimmy/openclaw:<tag>`
- `ghcr.io/squirreljimmy/openclaw-sandbox:<tag>`
- `ghcr.io/squirreljimmy/openclaw-sandbox-browser:<tag>`

标签规则：

- `:<tag>` = 上游 release tag
- `:latest` = 上游最新 release tag（滚动更新）

支持架构：`linux/amd64`

---

# Docker（可选）

如果你想用 Docker 来运行 Openclaw，请先了解 Openclaw 仍然**非常有状态**，并且对本机文件系统与运行时环境有强依赖：

- 需要访问你的 `~/.openclaw` 配置目录与 workspace。
- Sandbox 模式下需要访问 Docker。
- 需要使用外部频道（如 WhatsApp、Telegram）时，对持久化与网络环境要求更高。

如果 Docker 带来额外复杂度，建议优先使用上游文档中推荐的原生部署方式。

## Docker 是否适合你？

适合：
- 想把 Openclaw 跑在 VPS 或远程 Linux 机器上。
- 想把 Gateway 服务单独部署。

不太适合：
- 需要大量访问本机文件系统或本地 GUI 的场景（工具依赖可能受限）。
- 不熟悉 Docker 的环境。

## 要求

- Docker 已安装
- Docker Compose 已安装（`docker compose` 可用）

---

# 容器化 Gateway（Docker Compose）

## 快速开始（推荐）

上游脚本会自动完成：构建镜像、生成 `.env`、运行 onboarding 向导，并启动 Gateway。  
本仓库使用 GHCR 镜像时，只需在运行脚本前设置镜像：

```bash
export OPENCLAW_IMAGE=ghcr.io/squirreljimmy/openclaw:latest
```

然后在**上游仓库**根目录运行：

```bash
./docker-setup.sh
```

> 如果你没有上游仓库，请先克隆：  
> `git clone https://github.com/openclaw/openclaw.git`

## 手动流程（docker compose）

你也可以按以下流程手动启动：

### docker-compose.yml 示例（固定版本）

> 建议使用**固定版本**（上游 release tag），避免 `latest` 引入不确定变更。

```yaml
services:
  openclaw-gateway:
    image: ghcr.io/squirreljimmy/openclaw:<tag> # <tag> 替换为上游 release tag
    environment:
      HOME: /home/node
      TERM: xterm-256color
      OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN}
      CLAUDE_AI_SESSION_KEY: ${CLAUDE_AI_SESSION_KEY}
      CLAUDE_WEB_SESSION_KEY: ${CLAUDE_WEB_SESSION_KEY}
      CLAUDE_WEB_COOKIE: ${CLAUDE_WEB_COOKIE}
    volumes:
      - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
      - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
    ports:
      - "${OPENCLAW_GATEWAY_PORT:-18789}:18789"
      - "${OPENCLAW_BRIDGE_PORT:-18790}:18790"
    init: true
    restart: unless-stopped
    command:
      [
        "node",
        "dist/index.js",
        "gateway",
        "--bind",
        "${OPENCLAW_GATEWAY_BIND:-lan}",
        "--port",
        "18789",
      ]

  openclaw-cli:
    image: ghcr.io/squirreljimmy/openclaw:<tag> # 同上
    environment:
      HOME: /home/node
      TERM: xterm-256color
      OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN}
      BROWSER: echo
      CLAUDE_AI_SESSION_KEY: ${CLAUDE_AI_SESSION_KEY}
      CLAUDE_WEB_SESSION_KEY: ${CLAUDE_WEB_SESSION_KEY}
      CLAUDE_WEB_COOKIE: ${CLAUDE_WEB_COOKIE}
    volumes:
      - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
      - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
    stdin_open: true
    tty: true
    init: true
    entrypoint: ["node", "dist/index.js"]
```

> 版本选择：可用 `latest`，但生产环境建议固定到具体 `<tag>`。

```bash
# 1) 构建或拉取镜像
docker pull ghcr.io/squirreljimmy/openclaw:latest

# 2) 运行 onboarding
docker compose run --rm openclaw-cli onboard

# 3) 启动 gateway
docker compose up -d openclaw-gateway
```

> 上述命令默认依赖上游仓库中的 `docker-compose.yml`。

如果你设置了 `OPENCLAW_EXTRA_MOUNTS` 或 `OPENCLAW_HOME_VOLUME`，`docker-setup.sh` 会生成 `docker-compose.extra.yml`。
此时请在运行 Compose 时把它也包含进去：

```bash
docker compose -f docker-compose.yml -f docker-compose.extra.yml up -d openclaw-gateway
```

## Docker 环境变量（compose）

建议在 `docker-compose.yml` 同级目录创建 `.env`，至少包含以下变量：

必填：
- `OPENCLAW_GATEWAY_TOKEN`：Gateway 认证 Token（建议 32 字节十六进制）

建议配置：
- `OPENCLAW_CONFIG_DIR`：配置目录（默认：`~/.openclaw`，映射到容器 `/home/node/.openclaw`）
- `OPENCLAW_WORKSPACE_DIR`：工作区目录（默认：`~/.openclaw/workspace`，映射到容器 `/home/node/.openclaw/workspace`）
- `OPENCLAW_GATEWAY_PORT`：Gateway 端口（默认：`18789`）
- `OPENCLAW_BRIDGE_PORT`：Bridge 端口（默认：`18790`）
- `OPENCLAW_GATEWAY_BIND`：绑定模式（默认：`lan`）

可选：
- `OPENCLAW_IMAGE`：镜像名（默认：`openclaw:local`，建议设为你的 GHCR 镜像）
- `OPENCLAW_EXTRA_MOUNTS`：额外挂载（逗号分隔）
- `OPENCLAW_HOME_VOLUME`：持久化 `/home/node` 的命名卷或路径
- `OPENCLAW_DOCKER_APT_PACKAGES`：构建时安装的 apt 包（逗号分隔）
- `CLAUDE_AI_SESSION_KEY` / `CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`：按你的鉴权方式配置

示例 `.env`：

```bash
OPENCLAW_CONFIG_DIR=/home/youruser/.openclaw
OPENCLAW_WORKSPACE_DIR=/home/youruser/.openclaw/workspace
OPENCLAW_GATEWAY_TOKEN=请替换为你的随机值
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_BRIDGE_PORT=18790
OPENCLAW_GATEWAY_BIND=lan
OPENCLAW_IMAGE=ghcr.io/squirreljimmy/openclaw:latest
```

---

# 额外挂载

通过 `OPENCLAW_EXTRA_MOUNTS` 添加额外挂载（逗号分隔）：

```bash
export OPENCLAW_EXTRA_MOUNTS=/home/me/code:/home/node/code,/home/me/zips:/home/node/zips
./docker-setup.sh
```

---

# 持久化 `/home/node`

将容器内 `/home/node` 映射到一个命名卷或宿主目录：

```bash
export OPENCLAW_HOME_VOLUME=openclaw-home
./docker-setup.sh
```

---

# 安装额外 apt 包

通过 `OPENCLAW_DOCKER_APT_PACKAGES` 添加构建时依赖（逗号分隔）：

```bash
export OPENCLAW_DOCKER_APT_PACKAGES=ffmpeg,libzbar0
./docker-setup.sh
```

---

# 更快的重建（建议）

上游 Dockerfile 已按“先复制 lockfile/metadata 再安装依赖”的方式分层；一般只要 `pnpm-lock.yaml` 不变，重建就能复用缓存，避免重复跑 `pnpm install`。

另外：当前镜像默认以非 root 用户 `node`（uid 1000）运行；如果你把宿主目录挂载到 `/home/node/.openclaw` 或 workspace，遇到 `EACCES` 权限错误，通常需要把宿主目录属主改成 uid 1000（Linux 示例）：

```bash
sudo chown -R 1000:1000 /path/to/openclaw-config /path/to/openclaw-workspace
```

---

# 渠道配置

进入容器执行渠道配置：

```bash
# WhatsApp（扫码登录）
docker compose run --rm openclaw-cli channels login

# Telegram（bot token）
docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"

# Discord（bot token）
docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
```

更多渠道说明见：`https://docs.openclaw.ai/channels`

---

# 健康检查

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

如果你需要重新获取 Dashboard 链接与配对信息：

```bash
docker compose run --rm openclaw-cli dashboard --no-open
```

---

# E2E Smoke 测试（Docker）

```bash
scripts/e2e/onboard-docker.sh
```

---

# QR import Smoke 测试（Docker）

```bash
pnpm test:docker:qr
```

---

# 备注

数据默认保存在：
- `OPENCLAW_CONFIG_DIR`（默认：`~/.openclaw`）
- `OPENCLAW_WORKSPACE_DIR`（默认：`~/.openclaw/workspace`）

---

# Agent Sandbox（主机网关 + Docker 工具）

Openclaw 默认在主机运行 Gateway，你可以让**非 main 会话**在 Docker sandbox 里执行工具。

## 启用 sandbox（建议）

在配置里添加：

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main"
      }
    }
  }
}
```

## 使用本仓库预构建的 sandbox 镜像（推荐）

本仓库会同步构建并发布以下镜像（同样遵循 `<tag>` + `latest`）：

- `ghcr.io/squirreljimmy/openclaw-sandbox:latest`
- `ghcr.io/squirreljimmy/openclaw-sandbox-browser:latest`

在 `~/.openclaw/openclaw.json` 中覆盖默认 sandbox 镜像（上游默认一般是 `openclaw-sandbox:bookworm-slim`）：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        docker: { image: "ghcr.io/squirreljimmy/openclaw-sandbox:latest" },
      },
    },
  },
}
```

如果要把 `browser` 工具也放进 sandbox（需要浏览器镜像）：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        docker: { image: "ghcr.io/squirreljimmy/openclaw-sandbox:latest" },
        browser: {
          enabled: true,
          image: "ghcr.io/squirreljimmy/openclaw-sandbox-browser:latest",
        },
      },
    },
  },
}
```

## 自行构建 sandbox 镜像（上游仓库）

在上游 `openclaw/openclaw` 仓库根目录执行：

```bash
scripts/sandbox-setup.sh
scripts/sandbox-browser-setup.sh
```

它们会分别构建：

- `openclaw-sandbox:bookworm-slim`
- `openclaw-sandbox-browser:bookworm-slim`

## 网络（可选）

默认情况下 sandbox 容器网络是 `none`（无外网）。如需访问外网，显式设置网络（示例：`bridge`）：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        docker: {
          image: "ghcr.io/squirreljimmy/openclaw-sandbox:latest",
          network: "bridge",
        },
      },
    },
  },
}
```

## 安全提示

即便在 Docker sandbox 中执行，`shell`/`bash` 仍然可能产生副作用。建议只挂载必要目录，并避免在容器内保存敏感信息。

## 排错提示

确保你的 user 有权限访问 Docker socket，测试：

```bash
docker ps
```
