# 阶段 1 工程脚手架与验证记录

日期：2026-10-28

范围：T005～T013。依赖版本与端口基线见[阶段 0 基线](phase-0-baseline.md)。本记录只描述已执行结果，不代表业务 API、数据模型或发布环境已经完成。

## 1. 已建立的工程入口

- 根 pnpm workspace 管理 `apps/web` 与 `packages/api-client`，唯一正式锁文件为 `pnpm-lock.yaml`。
- `apps/web` 提供 Vue 3、TypeScript strict、Vite、Vue Router、TanStack Vue Query、Tailwind CSS 与 `@lucide/vue@1.62.0` 的最小首页；不包含固定原型数据。
- `apps/api` 使用独立 `pyproject.toml`、`uv.lock` 与 `.venv`，FastAPI 路由保持同步调用链；模块说明固定 `Router → Service → Repository / Model`，未建立通用 CRUD 框架，也未使用 `create_all`。
- `packages/api-client` 只保留 T029 的生成入口位置，不手写 DTO 冒充生成客户端。
- 统一 `Settings` 要求显式 `APP_ENV`、数据库 URL、Host/Origin 与连接参数；数据库 URL 使用 `SecretStr`，repr 不输出凭据。
- `infra/compose.yaml` 提供开发/测试两个 MySQL 8.4.13 实例、独立端口、凭据、数据库与命名卷；普通停止不删除卷。
- 根脚本提供锁定安装、检查、测试、迁移、前后端启动和数据库启停；Vite 代理 `/api` 且 `changeOrigin: false`。

## 2. 测试与保护

- Vitest 只收集 `src/**/*.test.ts`，不会误收集 Playwright 文件。
- Playwright 使用锁定版本 Chromium 执行最小首页冒烟测试。
- pytest 提供固定时钟、配置失败测试和真实 MySQL 集成入口。
- 测试启动以已验证的 `TEST_DATABASE_URL` 强制覆盖应用 `DATABASE_URL`；既有开发/生产 URL 不能绕过隔离。MySQL 集成测试需显式 `RUN_MYSQL_TESTS=1`，并在连接前拒绝非回环主机、非 3308 端口或非 `learnflow_test` 库名。
- development 配置只允许基线确定的 `API_HOST=127.0.0.1`，避免环境覆盖使 Uvicorn 监听局域网或全部接口；production 容器入口仍由后续任务单独实现。
- 集成检查确认 MySQL 8.4、`utf8mb4`、`utf8mb4_0900_ai_ci` 与 UTC 有效偏移。

## 3. CI 决定与边界

Q08 已由用户确认采用 GitHub Actions：

- Runner 固定为 `ubuntu-24.04`。
- Web job 执行冻结安装、ESLint、Prettier、vue-tsc、Vitest、生产构建与 Chromium E2E。
- API job 使用独立 MySQL service（宿主端口 3308、数据库 `learnflow_test`），执行 uv 冻结安装、Ruff、mypy、Alembic 入口和 pytest/MySQL 集成测试。
- workflow 使用最小 `contents: read` 权限；uv setup action 固定到提交 SHA。
- T029 的 OpenAPI 客户端生成/漂移检查、后续业务契约和完整学习旅程 E2E 尚未具备，workflow 明确记录而不放空脚本。

GitHub 托管验证记录：首次运行 [40630150592](https://github.com/aoa705470/LearnFlow/actions/runs/40630150592) 暴露了 Pydantic mypy 插件在 Windows 与 Ubuntu 对 `BaseSettings()` 构造签名判断不同的问题；Web job 通过，API job 在 mypy 停止。修正为精确兼容两个平台的诊断后，第二次运行 [40630376539](https://github.com/aoa705470/LearnFlow/actions/runs/40630376539) 的 Web 与 API/MySQL 两个 job 全部通过。

## 4. 2026-10-28 实际验证

| 验证 | 结果 |
| --- | --- |
| `pnpm install --frozen-lockfile` | 通过；631 个锁文件条目通过供应链策略检查 |
| `uv sync --project apps/api --locked` | 通过；Python 3.13.14 独立环境按 `uv.lock` 同步 |
| `pnpm check:web` | 通过；ESLint、Prettier、vue-tsc、Vitest 1 项、Vite production build 均成功 |
| `pnpm check:api` | 通过；Ruff format/lint、mypy strict 成功；无 MySQL 模式 13 passed、1 skipped |
| 隔离 MySQL pytest | 通过；真实测试实例 14 passed，测试应用 URL 强制指向验证后的测试库 |
| 危险配置回归 | 通过；既有生产/开发 `DATABASE_URL` 被隔离测试 URL 覆盖，development 的非 `127.0.0.1` 监听地址被拒绝 |
| `pnpm test:e2e` | 通过；Chromium 1 passed |
| Compose 配置与健康检查 | 通过；开发 3307、测试 3308 均仅绑定 `127.0.0.1`，两个实例进入 healthy |
| `pnpm db:migrate` | 通过；连接真实开发 MySQL，当前无业务迁移，Alembic 报告 MySQL 非事务 DDL 语义 |
| `pnpm dev:api` | 通过；配置驱动监听 `127.0.0.1:8000`，`GET /openapi.json` 返回 200 |
| `pnpm dev:web` 与代理 | 通过；`127.0.0.1:5173` 返回首页；`/api/not-found` 由 Uvicorn 返回 JSON 404，证明代理链路可达 |
| GitHub Actions 托管 Runner | 通过；run 40630376539，Web 50 秒、API/MySQL 57 秒，全部步骤成功 |

验证结束后 Uvicorn、Vite 与两个 MySQL 容器均已停止；MySQL 命名卷按要求保留，未写入示例学习数据。

## 5. 尚未冒充完成的能力

- Host/Origin/CORS 的实际请求拦截属于 T025；本阶段只校验配置并保持 Vite 原始 Host。
- SQLAlchemy Engine/Session、模型和首个迁移属于 T014 以后；当前 Alembic 只有可运行入口。
- 健康端点、初始化设置、真实业务读写和生产容器入口属于后续任务。
- 后续业务任务新增的契约、迁移或 E2E 检查仍需通过新的托管 CI 运行验证，不能沿用本次绿色结果代替。
