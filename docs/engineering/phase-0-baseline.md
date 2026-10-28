# 阶段 0：开发基线与工程参数

记录日期：2026-10-28。适用任务：T001～T004。本文件记录已经确认并实际探测的工程基线，不表示前后端脚手架、正式锁文件、MySQL Compose 或应用功能已经建立。

## 1. MVP 定义基线（T001）

### 1.1 范围与定义归属

- 产品范围、目标、里程碑与 AC-01～AC-15：`docs/product/learnflow-v1-prd.md`。
- 功能行为、资格、输入边界与今日计算：`FEATURES.md`。
- HTTP 字段、错误、版本、分页、幂等与导出：`API.md`。
- 物理存储、约束、事务、迁移与恢复：`DATABASE.md`。
- 分层、Session、锁、草稿与部署边界：`ARCHITECTURE.md`。
- 工具链、编码、测试、CI 与完成标准：`DEVELOPMENT.md`。
- D01～D08、FR-01～FR-04、RD-01～RD-26 与性能门禁：`docs/product/implementation-readiness.md`。
- 视觉目标与当前 Figma 状态：`docs/design/README.md`、`docs/design/component-map.md`、`docs/design/figma-state.json`。

MVP 继续采用本机单用户、单工作空间、模块化单体。阶段 0 不加入账号、公网部署、文件上传、AI 规划、跨设备同步、通知、深色模式、应用内导入或后台备份调度。

### 1.2 FR-01～FR-04 追溯

| 编号 | 当前定义 | 后续实现入口 |
| --- | --- | --- |
| FR-01 | 关联查询显式携带来源 `topic_id`；只传关联 ID 保持全局默认 | T028、T054、T062、T077 |
| FR-02 | 主题状态变化使相关列表、详情、今日与复习缓存失效，并阻止旧响应回写 | T041、T076、T077 |
| FR-03 | development 支持本机直连/Vite；production 业务流量仅经 Nginx | T004、T025、T095、T096 |
| FR-04 | `planned_date` 只接受 `1000-01-01`～`9999-12-31` 的真实日期 | T046、T086、T085 |

### 1.3 已登记但本阶段不修改的旧状态文字

当前 PRD 第 8 节和 `docs/design/figma-state.json` 已记录 Figma 配色同步与代表截图复核完成；实际 Vue、键盘和焦点验收仍未执行。下列文字仍把“画布同步”写成未完成，按 T001 只登记，等待后续获得源文档维护授权时统一修正：

- `FEATURES.md` 第 12 节；
- `ARCHITECTURE.md` 第 13 节；
- `docs/design/ui-architecture.md` 的“实现与验收边界”；
- `docs/product/implementation-readiness.md` 的 D07。

## 2. 工具链与依赖基线（T002）

### 2.1 固定工具链

| 工具 | 固定版本或镜像 | 说明 |
| --- | --- | --- |
| Node.js | 24.16.0 LTS | 使用 Node 24 系列，不跟随 Current 版本 |
| Python | 3.13.14 | 项目环境显式选择 3.13，不使用系统默认 3.14 |
| pnpm | 11.19.0 | 后续通过根 `package.json#packageManager` 固定 |
| uv | 0.11.29 | 后续由 `apps/api/uv.lock` 固定 Python 依赖 |
| MySQL | 8.4.13 LTS | 镜像索引摘要 `sha256:76f0358884cb92d9a086d24e5671c38048d3fef40f2588703d73eb55392d6b69` |

正式 `pnpm-lock.yaml` 和 `apps/api/uv.lock` 分别属于 T006、T007 的脚手架产物。阶段 0 固定精确版本并完成隔离解析、类型、构建和连接探测，不提前创建 `apps/` 目录或用临时锁文件冒充正式项目锁文件。T006、T007 生成锁文件时不得无记录改变本基线。

### 2.2 前端兼容组合

| 类别 | 包 | 固定版本 |
| --- | --- | --- |
| 运行时 | `vue` | 3.5.44 |
| 运行时 | `vue-router` | 5.4.0 |
| 服务端状态 | `@tanstack/vue-query` | 5.105.0 |
| 无头组件 | `reka-ui` | 2.11.0 |
| 图标 | `@lucide/vue` | 1.62.0 |
| Markdown | `markdown-it` | 15.0.3 |
| 内容净化 | `dompurify` | 3.4.17 |
| 构建 | `vite` / `@vitejs/plugin-vue` | 8.3.5 / 6.0.10 |
| 类型 | `typescript` / `vue-tsc` | 6.0.3 / 3.3.13 |
| 样式 | `tailwindcss` / `@tailwindcss/vite` | 4.3.3 / 4.3.3 |
| 组件源码工具 | `shadcn-vue` | 2.8.2 |
| 代码质量 | `eslint` / `eslint-plugin-vue` / `typescript-eslint` / `prettier` | 10.13.0 / 10.12.0 / 8.72.1 / 3.9.10 |

未采用 TypeScript 7.0.2：实际查询到的 `typescript-eslint@8.72.1` 对 TypeScript 的支持上限为 `<6.1.0`，因此选择已通过探测的 6.0.3。严格类型检查还需要显式固定 `@types/node@24.19.2`、`@types/markdown-it@14.2.0`、`@types/web-bluetooth@0.0.22` 与 `vue-component-type-helpers@3.3.13`。

`@tanstack/vue-query` 的 `vue-demi` 生命周期脚本必须在 `pnpm-workspace.yaml` 中按包名显式允许；不全局放开依赖脚本。

### 2.3 后端兼容组合

| 类别 | 包 | 固定版本 |
| --- | --- | --- |
| Web/API | `fastapi` | 0.162.0 |
| Schema/配置 | `pydantic` / `pydantic-settings` | 2.14.1 / 2.16.1 |
| ORM | `sqlalchemy` | 2.1.6 |
| MySQL 驱动 | `pymysql[rsa]` | 1.2.3；解析得到 `cryptography` 50.0.2 |
| 迁移 | `alembic` | 1.20.1 |
| ASGI 服务 | `uvicorn` | 0.54.0 |
| 测试客户端 | `httpx2` | 2.16.0 |
| 测试与检查 | `pytest` / `ruff` / `mypy` | 9.2.0 / 0.17.3 / 2.4.0 |

FastAPI、Pydantic、SQLAlchemy、PyMySQL、Alembic、pytest、Ruff 和 mypy 的已选版本为 MIT；Uvicorn 与 httpx2 为 BSD-3-Clause。依赖解析和许可记录不代替后续安全审计与升级测试。

## 3. 未锁定库与生成器（T003）

### 3.1 Markdown

- `markdown-it@15.0.3`，初始化时固定 `html: false`，不执行原始 HTML。
- `dompurify@3.4.17` 作为纵深净化，协议和标签允许列表在 T036 按 API/安全要求实现并测试。
- `markdown-it` 为 MIT；DOMPurify 为 MPL-2.0 或 Apache-2.0 双许可，均可用于本项目。

### 3.2 OpenAPI 到 TypeScript

- 使用 `@hey-api/openapi-ts@0.99.0`，输出 Fetch 客户端、SDK 与类型到 `packages/api-client` 的生成目录。
- 生成目录不得手改；T029 建立固定配置、统一命令及干净重生成漂移检查。
- 隔离探测已从最小 OpenAPI 3.1 文档生成 Fetch 客户端、SDK 和类型文件。

### 3.3 UI 包边界

- 使用 `shadcn-vue@2.8.2`、`reka-ui@2.11.0`、Tailwind CSS 4.3.3 与 `@lucide/vue@1.62.0`。
- 不安装 Pinia；出现真实跨页本地状态需求时另行评估。
- 不引入第二套 UI 或服务端状态架构。

经探测，原确认候选 `lucide-vue-next@1.0.0` 已被注册表标记弃用并要求迁移到 `@lucide/vue`。`@lucide/vue@1.62.0` 已通过类型和构建探测，并于 2026-10-28 获用户确认作为正式 Lucide Vue 包；许可为 ISC。

## 4. 环境与运行参数（T004）

### 4.1 入口、来源与数据库隔离

| 环境 | 浏览器/代理入口 | API | MySQL |
| --- | --- | --- | --- |
| development | `http://127.0.0.1:5173` | `127.0.0.1:8000`，可由 Vite 代理或显式直连 | `127.0.0.1:3307`，数据库 `learnflow_dev` |
| test | 不作为人工入口 | 测试进程分配，不复用开发数据 | `127.0.0.1:3308`，数据库 `learnflow_test` |
| production | `http://127.0.0.1:8080` | 仅容器内部，不映射宿主机端口 | 仅容器内部，数据库 `learnflow_prod` |

- development 的 `allowed_hosts`：`127.0.0.1:5173`、`127.0.0.1:8000`。
- development 的 `allowed_origins`：`http://127.0.0.1:5173`、`http://127.0.0.1:8000`。
- production 的 `allowed_hosts`：`127.0.0.1:8080`。
- production 的 `allowed_origins`：`http://127.0.0.1:8080`。
- `localhost` 不作为 `127.0.0.1` 的隐式别名；需要时必须单独配置。
- development 与 production 均不信任客户端的 `Forwarded` / `X-Forwarded-*`。Nginx 保留原始 Host，清除客户端伪造的转发头；当前基线无需依据转发头作安全决策，因此 Uvicorn 的可信代理列表为空。
- 所有数据库使用 InnoDB、`utf8mb4`、`utf8mb4_0900_ai_ci`；幂等键等要求区分大小写的列单独使用二进制排序规则。

真实 `.env` 不入库，根 `.env.example` 只提供无密钥示例。`APP_ENV` 必须显式为 `development` 或 `production`；缺失或未知值启动失败。正式配置文件由 T008 创建。

### 4.2 SQLAlchemy/PyMySQL 参数

| 参数 | 值 |
| --- | --- |
| `pool_size` | 5 |
| `max_overflow` | 5 |
| `pool_timeout` | 10 秒 |
| `pool_recycle` | 1800 秒 |
| `pool_pre_ping` | `true` |
| `connect_timeout` | 5 秒 |
| `read_timeout` / `write_timeout` | 30 秒 / 30 秒 |
| Session 时区 | 每次新连接设为 `+00:00` |
| `innodb_lock_wait_timeout` | 每次新连接设为 5 秒 |

连接时区与锁等待通过 SQLAlchemy 新连接事件统一设置，Repository 不自行变更。安全命令重试次数、游标有效期/完整性、健康端点路径与代理请求超时留在 T027、T061、T093、T095 前确定；阶段 0 不擅自填值。

## 5. 实际验证记录

2026-10-28 在 Windows、Docker Desktop Linux 后端上执行：

1. 前端隔离依赖解析：pnpm 11.19.0 安装 596 个锁文件条目；仅显式允许 `vue-demi` 生命周期脚本。
2. `vue-tsc --noEmit`：通过。首次探测暴露缺少 Web Bluetooth 与 Vue 类型辅助包，补入固定版本后通过。
3. `vite build`：通过，Vite 8.3.5 + Vue 3.5.44 + Tailwind 4.3.3 共转换 2649 个模块。沙箱内原生二进制受限，获准后在相同隔离目录复验通过。
4. `shadcn-vue --help`：CLI 可运行；未初始化正式组件。
5. `openapi-ts --input openapi.json --output generated`：通过，生成 Fetch 客户端、SDK 和类型。
6. Python 3.13.14 隔离环境：39 个后端包解析并安装；FastAPI 最小健康路由经 TestClient 返回预期 JSON。
7. MySQL 8.4.13 临时容器：通过 SQLAlchemy 2.1.6 + PyMySQL 1.2.3 从宿主机真实连接；查询得到 `utf8mb4`、`utf8mb4_0900_ai_ci`，连接后设置并验证 `time_zone='+00:00'`、`innodb_lock_wait_timeout=5`。临时容器未挂数据卷并已删除。

未执行：正式应用启动、正式锁文件生成、业务 API、迁移、浏览器闭环、并发、性能及恢复测试。这些仍由后续任务承担。
