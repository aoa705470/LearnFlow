# LearnFlow v2 公共组件

更新：2026-10-27。UI组合为 **shadcn-vue + Reka UI + Lucide + Tailwind CSS**，通过自定义业务组件和Figma Design System统一设计与实现。详见 [UI架构](ui-architecture.md)。

当前文件：[精简核心原型 v2](https://www.figma.com/design/bSNX31fo76f9NDomQkmXgy)。

## 变量与尺寸

基础变量保存原始值，语义变量引用基础变量，Web代码使用 var(--lf-color-brand) 等CSS变量。Prototype集合仅用于示例状态。

新增UI contract集合，通过别名映射为 --primary、--background、--foreground、--card、--border、--input、--ring 等shadcn语义变量，供Tailwind消费，不复制第二份品牌颜色。

品牌色#5476C0保留；深色强调/操作色#425E9F；正文#202D43；普通辅助文字#425E9F；背景#F6F8FC；表面#FFFFFF；边框#DFE5EF；浅色强调#EDF2FC；成功#32755F；错误#B33C46。原辅助色#738097仅保留作非文字装饰或禁用态，不用于普通小字号信息文字。

文字层级32/24/20/16/14/13px；主次按钮统一14px Medium、20px行高，主按钮深色#425E9F配白字；hover背景#365089、pressed背景#2E4474；focus-visible保持文字配色并提供独立焦点环。间距4/8/12/16/20/24/32/40px。

以下为用户于2026-10-27确认的实现契约，已同步至Figma画布并复核代表截图，证据见[设计状态记录](figma-state.json)的 accessibilitySync。品牌底色白字约4.4402:1，不用于14px普通文字；#425E9F配白字约6.2999:1。普通文字目标至少4.5:1，禁用态豁免不延伸到加载态。依据：[W3C文字对比度](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)。

| UI contract / CSS变量 | 已确认实现值 |
| --- | --- |
| primary / primary-foreground | #425E9F / #FFFFFF |
| background / foreground | #F6F8FC / #202D43 |
| card / card-foreground | #FFFFFF / #202D43 |
| muted / muted-foreground | #F6F8FC / #425E9F |
| accent / accent-foreground | #EDF2FC / #425E9F |
| border / input | #DFE5EF / #DFE5EF |
| ring / destructive | #5476C0 / #B33C46 |

--lf-color-brand仍为#5476C0，primary已改为操作色别名，不复制或修改品牌原始色；color/muted引用深色强调基础变量，旧muted基础值保留。14项Token已逐项读取核对，默认/hover/pressed/focus/loading/disabled组件截图已复核，焦点环引用品牌色；实际应用的键盘与焦点验收仍待实现后执行。

| Figma组件 | 节点 | 状态数与内容 | Vue对应 |
| --- | --- | --- | --- |
| UI/Button | 2:37 | 18种常规状态 + 1种128×40紧凑按钮 | shadcn-vue Button |
| UI/Field | 15:149 | 7：默认/悬停/聚焦/已填/错误/禁用/只读 | Input+Label+Textarea+提示 |
| UI/Input | 43:281 | Value、搜索图标、选择器图标属性；页面按输入/选择/多行用途组合 | Input / SelectTrigger / Textarea |
| Icon/Lucide/* | 43:114起 | 13个官方SVG组件；24网格缩放为16px操作图标 | Lucide按名称导入 |
| UI/NavigationItem | 16:51 | 3：默认/悬停/当前页 | RouterLink+Lucide |
| UI/StatusBadge | 16:59 | 4：活动/暂停/归档/到期 | shadcn-vue Badge |
| UI/InlineAlert | 16:67 | 3：信息/成功/错误 | shadcn-vue Alert |
| Business/LearningTaskItem | 16:76 | 2：待办/完成 | Card+Badge+Button+Lucide |
| Patterns/Dialog | 16:84 | 3：确认/表单/筛选 | Dialog/AlertDialog，适用交互使用Reka UI |

按钮和字段提供Label属性。组件状态展示使用实例。状态规范不代表所有键盘、加载和悬停行为都已在原型模拟。

## 使用规则

- 桌面常规按钮高40px，返回入口36px，关闭按钮32px；手机按钮44px。宽度容纳文字、16px图标和左右留白。
- 单行表单高40px、圆角8px，长内容用多行控件。27个桌面字段及2个手机字段已使用共享UI/Input实例。
- 加载时保持宽度并禁止重复提交；禁用需说明原因。错误不清空输入，只读允许查看。
- 确认弹窗480px，筛选/管理560px，复杂表单640px；内边距24px。
- 20个现有弹窗已统一20px标题、12px圆角、紧凑底部操作；取消/确认靠右，筛选重置靠左。
- 筛选搜索框512px，主题与阅读状态各248px。重置靠左，取消与应用靠右，仅一条分隔线。
- 长字段独占一行；短字段可并排。操作按钮横向排列，避免多条满宽按钮。
- 资料详情页：返回入口位于标题上方；主题与资料类型放在标题下；阅读状态在工具栏左侧，修改状态、编辑和归档放在右侧。三份资料详情使用同一布局。
- 实例描边同时提供语义变量和正确回退色，避免渲染为白色缺边。
- 原型提供关闭按钮及遮罩关闭。Esc、Tab焦点锁定、焦点返回、未保存离开提示在实际应用实现。
