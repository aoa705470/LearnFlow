# LearnFlow 设计交付与组件映射

日期：2026-10-23。产品范围已获用户确认；主色由用户指定为 `#5476C0`。本次交付是 Figma Design 可编辑页面及预设交互原型，尚未实现前后端。

## 设计入口

- [全新设计文件](https://www.figma.com/design/XQ8hWOsA2rFBv1mT4cMCuE?node-id=8-2)
- [桌面端可点击原型](https://www.figma.com/proto/XQ8hWOsA2rFBv1mT4cMCuE/LearnFlow?node-id=8-2&starting-point-node-id=8%3A2&scaling=scale-down)
- [手机端可点击原型](https://www.figma.com/proto/XQ8hWOsA2rFBv1mT4cMCuE/LearnFlow?node-id=18-2&starting-point-node-id=18%3A2&scaling=scale-down)
- [基础规范](https://www.figma.com/design/XQ8hWOsA2rFBv1mT4cMCuE?node-id=7-60)
- [组件预览](https://www.figma.com/design/XQ8hWOsA2rFBv1mT4cMCuE?node-id=27-245)

旧 LearnFlow 文件未修改、未删除。本次使用独立的新文件。

## 文件组织

| Figma 页面 | 内容 |
| --- | --- |
| 01 · 核心页面与可点击原型 | 19 个桌面画板，基准 1440 × 960，含核心流程及关键状态 |
| 02 · 组件与设计规范 | 23 个主组件、38 个变量、8 个文字样式、规范与实例预览 |
| 03 · 移动端核心流程 | 9 个 390 × 844 画板，覆盖学习、笔记、制卡、回忆、评分与进度 |

## 交互走查路线

1. 首页点击第一项“开始学习” → 笔记 → 完成学习 → 创建并复习 → 展示答案 → 任一评分 → 今日进度。
2. 笔记右侧“保存失败示例” → 重新保存 → 明确的保存成功反馈。
3. 学习偏好 → 30 分钟 → 保存偏好 → 首页只推荐 20 分钟任务，另有 4 分钟复习和 6 分钟弹性。
4. 从原型流程“02 首次使用”进入空态 → 创建学习主题 → 查看主题详情。
5. 手机端完成对应的笔记、制卡和评分闭环。

原型展示固定示例内容和状态。文本输入、搜索、筛选、真实保存与动态排程属于后续产品实现；次要列表入口可以共用示例笔记或资料详情。评分时间是固定示例，不表示实际写入数据库。

## 设计变量

| Token | 值 | 用途 |
| --- | --- | --- |
| `--color-primary` | `#5476C0` | 品牌主色、填充按钮、进度条 |
| `--color-primaryHover` | `#425E9F` | 主按钮悬停 |
| `--color-primary-text` | `#425E9F` | 小字号品牌文字，提高对比度 |
| `--color-soft` | `#EDF1FA` | 选中态和浅色强调区 |
| `--color-canvas` | `#F6F7FB` | 页面背景 |
| `--color-surface` | `#FFFFFF` | 卡片与输入区域 |
| `--color-ink` | `#202B43` | 正文 |
| `--color-muted` | `#65718A` | 辅助信息 |
| `--color-border` | `#E1E6F0` | 边框与分隔 |
| `--color-amber` / `--color-amberSoft` | `#9A5E16` / `#FFF5E5` | 重试和未同步状态 |
| `--color-red` / `--color-redSoft` | `#B74444` / `#FDEEEE` | 保存错误和忘记反馈 |

语义色通过别名引用 Primitives。变量设定了作用域和 WEB 语法，实际 ID、别名、模式及样式记录见 `figma-state.json`。这些是后续 CSS 的设计契约，尚无已实现样式表。

间距：4 / 8 / 12 / 16 / 24 / 32 / 40。圆角：8 / 12 / 20。主要操作高度：44。

字体统一为 Noto Sans SC。Display 32/44 Bold；Title 24/36 Bold；Heading 18/28 Medium；Body 14/24 Regular；Label 14/22 Medium；Caption 12/20 Regular；Metric 28/38 Bold；Action 19/28 Bold。

白色与主色对比度约 4.44:1，因此填充主按钮使用 19px Bold 大字号；小字号强调文字改用深色语义值。后续实现不得把填充主按钮随意改为 14px 白字。

## Figma → Vue 组件建议

| Figma 主组件 | Node ID | 计划中的 Vue 对应 | 变体 / 属性 |
| --- | --- | --- | --- |
| Button | 7:32 | `components/ui/button` | 5 类 × Default/Hover/Disabled，共 15 变体；Label |
| NavItem | 7:37 | `components/layout/SidebarNavItem.vue` | Default/Active；Label |
| Badge | 7:44 | `components/ui/badge` | Neutral/Green/Amber；Green 为沿用的内部轴名称，实际显示品牌蓝；Label |
| TaskRow | 7:45 | `components/learning/TaskRow.vue` | Title、Meta、Action |
| TopicCard | 7:50 | `components/learning/TopicCard.vue` | Tag、Title、Description、Meta |
| ResourceRow | 7:55 | `components/learning/ResourceRow.vue` | Title、Meta |

这些为本文件本地组件，不声称已经导入或发布 shadcn 远程库，也未创建 Code Connect。后续实现以 shadcn-vue 基础组件承载交互与可访问性，再套用本项目 Token。

## 已执行验证

- 截图检查核心桌面页面、异常状态、预算切换、手机闭环及组件预览，并修复自动布局导致的裁切。
- 桌面端：19 个画板，187 个导航跳转，13 项关键路径连接检查通过。
- 手机端：9 个画板，27 个导航跳转，8 项关键路径连接检查通过。
- 两端均无无效目标、无结构溢出；检查范围内文字均使用 Noto Sans SC，完整 UI 未使用扁平图片替代。
- 验证依据为 Figma 节点、原型反应图和渲染截图；没有宣称完成浏览器逐次点击测试或完整无障碍审计。

后续编辑应优先保留主组件及节点 ID，并更新交付状态记录；不要重新复制整页作为常规迭代方式。
