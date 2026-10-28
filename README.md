# LearnFlow

LearnFlow 是一个本机单用户的个人学习工作台。当前工程处于阶段 1：前后端、测试、MySQL 与 CI 脚手架已经建立，但尚未提供业务接口、数据表或示例学习数据。

## 固定工具链

- Node.js 24.16.0、pnpm 11.19.0
- Python 3.13.14、uv 0.11.29
- Docker Desktop 与 Docker Compose
- MySQL 8.4.13（由 Compose 固定镜像与摘要）

## 首次准备

在仓库根目录执行：

```powershell
Copy-Item .env.example .env
pnpm install --frozen-lockfile
uv sync --project apps/api --locked
```

随后修改本机 `.env` 中的占位密码。`.env` 已被 Git 忽略，不要提交真实密码。

三种配置用途相互隔离：

| 配置        | 入口与数据库                                              | 用途                                                                              |
| ----------- | --------------------------------------------------------- | --------------------------------------------------------------------------------- |
| development | `127.0.0.1:5173` / `127.0.0.1:8000`，`learnflow_dev:3307` | 本机开发；使用 `.env`                                                             |
| test        | 独立 `learnflow_test:3308`                                | pytest 与 CI；必须显式设置 `RUN_MYSQL_TESTS=1`                                    |
| production  | `127.0.0.1:8080`，应用与 MySQL 仅在容器网络可达           | 后续本机交付；将 `APP_ENV` 设为 `production`，Host/Origin 只允许 `127.0.0.1:8080` |

`APP_ENV` 只接受 `development` 或 `production`；测试属于隔离的运行配置，不新增宽松的应用环境。缺少环境、数据库 URL、Host/Origin 或连接池参数时 API 会拒绝启动。production 的容器入口将在阶段 17 建立，本阶段不提供未验证的启动命令。

## 本地开发

启动开发数据库并等待健康检查通过：

```powershell
pnpm db:dev:up
pnpm db:migrate
```

当前还没有业务迁移，因此 `upgrade head` 只验证 Alembic 入口。分别在两个终端启动 API 和前端：

```powershell
pnpm dev:api
pnpm dev:web
```

- 前端：<http://127.0.0.1:5173>
- API OpenAPI：<http://127.0.0.1:8000/openapi.json>
- Vite 将 `/api` 转发到 `VITE_API_PROXY_TARGET`，并保留原始 Host。

停止数据库不会删除命名卷：

```powershell
pnpm db:dev:down
```

## 检查与测试

```powershell
pnpm check:web
pnpm check:api
pnpm test:e2e
```

真实 MySQL 集成测试使用独立的 3308 端口和 `learnflow_test` 数据库：

```powershell
pnpm db:test:up
$env:RUN_MYSQL_TESTS = '1'
$env:TEST_DATABASE_URL = 'mysql+pymysql://learnflow_test:<测试密码>@127.0.0.1:3308/learnflow_test?charset=utf8mb4'
pnpm test:api
pnpm db:test:down
```

测试保护会拒绝非 3308 端口或非 `learnflow_test` 库名。Host/Origin 的实际请求拦截、业务读写与健康端点属于后续任务，本阶段不把 OpenAPI 可访问冒充为完整联调。
