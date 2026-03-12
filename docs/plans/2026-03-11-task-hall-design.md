# 独立任务大厅客户端设计文档

- 日期: 2026-03-11
- 状态: 已评审通过
- 关联系统: 2026_teaching_system

## 1. 目标与边界

任务大厅作为独立第三客户端（独立登录入口、路由、导航），服务三方主体：
- 企业方: 注册、资质审核、发布任务、验收、信誉分管理。
- 执行方: 复用教学系统账号（教师/学生在任务大厅同权），抢单、交付、查看收益。
- 平台方: 规则配置、审核、风控、仲裁。

当前阶段优先支持 ComfyUI 任务，后续扩展客服智能体、短视频等赛道。

## 2. 账号与登录

### 2.1 执行方登录

- 复用教学系统账号体系。
- 允许免登录（SSO）进入任务大厅。
- 教师账号与学生账号在任务大厅内不区分角色能力，按统一抢单规则处理。

### 2.2 企业方登录

- 企业可独立注册登录任务大厅。
- 企业可发布任务的前提: 资质审核通过（不要求保证金/预充值作为硬门槛）。

## 3. 企业信誉分与上架机制（v1）

### 3.1 核心规则

- 企业初始信誉分: 80。
- 自动上架阈值: 信誉分 >= 60。
- 人工审核阈值: 信誉分 < 60。
- 从受限恢复: 一到 60 立即恢复自动上架。
- 信誉分范围: 0 ~ 100（封顶/封底）。

### 3.2 状态机

- AUTO: 自动上架。
- MANUAL_REVIEW: 人工审核上架。

切换规则:
1. 企业创建后默认 `AUTO`。
2. 每次关键事件更新信誉分。
3. 分数 < 60 切到 `MANUAL_REVIEW`。
4. 分数 >= 60 切回 `AUTO`。

### 3.3 任务发布行为

- `AUTO` 企业发布任务后直接进入任务墙（`recruiting`）。
- `MANUAL_REVIEW` 企业发布任务后进入审核池，审核通过才上架。

## 4. 抢单资格与能力分

### 4.1 抢单资格（业务规则）

点击抢单时校验：
- 必须完成任务前置课程。
- 当前无进行中任务（或满足并发上限规则）。
- 任务名额未满。

前端可做预检查提示；后端进行最终判定与原子扣减。

### 4.2 能力分模型

- 权重方案: 课程完成度 40% + 历史任务评分 40% + 考试成绩 20%。
- 公式: `ability_score = c*0.4 + q*0.4 + e*0.2`。
- 抢单时写入资格快照，保留可追溯证据。

## 5. 数据模型（最小可用）

### 5.1 enterprise_profile

- 字段建议: `id`, `user_id`, `company_name`, `license_no`, `verification_status`, `credit_score`, `listing_mode`, `created_at`, `updated_at`。

### 5.2 task

- 字段建议: `id`, `publisher_user_id`, `publisher_enterprise_id`, `task_type`, `title`, `description`, `requirements_json`, `reward_points`, `slots_total`, `slots_remaining`, `publish_status`, `review_required`, `created_at`。

### 5.3 task_claim

- 字段建议: `id`, `task_id`, `claimer_user_id`, `status`, `claim_snapshot_json`, `created_at`, `updated_at`。
- 约束建议: `(task_id, claimer_user_id)` 唯一，避免重复抢同一任务。

### 5.4 enterprise_credit_log

- 字段建议: `id`, `enterprise_id`, `event_type`, `delta_score`, `score_after`, `related_task_id`, `reason`, `created_at`。

### 5.5 capability_score_snapshot

- 字段建议: `id`, `user_id`, `course_completion_score`, `task_quality_score`, `exam_score`, `final_score`, `level`, `rule_version`, `calculated_at`。

## 6. API 清单（任务大厅）

- `POST /hall/auth/sso/exchange`: 教学系统免登录换任务大厅会话。
- `POST /hall/enterprise/register`: 企业注册。
- `POST /hall/enterprise/verify`: 企业资质提交/更新。
- `GET /hall/tasks`: 任务墙列表（招募中/进行中/已结束）。
- `GET /hall/tasks/{id}`: 任务详情。
- `POST /hall/tasks/{id}/claim`: 抢单（后端最终资格校验+扣减名额）。
- `POST /hall/enterprise/tasks`: 企业发布任务（自动上架或入审核池）。
- `GET /hall/enterprise/credit/logs`: 企业信誉分流水。
- `GET /hall/portfolio/mine`: 我的作品集。
- `PATCH /hall/portfolio/{id}/visibility`: 公开/私密切换。
- `GET /hall/wallet/ledger`: 积分流水。
- `POST /hall/wallet/withdraw-requests`: 提现申请。

## 7. 前端设计（v1）

### 7.1 页面范围

- 赏金任务列表页。
- 任务详情页。
- 我的作品集。
- 积分钱包。
- 企业发单页。

### 7.2 ComfyUI 占位容器

- 任务详情页内预留 `TaskWorkbench` 区域。
- ComfyUI 启动方式直接复用学生端现有启动逻辑/API。
- 当前阶段使用静态图占位，展示“面板即将接入”。
- 后续嵌入真实面板时不改业务流程与接口。

### 7.3 多赛道扩展约定

- 按 `task_type` 渲染不同工作区组件（`comfyui/agent_cs/short_video`）。
- 统一配置接口 `getWorkbenchConfig(task_id)`。
- 统一交付接口 `submitDeliverable(task_id, payload)`，按赛道校验 `payload schema`。

## 8. 非功能要求

- 幂等: 抢单接口支持幂等，防重试/并发重复扣减。
- 原子性: 名额扣减必须后端事务或原子语义保证。
- 可追溯: 资格快照、信誉分流水全量留痕。
- 可配置: 阈值、权重、分值规则可后台配置（后续迭代）。

## 9. 分阶段实施建议

- Phase 1: 任务墙、详情、抢单、企业资质、信誉分、ComfyUI占位容器。
- Phase 2: 作品集、钱包流水、提现申请、运营审核后台联动。
- Phase 3: 多赛道接入（客服智能体、短视频）与高级风控。

## 10. 已确认决策汇总

- 采用独立第三客户端。
- 执行方复用教学系统账号并支持免登录进入任务大厅。
- 教师账号与学生账号在任务大厅同权。
- 企业可注册登录并发布需求，发布前需完成资质审核。
- 企业信誉分机制采用简单阈值制: 初始 80，低于 60 审核，回到 60 立刻恢复自动上架。
- 抢单资格包含前置课程完成与进行中任务限制。
- 能力分三者加权采用 40/40/20。
- ComfyUI 启动复用学生端既有方式。
