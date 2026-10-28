# LearnFlow 当前设计

当前唯一开发参考：[LearnFlow · 精简核心原型 v2](https://www.figma.com/design/bSNX31fo76f9NDomQkmXgy)。主色保持 **#5476C0**。

2026-10-27已将确认配色同步至Figma：14px按钮配白字使用#425E9F背景，普通辅助文字使用深色Token；以[组件映射](component-map.md)为准。14项Token、共享按钮状态及桌面/手机实例已核对，6个代表节点截图已复核；记录见[设计状态](figma-state.json)的 accessibilitySync。实际应用验收及剩余验证见[实施就绪记录](../product/implementation-readiness.md)。

UI方案：**shadcn-vue + Reka UI + Lucide + Tailwind CSS + 自定义业务组件**。见 [UI架构](ui-architecture.md) 和 [Figma实现契约](https://www.figma.com/design/bSNX31fo76f9NDomQkmXgy?node-id=34-129)。

- [桌面原型](https://www.figma.com/proto/bSNX31fo76f9NDomQkmXgy/LearnFlow?node-id=3-2&starting-point-node-id=3%3A2&scaling=scale-down)
- [手机原型](https://www.figma.com/proto/bSNX31fo76f9NDomQkmXgy/LearnFlow?node-id=7-477&starting-point-node-id=7%3A477&scaling=scale-down)
- [设计基础与按钮状态](https://www.figma.com/design/bSNX31fo76f9NDomQkmXgy?node-id=15-88)

## 结构

| 页面 | 内容 |
| --- | --- |
| 00 · 设计基础 | 视觉语言、按钮、字段、公共组件、弹窗、原型边界 |
| 01 · 桌面核心流程 | 16个完整页面、20个弹窗，3条流程起点 |
| 02 · 手机核心流程 | 6个390px页面 |

主线为今日学习→资料→笔记→制卡→回忆→反馈。管理流程包括资料筛选、阅读状态、归档入口及主题暂停/归档/恢复。使用共享变量表达部分状态，不再为所有组合复制整页。

## 验证边界

2026-10-27 的既有设计交付记录记载：已统一现有桌面/手机按钮、29个表单字段和20个弹窗，并接入Lucide SVG组件；桌面控件与弹窗直接子节点边界检查无溢出，代表性截图已复核，原按钮点击动作与可见性绑定保留。这些是历史交付记录，该轮文档修复未重新验证画布或浏览器点击；后续配色同步证据以 accessibilitySync 为准，本次未新增浏览器点击验收。[基础组件迁移记录](ui-migration-state.json)记录图标、按钮属性与输入组件；[页面迁移及验证记录](ui-page-migration.json)记录桌面/手机替换、弹窗调整和截图节点。

代表性截图、弹窗布局和按钮文字边界已检查。8个原型动作分支静态执行通过，见 figma-state.json。浏览器首页已加载，但点击工具超时，完整实际点击验收尚未完成。

表单为预填示例，不支持任意输入。任意组合搜索、实际导出、持久化、并发、排程和错误恢复需前后端实现。空结果画板用于视觉验收，产品界面不放测试路径按钮。

按用户要求，旧Figma文件的画板和组件内容已清理；旧云文件本身仍为空文件。项目旧版设计记录已删除，不再作为开发入口。

关联文档：[PRD](../product/learnflow-v1-prd.md)、[组件映射](component-map.md)、[覆盖范围](prd-figma-coverage.md)。
