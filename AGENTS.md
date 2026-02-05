# Repository Guidelines

## 项目结构与模块组织
- `README.md`：使用与镜像说明。
- `scripts/discover_targets.py`：扫描上游仓库中的 Dockerfile，并输出 GitHub Actions 构建矩阵 JSON。
- `.github/workflows/openclaw-images.yml`：定时/手动触发的构建与发布流水线；CI 会临时克隆上游到 `upstream/`。
- 本仓库不包含 Dockerfile 或应用源码，构建输入来自上游仓库目录 `upstream/`。

## CI 与镜像策略
- 触发方式：定时 `0 2 */3 * *`（UTC；北京时间约 10:00，每 3 天一次）与 `workflow_dispatch` 手动触发。
- 上游来源：`UPSTREAM_REPO=openclaw/openclaw`，优先使用 release tag；回退到最新 git tag。
- 标签策略：发布 `<tag>` 与 `latest` 两个标签到 `ghcr.io/<owner>/`（注意 GHCR 仓库名要求小写）。
- 矩阵字段：`name`、`context`、`dockerfile`、`image` 由脚本生成并传入 Buildx。
- 目标架构：`linux/amd64`（如需多架构，请更新 workflow 与上游 Dockerfile 支持情况）。

## 构建、测试与本地开发命令
- `python3 scripts/discover_targets.py <repo_root>`：生成镜像构建矩阵。
- 示例：
  - `git clone --depth 1 --branch <tag> https://github.com/openclaw/openclaw.git upstream`
  - `python3 scripts/discover_targets.py upstream > matrix.json`
- 构建由 CI 完成；如需本地验证，可使用上游的 Dockerfile 在 `upstream/` 目录手动构建。

## 编码风格与命名规范
- Python 3，4 空格缩进，函数与变量使用 `snake_case`。
- 避免新增第三方依赖，优先使用标准库。
- 文件名使用小写与下划线（如 `discover_targets.py`）。

## 变更影响与兼容性
- 调整镜像名前缀或命名规则时，需同步更新 `IMAGE_PREFIX_DEFAULT` 与 README 示例。
- 修改 workflow 权限或触发条件时，请确认 `packages: write` 与 `contents: write` 仍满足发布需求。
- 新增脚本请保持可在最小环境运行（仅 `python3` 与常见 CLI）。

## 测试指南
- 当前无测试框架与覆盖率要求。
- 修改脚本后建议进行冒烟验证：
  - `python3 -m py_compile scripts/discover_targets.py`
  - 运行脚本并检查 JSON 输出是否包含 `include` 列表。
- 如新增测试，建议放在 `tests/`，并在 PR 中说明如何运行。

## 提交与 PR 指南
- 仓库暂无提交历史，未形成既定约定。
- 建议使用 Conventional Commits：`feat:`, `fix:`, `chore:`，必要时加作用域。
- PR 需包含：变更目的、影响范围、是否触及镜像标签或 CI；如影响使用方式，请更新 `README.md`。
- 若关联 issue 或 release，请在描述中链接相关 URL。
- CI 或脚本逻辑变更建议附上关键输出示例（如 `matrix.json` 片段）。

## 安全与配置
- 不要提交任何密钥；CI 使用 GitHub Actions Secrets（例如 `GITHUB_TOKEN`）。
- `.last_built_tag` 由 CI 自动写入与提交，除非确有需要不要手动修改。
- Workflow 关键环境变量：`IMAGE_REGISTRY`、`IMAGE_NAMESPACE`、`IMAGE_PREFIX_DEFAULT`；调整时请同步更新文档。
