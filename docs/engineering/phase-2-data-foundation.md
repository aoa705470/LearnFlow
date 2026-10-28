# 阶段 2 数据基础与验证记录

日期：2026-10-28

范围：阶段 2 按依赖逐项推进。本记录当前只覆盖已完成的 T014，不代表 T015～T022 的业务模型、迁移、事务规则或备份恢复已经完成。

## 1. T014 实现

- `app.db.engine` 按统一 `Settings` 创建同步 SQLAlchemy Engine，落实连接池大小、溢出、等待、回收和连接/读/写超时，并启用 `pool_pre_ping`。
- 每个新数据库连接显式设置 UTC 会话时区和 5 秒 InnoDB 锁等待，避免依赖数据库实例的隐式默认值。
- `app.db.session` 提供请求依赖。每次解析依赖都会创建新的 Session，请求结束时关闭；Session 禁止自动开启事务，后续 Service 必须显式拥有事务边界，依赖和 Repository 不提交。
- `UUIDChar` 将 Python `UUID` 映射为 `CHAR(36) CHARACTER SET ascii COLLATE ascii_bin`，使用规范小写文本和逐字节比较。
- `UTCDateTime` 只接受带时区的 Python 时间，写入前转换为 UTC naive 值并存入 `DATETIME(6)`；读取时恢复为 UTC-aware 时间，保留微秒。
- 公共列类型固定版本号为 `BIGINT UNSIGNED`、本地日历日期为 `DATE`、标准文本为 `TEXT`、长正文为 `MEDIUMTEXT`。业务字段长度校验仍由后续模型和 API 任务实现。
- Alembic 已接入公共 `Base.metadata`；本任务没有提前创建十张业务表，也没有使用 `create_all` 代替迁移。

## 2. 2026-10-28 实际验证

| 验证                  | 结果                                                                                                                                                                                    |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pnpm check:api`      | 通过；Ruff lint/format、mypy strict 均成功；无 MySQL 模式 18 passed、2 skipped                                                                                                          |
| 请求 Session 单元测试 | 通过；两个并发 FastAPI 请求在同步点相遇并取得两个不同 Session；同时确认 `autobegin=False`                                                                                               |
| 类型适配单元测试      | 通过；UUID DDL、规范文本、UTC 正反转换、微秒保留和 naive 时间拒绝均符合预期                                                                                                             |
| 隔离 MySQL pytest     | 通过；MySQL 8.4.13 上 20 passed，无跳过                                                                                                                                                 |
| MySQL 会话参数        | 通过；连接事件实际得到 `@@session.time_zone = '+00:00'` 和 5 秒锁等待                                                                                                                   |
| MySQL 类型往返        | 通过；UUID、带 `+08:00` 的微秒时间、`BIGINT UNSIGNED` 最大值、`1000-01-01`、10,000 字符 `TEXT` 和 200,000 字符 `MEDIUMTEXT` 精确往返，无截断                                            |
| `pnpm db:migrate`     | 通过；补齐必填测试配置后连接隔离 MySQL 并升级至当前 head；当前尚无业务迁移                                                                                                              |
| GitHub Actions        | 通过；实现提交 `abca68c` 对应的 [CI 运行 40668638618](https://github.com/aoa705470/LearnFlow/actions/runs/40668638618) 成功，Web checks 59 秒、API and MySQL checks 53 秒，全部步骤通过 |
| `git diff --check`    | 通过                                                                                                                                                                                    |

迁移入口第一次只设置 `DATABASE_URL` 时，按设计被其余必填配置校验拒绝；补齐与工程基线一致的测试环境变量后通过。验证结束后已停止 `mysql-test` 容器，保留命名卷，未删除或覆盖开发数据。

## 3. 当前边界

- T015 才会建立 `settings`、`topics` 模型和第一份业务迁移。
- T016～T018 才会补齐其余业务表、外键和约束；本任务的公共类型不能替代字段级业务约束。
- T019～T021 才会验证迁移链路、种子数据和真实并发事务；T014 的请求级 Session 测试不冒充业务并发验收。
- 实现提交 `abca68c` 已由 GitHub Actions 托管 Runner 验证；后续模型和迁移变更仍必须取得各自的新运行证据，不能沿用本次结果。
