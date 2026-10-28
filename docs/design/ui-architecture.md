# UI架构与Figma Design System

更新：2026-10-27。采用用户指定方案，主色保持 #5476C0。

**成熟的无头组件 + Tailwind CSS + 自定义业务组件 + Figma Design System。组件组合：shadcn-vue + Reka UI + Lucide。**

| 层 | 选择 | 职责 |
| --- | --- | --- |
| 设计规范 | Figma Design System | Token、状态、尺寸、图标与布局 |
| 基础UI | shadcn-vue | 组件源码纳入项目，统一维护样式与属性 |
| 交互原语 | Reka UI | 适用组件的无头交互、键盘、焦点与可访问性 |
| 样式 | Tailwind CSS | 消费语义CSS变量，实现布局和状态样式 |
| 图标 | Lucide | 统一SVG图标，按名称导入 |
| 业务组合 | 自定义Vue组件 | 组合任务、资料、笔记、复习卡与今日建议 |

优先复用shadcn-vue已有封装，确有缺口才直接组合Reka UI原语。Button、Badge等简单组件使用原生语义，不强行叠加复杂交互。避免为同一弹窗维护两套基础交互。

## 组织与映射

- `components/ui`：Button、Input、Label、Textarea、Select、Popover、Dialog、AlertDialog、Badge、Alert。
- `components/learning`：LearningTaskItem、ResourceItem、ResourceFilter、NoteEditor、ReviewCard、ReviewRating、TodaySuggestion。
- 页面负责路由、组合与数据连接；基础组件不内置复习排程等领域规则。
- Figma按UI/、Patterns/、Business/分层。原组件ID与实例引用保留，不复制既有页面。
- Button primary对应default，secondary对应outline；quiet是项目扩展浅色变体。default/hover/pressed/focus对应正常/hover/active/focus-visible；disabled和loading阻止重复提交。
- 普通表单/筛选使用Dialog；归档/重置确认使用AlertDialog，明确取消和确认，不因点击遮罩执行危险操作。

## 设计变量

基础色→语义色→UI contract→CSS variables→Tailwind→UI组件→业务组件。

Figma新增UI contract集合，14项别名为：primary、primary-foreground、background、foreground、card、card-foreground、muted、muted-foreground、accent、accent-foreground、border、input、ring、destructive。

这是本项目的设计契约，不代表与外部UI Kit自动同步。设计变量和组件调整需要同步代码与映射文档。

2026-10-27用户确认的配色修复以[组件映射](component-map.md)的14项Token表为准：品牌保持#5476C0，primary=#425E9F、primary-foreground=#FFFFFF，普通辅助文字使用深色Token，按钮统一14px Medium。Figma的变量别名、控件填充和回退色现已同步，代表截图已复核；证据见[设计状态记录](figma-state.json)的 accessibilitySync，实际Vue组件仍待开发验收。

## Lucide规范

16px用于紧凑操作、20px用于常规操作、24px用于独立图示；标准24×24网格与2px描边。颜色继承语义Token。

Search搜索、X关闭、ChevronDown下拉、ArrowLeft返回、Archive归档、BookOpen学习。纯图标按钮提供可访问名称，装饰图标不重复朗读。

使用官方Vue包并按需导入。当前Lucide v1官方名称为 `@lucide/vue`，旧版为 `lucide-vue-next`；开发时结合shadcn-vue版本锁定兼容依赖，不重复安装。

现有页面的关闭、返回、搜索、下拉、添加、编辑、归档、外链和品牌图形已使用Lucide SVG实例。设计资产固定采用lucide-static 0.468.0（ISC），保存于assets/lucide；该设计资产版本不决定未来Vue依赖版本。

## 实现与验收边界

既有记录描述此前设计迁移；本轮仅修复文档，没有安装依赖、创建应用或修改Figma。新配色需同步画布并截图复核。弹窗焦点锁定与返回、Esc、选择器键盘操作、加载防重、错误保留输入、可访问名称需在真实Vue应用验收。Figma点击不能替代这些验收。

## 官方依据

- [shadcn-vue介绍](https://www.shadcn-vue.com/docs/introduction)
- [Reka UI介绍](https://reka-ui.com/docs/overview/introduction)
- [Lucide图标与官方包](https://lucide.dev/guide/)
- [Lucide v1包名称变更](https://lucide.dev/guide/version-1)
