# 后端模块边界

后续业务模块按 `Router → Service → Repository / Model` 依赖：

- Router 使用同步 `def`，只处理 HTTP 请求、响应和基础字段适配。
- Service 承担业务资格判断和事务边界。
- Repository 负责查询、锁和持久化，但不自行 `commit`。
- 纯策略显式接收时钟与输入，不依赖 HTTP、数据库或系统实时时钟。

阶段 1 不创建通用 CRUD 框架，也不使用 `create_all` 代替 Alembic 迁移。
