# Redis通用缓存功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标：** 为系统添加通用Redis缓存功能，提升API响应速度和减少数据库压力

**架构：** 装饰器模式缓存 + 手动缓存操作，写操作时主动失效缓存

**技术栈：** Redis (Python), FastAPI, Vue 3, 已有的Redis工具类

---

## 前置条件

✅ Redis服务已安装并运行（Docker）
✅ Redis工具类已创建 (`backend/app/core/redis.py`)
✅ Redis配置已完成 (`backend/app/core/config.py`)

---

## 阶段一：用户认证缓存

### Task 1: 添加用户认证缓存

**文件：**
- Modify: `backend/app/api/deps.py`

**Step 1: 读取当前deps.py**

```bash
cat backend/app/api/deps.py
```

Expected: 查看当前的get_current_user函数实现

**Step 2: 添加Redis缓存导入**

在文件顶部添加：
```python
from app.core.redis import get_cache, set_cache
```

**Step 3: 修改get_current_user函数添加缓存逻辑**

找到 `get_current_user` 函数，在JWT解码后、数据库查询前添加：
```python
# 先尝试从缓存获取
cache_key = f"user:{username}"
cached_user = get_cache(cache_key)
if cached_user:
    # 将dict转换为User对象
    from app.models.user import User
    return User(**cached_user) if isinstance(cached_user, dict) else cached_user
```

在数据库查询成功后，添加缓存写入：
```python
# 存入缓存（1小时过期）
user_dict = {
    "id": user.id,
    "username": user.username,
    "full_name": user.full_name,
    "role": user.role,
    "is_active": user.is_active,
    "student_number": user.student_number,
    "student_profile": {
        "avatar": user.student_profile.avatar if user.student_profile else None
    } if user.student_profile else None
}
set_cache(cache_key, user_dict, expire=3600)
```

**Step 4: 测试缓存**

```bash
# 重启后端
cd backend
# 重启后服务

# 触发API请求，然后在Redis中查看
docker exec <redis-container> redis-cli keys "user:*"
```

Expected: 能看到 `user:xxx` 格式的key

**Step 5: Commit**

```bash
git add backend/app/api/deps.py
git commit -m "feat: add user authentication cache"
```

---

## 阶段二：班级列表缓存

### Task 2: 添加教师班级列表缓存

**文件：**
- Modify: `backend/app/api/v1/endpoints/course.py`

**Step 1: 添加Redis导入**

在文件顶部添加：
```python
from app.core.redis import get_cache, set_cache, delete_cache_pattern
```

**Step 2: 找到班级列表接口**

```bash
grep -n "def read_my_classes" backend/app/api/v1/endpoints/course.py
```

Expected: 找到函数定义的行号

**Step 3: 修改函数添加缓存逻辑**

在函数开头添加缓存读取：
```python
@router.get("/my")
def read_my_classes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 尝试从缓存获取
    cache_key = f"teacher:{current_user.id}:classes"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # 原有查询逻辑...
```

在return语句前添加缓存写入：
```python
    # 存入缓存（30分钟）
    set_cache(cache_key, result, expire=1800)

    return result
```

**Step 4: 在创建班级时清除缓存**

找到创建班级的接口（可能在同一文件中），在创建成功后添加：
```python
delete_cache_pattern(f"teacher:{current_user.id}:*")
```

**Step 5: 测试缓存**

```bash
# 访问班级列表API
# 然后查看Redis
docker exec <redis-container> redis-cli keys "teacher:*:classes"
```

**Step 6: Commit**

```bash
git add backend/app/api/v1/endpoints/course.py
git commit -m "feat: add class list cache"
```

---

## 阶段三：作业统计数据缓存

### Task 3: 添加作业统计缓存

**文件：**
- Modify: `backend/app/api/v1/endpoints/homework.py`

**Step 1: 添加Redis导入**

```python
from app.core.redis import get_cache, set_cache, delete_cache_pattern
```

**Step 2: 找到作业统计接口**

```bash
grep -n "stats\|统计" backend/app/api/v1/endpoints/homework.py
```

**Step 3: 添加缓存逻辑**

找到统计相关的接口，添加：
```python
# 缓存key
cache_key = f"teacher:{current_user.id}:homework_stats"

# 尝试从缓存获取
cached = get_cache(cache_key)
if cached:
    return cached

# ... 原有统计逻辑 ...

# 存入缓存（10分钟）
set_cache(cache_key, result, expire=600)
```

**Step 4: 在作业变更时清除缓存**

在作业相关写操作（创建、更新、删除、批改）后添加：
```python
delete_cache_pattern(f"teacher:{current_user.id}:*")
```

**Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/homework.py
git commit -m "feat: add homework stats cache"
```

---

## 阶段四：题库筛选缓存

### Task 4: 添加题库筛选缓存

**文件：**
- Modify: `backend/app/api/v1/endpoints/exam.py`

**Step 1: 修改get_questions接口**

找到 `read_questions` 函数（获取题目列表），添加：
```python
@router.get("/questions", response_model=QuestionPagination)
def read_questions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    type: Optional[str] = None,
    difficulty: Optional[int] = None,
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    # 生成缓存键（包含筛选条件）
    cache_key = f"teacher:{current_user.id}:questions:{type or 'all'}:{difficulty or 'all'}:{keyword or ''}:{tag or ''}:{skip}:{limit}"

    # 尝试从缓存获取
    cached = get_cache(cache_key)
    if cached:
        return cached

    # 原有查询逻辑...
```

在return前添加缓存写入：
```python
# 存入缓存（30分钟）
set_cache(cache_key, {"total": total, "items": questions}, expire=1800)
```

**Step 2: 在题目变更时清除缓存**

在题目相关写操作后添加：
```python
delete_cache_pattern(f"teacher:{current_user.id}:questions:*")
```

**Step 3: Commit**

```bash
git add backend/app/api/v1/endpoints/exam.py
git commit -m "feat: add question filter cache"
```

---

## 阶段五：测试验证

### Task 5: 缓存功能测试

**文件：** 无

**Step 1: 启动Redis监控**

```bash
docker exec <redis-container> redis-cli monitor
```

**Step 2: 测试用户认证缓存**

1. 登录系统
2. 查看Redis：
```bash
docker exec <redis-container> redis-cli keys "user:*"
docker exec <redis-container> redis-cli get "user:你的用户名"
```

Expected: 能看到缓存的用户数据

**Step 3: 测试班级列表缓存**

1. 访问班级列表
2. 第一次会查数据库
3. 第二次应该从缓存返回（速度快）

**Step 4: 测试缓存失效**

1. 创建一个新班级
2. 再次访问班级列表
3. 确认是新数据（旧缓存已清除）

**Step 5: 清空测试数据**

```bash
docker exec <redis-container> redis-cli FLUSHDB
```

---

## 任务完成检查清单

- [ ] 用户认证缓存已添加并测试
- [ ] 班级列表缓存已添加并测试
- [ ] 作业统计缓存已添加并测试
- [ ] 题库筛选缓存已添加并测试
- [ ] 缓存失效逻辑正常工作
- [ ] Redis故障不影响主流程

---

## 附录：缓存键命名规范

```python
# 用户相关
"user:{username}"                    # 用户基本信息

# 教师相关
"teacher:{teacher_id}:classes"      # 班级列表
"teacher:{teacher_id}:homework_stats"  # 作业统计
"teacher:{teacher_id}:questions:{filters}"  # 题库筛选

# 通用模式
"{模块}:{资源ID}:{可选参数}"
```

## 附录：缓存过期时间参考

| 数据类型 | 过期时间 | 说明 |
|---------|---------|------|
| 用户认证 | 3600秒 (1小时) | 变化频率低 |
| 班级列表 | 1800秒 (30分钟) | 创建班级时清除 |
| 作业统计 | 600秒 (10分钟) | 频繁更新 |
| 题库筛选 | 1800秒 (30分钟) | 题目变更时清除 |
