# LearnFlow v1 接口规范

| 信息 | 内容 |
| --- | --- |
| 版本 | 1.1 |
| 日期 | 2026-10-27 |
| 状态 | 拟实施契约，尚未实现接口或进行联调 |
| 基础路径 | `/api/v1` |
| 依据 | [功能规格](FEATURES.md)、[系统架构](ARCHITECTURE.md)、[数据库设计](DATABASE.md) |

本文用于前后端分工、OpenAPI 建模及契约测试。下文所有路径省略基础路径。最终机器可读契约由 FastAPI/Pydantic 生成并纳入版本控制。示例是说明性数据，不是生产初始化数据。

## 1. 通用约定

### 1.1 传输、安全与身份

- JSON 使用 UTF-8，写入请求使用 `Content-Type: application/json`，字段采用 snake_case；下载接口除外。
- 本版本机单用户，无登录、Token 和 user_id 参数。仅允许配置中的本地入口与来源；不能直接公开到公网。
- 所有写操作由服务端验证状态与关联，不信任前端隐藏按钮或 actions 提示。
- UUID 使用标准小写字符串。时间戳为 UTC ISO 8601，例如 `2026-10-27T01:00:00.000000Z`；本地日期为 `YYYY-MM-DD`。
- 普通数值为 JSON number；数据库 BIGINT 版本号统一使用十进制字符串，例如 `"3"`，避免 JavaScript 整数精度问题。
- 服务端生成创建时间、更新时间、完成时间和评分时间；客户端不能指定这些字段。
- 未知请求字段、未知枚举、非法排序和缺失必填字段返回 422，防止拼写错误被静默忽略。
- 响应包含 `X-Request-ID`。本机学习数据响应建议 `Cache-Control: no-store`；前端内存查询缓存仍可按应用规则管理。
- 请求体上限 1 MiB（1,048,576 字节，含 JSON 编码开销）；代理和 API 均在完整解析前限制接收量，并将超限统一转换为 413 PAYLOAD_TOO_LARGE。仅接受无压缩请求体，非 identity 的 Content-Encoding 返回 415 UNSUPPORTED_MEDIA_TYPE，避免解压后绕过上限。

下列来源安全规则在开发与生产环境均执行；有反向代理时由代理与API共同执行，开发直连时由API执行，不能仅配置CORS：

| 请求条件 | 处理 |
| --- | --- |
| Host（含端口）不在显式配置列表 | 403 HOST_NOT_ALLOWED；不使用 *.localhost 或任意后缀匹配 |
| 写请求的 Origin 为允许的完整 scheme/host/port | 继续 JSON、版本、资格校验 |
| 写请求缺少 Origin、为 null 或不在允许列表 | 403 ORIGIN_NOT_ALLOWED；本地 CLI/测试调用需显式附上已配置 Origin，无绕过开关 |
| GET/HEAD 缺少 Origin，Host 合法 | 允许读取，仍不扩大 CORS；显式携带非法 Origin 则拒绝 |
| OPTIONS | 仅给合法 Host、允许的 Origin/方法/头返回 204；非法来源仍拒绝；不执行写入 |
| 写请求 Content-Type 非 application/json | 415 UNSUPPORTED_MEDIA_TYPE；DELETE 无正文时可省略 Content-Type，但仍校验 Origin |

所有POST/PATCH/PUT/DELETE都是写请求。APP_ENV必须显式为development或production，缺失/未知值启动失败，不自动降级为宽松开发模式。production指现有的本机交付环境，不表示支持公网。以下端口是配置示例，脚手架须将实际值、代理上游及Host/Origin列表一起写入运行说明；使用localhost须单独配置，不能视为127.0.0.1的自动别名。

| 配置项 | development：本机开发 | production：本机交付 |
| --- | --- | --- |
| 浏览器入口与代理 | Vite示例http://127.0.0.1:5173，代理/api到本机API；允许显式配置的调试页面直连API | Nginx示例http://127.0.0.1:8080，提供静态文件并代理/api；宿主机入口仅绑定127.0.0.1 |
| API可达性 | Uvicorn示例127.0.0.1:8000，允许Vite、本机CLI及调试直连，不要求Nginx存在 | API不映射宿主机端口，业务请求只经现有内部容器网络的Nginx入口；不因配置Origin而允许绕过代理直连 |
| allowed_hosts示例（含端口） | 127.0.0.1:5173、127.0.0.1:8000，分别用于保留原Host的Vite转发和直连 | 127.0.0.1:8080，只接受配置中的交付入口Host |
| allowed_origins示例（完整来源） | http://127.0.0.1:5173、http://127.0.0.1:8000，后者用于显式启用的本机API调试页 | http://127.0.0.1:8080，不自动继承开发端口 |
| 转发头与可信代理 | Vite保留原始Host；直接请求不信任Forwarded/X-Forwarded-*，不能用它们覆盖Host或来源校验 | Nginx保留原始Host（含端口），清除客户端伪造的转发头后按需重建；仅将该受控代理配置为可信代理，转发头不替代上述允许列表 |
| CLI与健康检查 | CLI写请求仍附允许Origin和合法Host；GET健康检查可无Origin | 用户CLI通过Nginx入口且遵守相同校验；容器内只读健康检查可从本容器回环访问健康端点并附合法Host，此例外不开放业务写接口 |

两种环境均不用Host/Origin通配符，不允许缺失/null Origin的写入，也不设置跳过校验的开发开关。显式跨域调试的CORS只允许已配置Origin及GET/HEAD/POST/PATCH/PUT/DELETE/OPTIONS；请求头允许Content-Type、Idempotency-Key，响应暴露X-Request-ID、Content-Disposition、Idempotency-Replayed，不启用凭据模式。这里的Origin校验不新增账号鉴权，也不防御能直接控制本机进程的攻击者。依据：[Origin](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin)、[OWASP 来源校验](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#using-standard-headers-to-verify-origin)。

### 1.2 响应结构

单对象响应直接返回对象，不额外包裹 data。普通列表返回：

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

统一普通分页：page 从 1 开始，page_size 默认 20、范围 1～100；超出页返回空 items，并保留实际 total。复习到期队列采用第 8 节的游标契约。

查询参数省略表示默认值；可选过滤条件通过省略清空，不传字符串 `null`。未知参数返回 422。查询关键词去除首尾空白，空串等同未设置；按普通子串匹配，不允许用户输入 SQL 或通配表达式。

资料、任务、笔记与卡片管理列表均支持 topic_status=active/paused/archived/unarchived/all；unarchived 表示 active 或 paused。省略时：有 topic_id 则按 all；无 topic_id 则按 unarchived；资料列表 archived=true 的独立归档入口省略时按 all。显式 topic_status 始终生效，topic_id 与其不匹配则空列表。archived 参数只过滤子项自身 archived_at，不能代替 topic_status。直接 GET 详情、事件、来源与导出不套用列表隐藏规则。

从某个资料/笔记查看其关联内容时，调用方先使用该对象详情中的topic_id，连同resource_id/note_id提交列表查询；不借用全局当前选中主题。仅传resource_id或note_id仍按无topic_id的全局列表默认值过滤，不隐式豁免归档主题。主题与关联ID条件按交集过滤，不匹配为空列表，不返回其他主题记录。

### 1.3 写入与版本

- POST 创建成功返回 201、对象和 Location；更新、状态命令返回 200 和更新后的对象；删除成功为 204，无 JSON body。
- 更新请求显式携带 `expected_version`；缺少版本返回 422，版本过期返回 409。
- PATCH 只更新出现的字段；省略表示不变，null 仅用于允许清空的可选关联或日期。不可变字段如 topic_id 不接受 PATCH。
- 所有 PATCH 至少提供一个允许修改的内容字段，仅有 expected_version 返回 422。内容请求中的布尔、整数、字符串不互相隐式转换；版本为正整数十进制字符串，无前导零，范围不超过 BIGINT UNSIGNED。
- 同版本多字段更新一次提交，只递增一次实体 version；改变任务集合或顺序还递增主题 version，使旧排序列表失效。
- 创建请求除另有规定外不保证重试幂等；网络超时不应自动重复 POST 创建。前端先检查列表或提示确认结果，不将它与评分幂等混淆。
- 状态操作已处于目标状态且版本正确时返回当前对象、不新增事件；版本已过期仍返回 409。任务完成和评分回放按其专用规则处理。

### 1.4 错误格式

```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "内容已更新，请查看最新版本后重试。",
    "field_errors": {},
    "request_id": "req-example",
    "details": { "current_version": "4" }
  }
}
```

field_errors 为字段路径到字符串数组的映射，例如 `{"url":["仅支持 HTTP 或 HTTPS 地址"]}`。details 为可选结构化补充；客户端依据 code 判断行为，不解析 message。不暴露 SQL、密码或异常堆栈。

| HTTP | code | 含义与前端处理 |
| --- | --- | --- |
| 400 | INVALID_CURSOR | 游标无效、过期或与筛选不匹配，重载队列 |
| 403 | ORIGIN_NOT_ALLOWED | 来源不被允许 |
| 403 | HOST_NOT_ALLOWED | 请求 Host 不被允许，检查本机入口配置 |
| 404 | NOT_FOUND | 对象不存在，提供返回入口 |
| 409 | VERSION_CONFLICT | 保留输入，获取最新版本后由用户决定 |
| 409 | TOPIC_READ_ONLY | 主题已归档，刷新状态并停止写入 |
| 409 | RESOURCE_READ_ONLY | 资料自身归档，保留输入，提示先恢复资料 |
| 409 | TOPIC_NOT_ACTIVE | 主题暂停或归档，不能加入学习/评分 |
| 409 | CARD_PAUSED / CARD_NOT_DUE | 卡片不再可评分，刷新队列 |
| 409 | CARD_HAS_HISTORY | 卡片已有历史，不允许永久删除 |
| 409 | IDEMPOTENCY_KEY_REUSED | 同一键用于不同请求，不能当成功回放 |
| 409 | ORDER_SET_CHANGED / TASK_COMPLETED | 排序集合改变或任务不允许相应修改 |
| 409 | LOCAL_DATE_CHANGED | 当天已变化，刷新今日页面再操作 |
| 413 | PAYLOAD_TOO_LARGE | 请求超过部署上限，保留输入并提示 |
| 415 | UNSUPPORTED_MEDIA_TYPE | 不支持的 Content-Type 或 Content-Encoding |
| 422 | VALIDATION_ERROR | 字段、URL、枚举、关联主题或参数错误 |
| 503 | SERVICE_UNAVAILABLE | 暂时不可用；保留内容，安全重试 |
| 500 | INTERNAL_ERROR | 未预期故障，显示 request_id 便于排查 |

FastAPI 默认校验错误也转换为此结构。下载请求失败尚未开始发送文件时同样返回 JSON 错误。

资格校验顺序：结构/安全校验 → 已提交幂等评分/重置回放（或已完成任务回放）→ 锁内存在性与版本 → 业务资格。普通编辑的归档主题报 TOPIC_READ_ONLY；完成任务、当日覆盖 PUT 与新评分的非活动主题报 TOPIC_NOT_ACTIVE；其后再检查资料只读、卡片暂停/到期等子项状态。评分失败不前进，保留当前卡及已提交的原键/body；资格失效时禁用评分并刷新队列，404 则提示已不存在。笔记冲突或只读仍保留本地文本，禁止自动覆盖。无幂等回放时，复习新键旧版本优先报 VERSION_CONFLICT。

## 2. 公共数据结构与枚举

### 2.1 资源摘要

可变实体通用响应字段：`id: UUID`、`version: string`、`created_at: UTC`、`updated_at: UTC`。关联字段采用明确 ID；可选关联为 null，不用空字符串。

来源摘要：`{id, title, archived_at, topic_status}`；不存在可选来源时为 null。来源已归档仍返回其 ID 与标题，不假装为无关联。主题状态归档与资料自身归档分别表达。

详情返回 `allowed_actions: Action[]`，列表省略。Action 枚举为 edit/pause/archive/restore/complete/reorder_tasks/reset/delete/export；edit 依对象状态只开放 FEATURES.md 操作矩阵允许的字段，export 对应对象既有导出格式，不扩展新导出能力。只返回当前对象适用且当前资格允许的动作；allowed_actions 只是查询时快照，写入时必须重新校验。归档主题可返回 restore/export，归档主题下子对象仅允许既有只读导出（无导出能力的对象返回空数组）。

| 概念 | API 值 |
| --- | --- |
| 主题状态 | active / paused / archived |
| 资料类型 | link / excerpt |
| 阅读状态 | unread / read |
| 任务状态 | todo / completed |
| 评分 | forget / fuzzy / remember |
| 复习事件类型 | review / reset |
| 当日覆盖 | include / skip |
| 目标类型 kind | task / card |
| 学习日 | 1～7 的不重复整数数组，1 为周一；API 不暴露数据库位掩码 |

priority 固定为 low / normal / high，映射数据库 10 / 20 / 30，创建默认 normal；不把任意整数排序值暴露给 UI。

### 2.2 输入边界

所有输入采用 [FEATURES.md 第 2 节](FEATURES.md#输入边界)已确认边界，Pydantic/OpenAPI 与前端使用相同的 min/max 与枚举。标题去首尾空白，正文不裁剪；长度按 Unicode 码点计算，请求体按实际接收字节计算，两者独立校验。内容超长返回 422，原始请求体超过 1 MiB 返回 413；不能把数据库报错当输入校验。所有未指定默认值的创建内容字段为必填，source_description 默认空串，url/excerpt 非对应字段及可选关联/计划日期默认 null。

### 2.3 完整响应字段

下面定义用于 Pydantic/OpenAPI 的字段集合；“+”表示字段并集，不是返回嵌套包装。除明确写“可省略”的错误 details 外，所列字段均必返，nullable 字段返回 null。正文预览为原文本前 200 个 Unicode 码点，仅作纯文本展示。

| 类型 | 字段及类型 |
| --- | --- |
| Entity | id: UUID；version: Version；created_at/updated_at: UTC 时间字符串 |
| Source | id: UUID；title: string；archived_at: UTC 或 null；topic_status: TopicStatus |
| TopicSummary | Entity + title/goal: string；priority: Priority；status: TopicStatus；archived_at: UTC 或 null |
| TopicDetail | TopicSummary + counts: TopicCounts；allowed_actions: Action[] |
| TopicCounts | resources/tasks_todo/tasks_completed/notes/cards: 非负整数，各字段必返 |
| ResourceSummary | Entity + topic_id: UUID；topic_title/title/source_description: string；topic_status: TopicStatus；type: link/excerpt；reading_status: unread/read；archived_at: UTC或null；url: string或null；excerpt_preview: string或null（仅excerpt非null） |
| ResourceDetail | ResourceSummary 去掉 excerpt_preview + excerpt: string或null；allowed_actions: Action[] |
| Task | Entity + topic_id: UUID；topic_status: TopicStatus；title: string；estimated_minutes/position: 正整数；planned_date: 本地日期或null；resource_id: UUID或null；status: todo/completed；archived_at: UTC或null |
| TaskDetail | Task + source: Source或null；allowed_actions: Action[] |
| Completion | id/task_id: UUID；occurred_at: UTC；local_date: 本地日期；timezone: IANA字符串；estimated_minutes_snapshot: 正整数 |
| CompletionResult | task: TaskDetail；completion: Completion |
| TaskOrderResult | topic_version: Version；items: 数组，每项包含 id: UUID、position: 正整数、version: Version，按position升序 |
| NoteSummary | Entity + topic_id: UUID；topic_status: TopicStatus；title: string；resource_id: UUID或null；archived_at: UTC或null；body_preview: string |
| NoteDetail | NoteSummary 去掉 body_preview + body_markdown: string；source: Source或null；allowed_actions: Action[] |
| CardSummary | Entity + topic_id: UUID；topic_status: TopicStatus；note_id: UUID或null；question/policy_version: string；stage: -1～5整数；due_at: UTC；is_paused: boolean |
| CardDetail | CardSummary + answer: string；source: Source或null；allowed_actions: Action[] |
| ScheduleSummary | id: UUID；version: Version；stage: -1～5整数；due_at: UTC；is_paused: boolean；policy_version: string |
| ReviewEvent | 第8.2节event示例的全部字段；rating仅reset为null，其余为Rating；old/new_stage为-1～5整数；所有card_version_*为Version |
| ReviewResult / ResetResult | card: ScheduleSummary；event: ReviewEvent |
| Override | Entity + kind: task/card；target_id: UUID；local_date: 本地日期；action: include/skip；card只允许skip |
| Settings | daily_minutes: 整数；learning_days: 整数数组；timezone: IANA字符串；version: Version；created_at/updated_at: UTC |
| DueItem | id/topic_id: UUID；question: string；due_at: UTC；version: Version |
| DuePage | items: DueItem[]；as_of: UTC；next_cursor: string或null；has_more: boolean，等于next_cursor非null |

Version 为1～18446744073709551615的十进制字符串；TopicStatus、Priority、Rating 使用本节枚举。Page<T> 必返 items: T[]、page/page_size: 正整数、total: 非负整数；页码与页大小规则见第1.2节。ReviewEvent、Today 与错误结构分别以第8.2、9.1、1.4节为完整定义。错误 field_errors 为 string 到 string[] 的映射；details 可省略，版本冲突时必有 current_version: Version（创建覆盖时不存在则为null），覆盖冲突另外返回 current_override_id: UUID或null。

## 3. 学习主题

### 3.1 查询与创建

| 方法与路径 | 请求 | 成功结果 |
| --- | --- | --- |
| GET `/topics` | status 默认 active，可选 paused/archived/all；q；sort 默认 updated_desc，可选 created_asc/priority_desc；分页 | TopicSummary 列表 |
| POST `/topics` | title、goal 可选默认空串、priority 可选 | 201 TopicDetail，初始 active |
| GET `/topics/{id}` | 无 | 200 TopicDetail |
| PATCH `/topics/{id}` | expected_version；title/goal/priority 至少一项 | 200 TopicDetail |

所有普通排序以ID升序作稳定兜底（事件历史明确为ID倒序的除外）；title_asc采用数据库已锁定排序规则，不能由浏览器另排整页。TopicSummary包含公共字段、title、goal、priority、status、archived_at。详情额外返回counts：resources、tasks_todo、tasks_completed、notes、cards；默认统计未归档资料/任务/笔记及所有保留卡片，包含暂停卡。统计不混入分页列表，不因主题归档隐藏其自身详情汇总。

详情的四个内容分区通过各模块列表传 topic_id 独立分页，不一次返回所有正文。主题暂停时仍可编辑，归档时 PATCH 返回 TOPIC_READ_ONLY。

```json
{
  "title": "Vue 3 入门到实践",
  "goal": "独立完成一个带接口的页面",
  "priority": "high"
}
```

### 3.2 状态命令

| 方法与路径 | body | 规则 |
| --- | --- | --- |
| POST `/topics/{id}/pause` | expected_version | active → paused；退出推荐和复习，不改子项 |
| POST `/topics/{id}/archive` | expected_version、confirm=true | 活动或暂停 → archived；保留关联与历史 |
| POST `/topics/{id}/restore` | expected_version | paused/archived → active；归档恢复清空archived_at |

成功均返回 TopicDetail。confirm 缺失或不是 true 返回 422，它表达操作意图，不替代服务端资格校验。主题恢复不批量改变子项、历史和排程；已为 active 的 restore 按第1.3节返回当前对象。

## 4. 资料库

### 4.1 列表与详情

`GET /resources`：q 匹配标题或来源描述；topic_id；topic_status；reading_status；archived 默认 false，可为 true/all；sort 默认 updated_desc，可选 created_desc/title_asc；普通分页。没有 topic_id 表示跨主题查询，主题过滤不借用当前前端全局选中项。

archived 只过滤资料自身 archived_at。topic_status 默认规则见第1.2节；归档主题不被误当资料自身归档，已归档资料入口使用 archived=true，默认跨全部主题。

`GET /resources/{id}` 返回 ResourceDetail，列表返回 ResourceSummary；字段以第2.3节为准，详情必须返回完整对应内容。

已归档资料仍可GET。先读取ResourceDetail，再使用 `GET /notes?topic_id={resource.topic_id}&resource_id={resource.id}` 查看关联笔记；省略topic_status按all，主题归档不造成伪空列表。无关联笔记时才显示真实空态，不跳转固定示例笔记。返回原资料或列表保留来源ID和筛选上下文。

### 4.2 创建、编辑与归档

| 方法与路径 | 请求字段 | 成功 |
| --- | --- | --- |
| POST `/resources` | topic_id、title、type、source_description 可选、reading_status 默认 unread、对应内容 | 201 ResourceDetail |
| PATCH `/resources/{id}` | expected_version；可修改 title/type/source_description/reading_status/url/excerpt | 200 ResourceDetail |
| POST `/resources/{id}/archive` | expected_version、confirm=true | 200 ResourceDetail，archived_at 非空 |
| POST `/resources/{id}/restore` | expected_version | 200 ResourceDetail，archived_at 清空，不改变阅读状态和关联 |

```json
{
  "topic_id": "11111111-1111-4111-8111-111111111111",
  "title": "Vue 官方文档 · 响应式基础",
  "type": "link",
  "source_description": "Vue 官方文档",
  "reading_status": "unread",
  "url": "https://cn.vuejs.org/guide/essentials/reactivity-fundamentals.html"
}
```

link 要求非空安全 HTTP/HTTPS URL，excerpt 要求非空摘录；另一内容字段可省略或 null，不能提供非空值。PATCH 切换类型时必须同时提交新的内容和将旧内容置 null，避免后台保留错误内容。

阅读状态调整只 PATCH reading_status 与 expected_version，不修改任务。topic_id 不可修改。资料自身归档后 PATCH 返回 RESOURCE_READ_ONLY；活动或暂停主题内允许恢复资料，归档主题内恢复资料返回 TOPIC_READ_ONLY。关联已归档资料不阻止笔记保存或任务学习，来源摘要如实标注归档；任何已有资料均须同主题。无“打开外链 API”，前端用详情 URL 在新标签页打开，服务器不抓取网页。

筛选条件由前端 URL query 保存：进入详情带上返回上下文，返回不重置条件。API 不接受任意 return_url，也不返回固定跳转页面。

## 5. 学习任务

| 方法与路径 | 请求 | 成功结果 |
| --- | --- | --- |
| GET `/tasks` | topic_id、topic_status、resource_id、status 可选；archived 默认 false，可 true/all；sort 默认 position_asc，可 planned_asc；分页 | Task 列表 |
| POST `/tasks` | topic_id、title、estimated_minutes、planned_date 可选、resource_id 可选 | 201 Task，服务端追加主题内顺序 |
| GET `/tasks/{id}` | 无 | TaskDetail，含关联资料摘要 |
| PATCH `/tasks/{id}` | expected_version；title/estimated_minutes/planned_date/resource_id | TaskDetail |
| POST `/tasks/{id}/complete` | expected_version | CompletionResult |
| PUT `/topics/{id}/task-order` | expected_version（主题版本）、task_ids | 新主题版本与任务顺序 |

Task 字段以第2.3节为准。planned_date 和 resource_id 可通过 null 清空。同主题关联错误返回 422。无 start 命令：有资料则进入 GET /notes?topic_id=...&resource_id=... 的关联笔记列表，无资料则进入 GET /notes?topic_id=...；由用户选择或新建，不自动选第一篇，不伪造进行中状态。第一版没有任务/笔记独立归档、恢复或删除接口。

planned_date只接受真实公历日期字符串YYYY-MM-DD，范围为1000-01-01～9999-12-31（含边界），与FEATURES及MySQL DATE支持范围一致。创建省略/null表示无计划日期；PATCH省略不变、null清空。空串、非零填充日期、时间戳、数值、零日期、不存在的日期及越界值均返回422 VALIDATION_ERROR，field_errors.planned_date为可读错误字符串数组。服务端Schema在写入前完成格式、日历及范围校验；前端选择器与手工输入采用同一边界，不按UTC转换，不等数据库异常才报错，也不自动修正或截断日期。过去/今天/未来日期的既有调度规则不变。已完成任务的合法受限字段仍按TASK_COMPLETED拒绝；格式非法先按通用结构校验报422。

例如planned_date="0999-12-31"的字段错误为：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "计划日期不合法。",
    "field_errors": { "planned_date": ["计划日期须为1000-01-01至9999-12-31之间的有效日期。"] },
    "request_id": "req-example"
  }
}
```

排序提交该主题全部未归档任务 ID，含已完成任务；列表分页不改变集合要求。前端先取得完整排序集合再提交，服务端在主题锁内验证无遗漏、无重复、无外来 ID。成功示例：

```json
{
  "topic_version": "8",
  "items": [
    { "id": "22222222-2222-4222-8222-222222222222", "position": 1, "version": "3" }
  ]
}
```

完成结果为第2.3节 CompletionResult。任务已完成时优先返回已有完成结果，不因旧 expected_version 再完成一次；未完成时正常检查版本及活动主题资格。首版不能重新打开任务；已完成任务 PATCH 仅允许 title/resource_id 和 expected_version，提交 estimated_minutes 或 planned_date（即使与原值相同）返回 TASK_COMPLETED，整体不写入。标题/关联资料修改不改变完成快照；任务仍参与排序。

position_asc 为 position升序、ID升序；跨主题同position用ID稳定兜底。planned_asc 为有日期在前、日期升序、position升序、ID升序。任务排序完整集合不受分页及默认主题状态筛选影响，有 topic_id 时取 archived=false、topic_status=all 的全部页。

## 6. 知识笔记

| 方法与路径 | 请求 | 成功结果 |
| --- | --- | --- |
| GET `/notes` | q（标题或正文）、topic_id、topic_status、resource_id、archived 默认 false，可 true/all；sort 默认 updated_desc，可 created_desc/title_asc；分页 | NoteSummary 列表 |
| POST `/notes` | topic_id、title、body_markdown、resource_id 可选 | 201 NoteDetail |
| GET `/notes/{id}` | 无 | NoteDetail |
| PATCH `/notes/{id}` | expected_version；title/body_markdown/resource_id | NoteDetail |

NoteSummary/NoteDetail 以第2.3节为准；预览由前端安全 Markdown 渲染完成，不建立仅服务固定原型文本的 preview API。空正文允许保存，标题必填。

从笔记查看来源卡片使用 `GET /cards?topic_id={note.topic_id}&note_id={note.id}`；主题状态省略时按all，保留归档主题内的只读查看路径。资料关联任务列表同样携带资料的topic_id和resource_id。以上只修正调用上下文，不改变全局列表默认过滤或归档只读资格。

```json
{
  "expected_version": "3",
  "title": "ref 与 reactive",
  "body_markdown": "## 我的理解\nref 包装独立值，reactive 创建对象的响应式代理。"
}
```

成功必须返回新 version 和服务端 updated_at；前端收到成功才标记已保存。冲突时返回 current_version，前端另 GET 最新内容并保留本地文本，不自动覆盖后重试。服务端无离线草稿同步接口；浏览器临时草稿不是保存成功。

## 7. 复习卡管理

| 方法与路径 | 请求 | 成功结果 |
| --- | --- | --- |
| GET `/cards` | topic_id、topic_status、note_id、paused 可选 true/false；sort 默认 due_asc，可 updated_desc；分页 | CardSummary 列表 |
| POST `/cards` | topic_id、question、answer、note_id 可选 | 201 CardDetail |
| GET `/cards/{id}` | 无 | CardDetail |
| PATCH `/cards/{id}` | expected_version；question/answer/note_id | CardDetail |
| POST `/cards/{id}/pause` | expected_version | CardDetail |
| POST `/cards/{id}/restore` | expected_version | CardDetail |
| POST `/cards/{id}/reset` | expected_version、confirm=true；Idempotency-Key | ResetResult |
| DELETE `/cards/{id}` | query expected_version、confirm=true | 204，仅允许没有历史事件的卡片 |
| GET `/cards/{id}/events` | 普通分页；固定 occurred_at 倒序、ID 倒序 | 复习/重置事件列表 |

CardSummary/CardDetail 以第2.3节为准。管理列表不等于到期队列：暂停或未来卡片可在管理入口查到，归档主题内容可通过 topic_status 或主题详情查看。

创建保存快照，stage=-1，due_at 为服务端当前时间。问答编辑不改排程；客户端不得直接 PATCH stage/due_at/is_paused。恢复卡片不解除主题限制。删除已有 review/reset 事件卡片返回 CARD_HAS_HISTORY；成功删除同时清理该卡全部保留日期的覆盖，不删除任何复习历史。

重置与评分同样使用幂等机制，返回 card 和 event，event_type=reset、rating=null、new_stage=-1、new_due_at 为提交时间。允许非到期卡重置，但主题归档不可写；重置不增加评分次数。

## 8. 复习队列与评分

### 8.1 到期队列

`GET /reviews/due` 参数：topic_id 可选、limit 默认 20/最大100、cursor 可选。固定排序 due_at 升序、ID 升序，只有活动主题中未暂停且到期的卡片。

```json
{
  "items": [
    {
      "id": "33333333-3333-4333-8333-333333333333",
      "topic_id": "11111111-1111-4111-8111-111111111111",
      "question": "ref 与 reactive 有什么区别？",
      "due_at": "2026-10-27T00:00:00Z",
      "version": "2"
    }
  ],
  "as_of": "2026-10-27T01:00:00Z",
  "next_cursor": null,
  "has_more": false
}
```

游标是不透明服务端编码，包含上次排序键、as_of 和 topic_id 过滤身份，并校验完整性。后续分页继续使用原 as_of，不保证数据库历史快照；删除、评分、暂停可使下一页缩短。新到期卡需从第一页刷新。非法或不同筛选游标返回 INVALID_CURSOR。

队列不返回答案，避免页面初始意外展示；点击“显示答案”读取 `GET /cards/{id}`。这只是体验控制，不是答案保密协议；用户本就拥有全部学习数据。GET 不更新排程，评分前再次校验资格。独立复习队列不受今日 skip 覆盖影响，今日推荐会排除 skip。

### 8.2 提交评分

`POST /cards/{id}/reviews`，必须提供 `Idempotency-Key`（1～128 ASCII 字符，建议 UUID），JSON body：

```json
{ "expected_version": "2", "rating": "remember" }
```

首次成功与相同请求回放均返回 200，并可用 `Idempotency-Replayed: true/false` 表明是否回放。响应示例：

```json
{
  "card": {
    "id": "33333333-3333-4333-8333-333333333333",
    "version": "3",
    "stage": 0,
    "due_at": "2026-10-28T01:00:00Z",
    "is_paused": false,
    "policy_version": "fixed_interval_v1"
  },
  "event": {
    "id": "44444444-4444-4444-8444-444444444444",
    "card_id": "33333333-3333-4333-8333-333333333333",
    "event_type": "review",
    "rating": "remember",
    "old_stage": -1,
    "new_stage": 0,
    "old_due_at": "2026-10-27T00:00:00Z",
    "new_due_at": "2026-10-28T01:00:00Z",
    "occurred_at": "2026-10-27T01:00:00Z",
    "local_date": "2026-10-27",
    "timezone": "Asia/Shanghai",
    "policy_version": "fixed_interval_v1",
    "card_version_before": "2",
    "card_version_after": "3"
  }
}
```

card 为排程摘要，不是完整 CardDetail。事件历史接口采用上述 event 结构；不公开内部幂等响应存储内容或请求 hash。

- 相同操作、相同键、相同目标/版本/评分：返回原结果，不重复评分；回放优先于当前状态与版本检查。
- 同键不同目标或载荷：409 IDEMPOTENCY_KEY_REUSED。
- 新键但旧版本：409 VERSION_CONFLICT；不能通过换键规避冲突。
- 请求提交中禁用再次评分；网络未知结果时以原键原 body 重试。用户下一次有效复习使用新键。
- stage 和 due_at 服务端计算；忘记为10分钟后、模糊为1天后、记住按新阶段间隔。完整公式见 FEATURES.md。
- UI 在显示答案后才提供评分；API 不引入“已展示答案”的服务端持久化状态。

## 9. 今日学习与覆盖

### 9.1 查询今日安排

`GET /today` 不接受客户端指定“当前时间”或历史日期，服务端基于设置时区计算今天。响应字段：

| 字段 | 类型与说明 |
| --- | --- |
| as_of / local_date / timezone | UTC字符串 / 本地日期字符串 / IANA字符串 |
| daily_minutes / is_learning_day | 整数 / boolean |
| stats | 对象；completed_task_count、review_count、used_estimated_minutes、remaining_minutes、due_card_count，全部为必返非负整数 |
| suggested_tasks | 数组；每项 task_id/topic_id: UUID、title: string、estimated_minutes:正整数、reason_code:Reason、reason_text:string、exceeds_budget:boolean、version:Version；包含有效手动加入任务及自动任务，手动项置前 |
| suggested_reviews | 数组；每项 card_id/topic_id:UUID、question:string、due_at:UTC、estimated_minutes:整数2、reason_code:Reason、version:Version |
| unallocated_minutes | 非负整数，FEATURES.md 第9节定义的未分配时间，不冒充实际空闲时长 |
| exceeds_budget_minutes | 非负整数，FEATURES.md 第9节定义的整体超额 |
| remaining_due_count | 非负整数，stats.due_card_count减suggested_reviews长度；包含今天跳过但仍可从完整队列访问的卡 |
| overrides | Override[]；当日全部覆盖，包括当前资格不符而暂不生效的记录 |

Reason 固定为 DUE_REVIEW、PLANNED_DATE_REACHED、TOPIC_PRIORITY、TOPIC_ORDER、MANUAL_INCLUDE、EXCEEDS_BUDGET。手动任务优先 MANUAL_INCLUDE；自动超额回退任务为 EXCEEDS_BUDGET；其余有日期任务为 PLANNED_DATE_REACHED，无日期高优先级主题任务为 TOPIC_PRIORITY，剩余为 TOPIC_ORDER；复习为 DUE_REVIEW。reason_text 可读但不用于逻辑判断。stats.due_card_count 统计完整活动主题到期队列，不扣今天skip；统计来自事件且不依赖前端计数。

全部字段必返；空数组返回 []。首次使用示例（此处没有主题、任务或卡片，不依赖手动合并分支）：

```json
{
  "as_of": "2026-10-27T01:00:00Z",
  "local_date": "2026-10-27",
  "timezone": "Asia/Shanghai",
  "daily_minutes": 45,
  "is_learning_day": true,
  "stats": {
    "completed_task_count": 0,
    "review_count": 0,
    "used_estimated_minutes": 0,
    "remaining_minutes": 45,
    "due_card_count": 0
  },
  "suggested_tasks": [],
  "suggested_reviews": [],
  "unallocated_minutes": 45,
  "exceeds_budget_minutes": 0,
  "remaining_due_count": 0,
  "overrides": []
}
```

算法、手动占预算、超额与非学习日规则仅以 FEATURES.md 第9节为准。完成任务和评分成功后重取今日数据。

### 9.2 手动安排

`PUT /today/overrides/{kind}/{id}`：

```json
{
  "local_date": "2026-10-27",
  "action": "skip",
  "expected_override_id": null,
  "expected_version": null
}
```

expected_override_id 与 expected_version 均为必填可空字段：同时为 null 表示要求当前不存在覆盖；已有记录时须同时传该记录 UUID 和字符串版本。只提供其中一项为 422；记录身份或版本不匹配为 409 VERSION_CONFLICT。成功返回 200 Override：`{id, kind, target_id, local_date, action, version, created_at, updated_at}`。

覆盖删除后重新创建使用新 UUID。即使新旧记录 version 都是 "1"，旧请求携带的 expected_override_id 也不能更新新记录。首次创建及更新均在目标主题锁内检查当前覆盖，唯一约束作为最后防线。

身份/版本正确且action不变时返回原对象，不更新version/updated_at；action改变时更新两者，skip改include的updated_at作为最近加入时间，手动任务按updated_at、id升序。其他字段不可PATCH覆盖，保证updated_at不被无关编辑改变其排序语义。

local_date 必须等于服务端当前设置时区日期，否则 LOCAL_DATE_CHANGED，避免午夜或修改时区后误改另一天。PUT 验证目标存在、主题活动及相应待办/未暂停资格；include/skip 同日同项只保留一个。

`DELETE /today/overrides/{kind}/{id}?local_date=...&expected_override_id=...&expected_version=...` 撤销覆盖；日期、覆盖 UUID 与字符串版本均必填。日期校验与 PUT 相同。成功 204；当前不存在覆盖为 204，存在但记录身份或版本不匹配为 409。撤销不改任务日期或卡片 due_at；主题随后暂停也允许清除当天覆盖，但不因此进入推荐。

支持 task include/skip（包括未来任务的显式include）与 card skip；card include 返回422 VALIDATION_ERROR。card skip要求卡片当前未暂停且到期。手动加入与自动项合并遵循 FEATURES.md 第9节，不另设API算法。跨日覆盖自动不生效，无需 API 删除全部历史覆盖。

## 10. 设置与导出

### 10.1 设置

`GET /settings` 返回 daily_minutes、learning_days、timezone、version、created_at、updated_at，不暴露 singleton_id。`PUT /settings` 为完整设置替换，必须包含：

```json
{
  "expected_version": "1",
  "daily_minutes": 45,
  "learning_days": [1, 2, 3, 4, 5],
  "timezone": "Asia/Shanghai"
}
```

校验5～1,440整数分钟、学习日不重复且为1～7、有效 IANA 时区；空学习日数组允许，返回200 Settings。保存成功后重取今日建议，不重写历史事件或覆盖日期。浏览器时区变化不触发自动 PUT。

### 10.2 文件导出

| 接口 | 成功 Content-Type | 内容 |
| --- | --- | --- |
| GET `/exports/topics/{id}` | application/json | 主题及关联实体、事件、策略与时间元数据 |
| GET `/exports/notes/{id}` | text/markdown; charset=utf-8 | 标题与 Markdown 正文 |

返回 `Content-Disposition: attachment`，安全文件名及 UTF-8 filename*；HTTP 200 表示文件已完整生成，可开始下载。不存在404，主题归档不阻止只读导出。生成失败先返回 JSON 错误，不将半文件作为成功结果。

主题JSON采用独立schema_version="1.0"；以下根字段全部必返，集合为空为[]，可空字段保留null，不导出allowed_actions、动态counts或内部幂等响应缓存。所有实体、事件及覆盖均来自同一REPEATABLE READ快照，不套用普通列表过滤，不遗漏归档记录。

| 根字段 | 类型与完整内容 |
| --- | --- |
| schema_version / exported_at | string固定"1.0" / UTC字符串 |
| metadata | timezone: 当前设置IANA字符串；policy_versions: 本文件卡片/事件中policy_version去重后字典序数组 |
| topic | Entity + title/goal:string、priority:Priority、status:TopicStatus、archived_at:UTC或null |
| resources | 每项Entity + topic_id:UUID、title/source_description:string、type、reading_status、archived_at、url/excerpt；类型与第2.3节一致，不包含预览/主题标题等派生字段 |
| tasks | 每项Task去掉派生的topic_status |
| notes | 每项Entity + topic_id:UUID、title/body_markdown:string、resource_id:UUID或null、archived_at:UTC或null |
| cards | 每项CardSummary去掉topic_status + answer:string |
| task_completions | Completion[]，按该主题tasks的ID选择，不按发生日期过滤 |
| review_events | ReviewEvent[] + 每项operation:string（review.submit或review.reset）、idempotency_key:string，由idempotency_request_id关联取得；不导出内部响应缓存 |
| daily_overrides | Override[]，选择目标属于本主题的所有保留日期，包含目前不生效的覆盖 |

resources/tasks/notes/cards以id升序；完成/复习事件以occurred_at、id升序；覆盖以local_date、created_at、id升序。关联ID保留，所有下游的可选来源必须在同主题相应集合中；不能把归档来源置null。此格式只用于用户数据导出，不承诺整库恢复或历史问答文本回放。

Markdown文件精确采用UTF-8无BOM，内容为 `"# " + note.title + "\n\n" + note.body_markdown`，不裁剪正文，不额外改写正文换行或Markdown符号；空正文仍保留标题和分隔换行。标题原文保留，不额外解析为HTML。文件名用实体ID兜底，去除路径分隔符、控制字符和平台非法字符，响应头不直接拼接未处理标题。

导出采用本次工程默认值：成品缓冲超过8MiB后转受控临时文件；MAX_EXPORT_BYTES默认128MiB，可通过配置增大，不是业务记录数量限制。超过成品上限在发响应前返回422 VALIDATION_ERROR，field_errors.export提示上限；临时空间不足返回503。成功、失败和断开连接均清理临时文件，应用重启时仅清理自身导出临时目录中的遗留文件，不访问用户备份目录。下载开始后网络中断属于传输失败，前端不得因已收到200就宣称完整下载成功；需完整接收Blob后再触发文件保存，失败保留重试入口。

没有导入接口、外链抓取接口或数据库恢复 HTTP 接口。

## 11. 状态、查询身份与前端同步

| 写入成功 | 至少失效/刷新 |
| --- | --- |
| 主题暂停/归档/恢复 | 所有可能包含该主题的主题/资料/任务/笔记/卡片列表（全局及主题内、全部筛选和分页变体）、该主题及其子项详情/来源摘要/可用操作、今日安排（含统计和覆盖）、相关复习队列 |
| 资料创建/编辑/阅读状态/归档/恢复 | 当前资料详情、所有相关资料列表、主题汇总、相关任务/笔记来源摘要 |
| 任务完成/排序 | 任务详情与主题任务列表、主题汇总、今日统计 |
| 笔记创建/保存 | 当前笔记及搜索列表、主题汇总、卡片来源标题摘要；不改已有卡片答案 |
| 卡片编辑/暂停/恢复/重置/评分 | 当前卡片、主题卡片列表、复习队列、今日统计 |
| 设置保存 | 设置与当前日期/时区相关查询 |
| 任务创建/编辑、卡片创建/删除 | 对应列表/详情、主题汇总、今日安排与相关覆盖；卡片变动同时刷新复习队列 |

资料查询缓存键包含所有有效筛选条件，详情键包含实际 ID。请求乱序时取消或丢弃旧查询结果，不能把上一资料响应覆盖当前资料。进入详情不清空列表 query；阅读状态改变可能使当前项退出原筛选，返回列表应如实刷新并保留原条件。

主题状态命令成功后，先取消或作废上述范围内在成功确认前已发起的在途读取（含命令提交期间发起的读取），避免旧响应回写；用返回的主题状态立即限制当前界面操作，再将全部受影响缓存标为失效。活动查询立即重取，未挂载查询下次使用前重取，不以较长staleTime跳过；全局列表即使尚不含该主题，也可能在恢复后新增成员，不能只按当前items匹配失效。可保守失效上述查询类别的全部列表变体，不要求新增反向依赖索引。服务端仍在每次写入时校验资格，不能把缓存提示当权限。

重取保留关键词、主题状态/自身归档筛选、页码和返回上下文；当前页变空按既有分页规则显示，不跳到默认列表。刷新失败不撤销已成功的主题命令、不展示旧的可写资格，保留笔记/表单输入及本地草稿并提供重试，不清空整套缓存或IndexedDB。以上适用于当前QueryClient；其他标签页按既有重新聚焦、再次进入及状态冲突后的重取规则同步，不引入推送或后台同步服务。

## 12. 契约状态与验收

本文的分页默认值、版本字符串、优先级映射、队列游标、排序完整集合和覆盖身份/版本协议为 v1 拟实施契约；产品分支已按用户确认的 D01～D07 收口，详见[实施就绪记录](docs/product/implementation-readiness.md)。Pydantic/OpenAPI 固化时必须逐字段匹配本文；变更须同步调用方、数据库映射和契约检查，不能重新把已明确条款当作自由建议。

| 用例 | 预期 |
| --- | --- |
| 筛选后进入不同资料并返回 | 条件和实体身份不串页；空结果保留条件 |
| 非法 URL、跨主题关联、未知字段 | 422 字段错误，原内容未被部分写入 |
| 旧版本笔记保存 | 409，最新正文保留、本地输入可恢复 |
| 评分相同键重试、同键异载荷、新键旧版本 | 分别回放、键冲突、版本冲突 |
| 暂停/归档与评分并发 | 服务端锁内资格一致，不在归档后产生新评分 |
| 重复完成任务 | 一次完成快照与估时 |
| 无效排序集合或重复任务 ID | 拒绝整个请求，不保存半套顺序 |
| 午夜前打开页面、午夜后调整安排 | 日期不匹配时明确拒绝并刷新 |
| 归档资料查看、关联来源、导出 | 可读取正确记录，历史关联不丢失 |
| 导出失败 | JSON 错误，无伪成功文件 |

OpenAPI 必须描述全部参数、枚举、nullable、响应结构和错误；生成 TypeScript 客户端后运行契约检查。本文只是接口规范，未进行实际 HTTP 调用、并发测试或联调，不代表实现已通过验收。
