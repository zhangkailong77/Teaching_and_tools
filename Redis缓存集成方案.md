# Redis缓存集成方案

## 一、缓存场景清单

### 优先级1 - 强烈建议（高收益）

| 场景 | 当前方式 | 缓存策略 | 缓存时长 |
|-----|---------|---------|---------|
| **用户认证信息** | 每次请求查MySQL | 缓存用户基本信息 | 1小时 |
| **班级列表+学生数** | 每次多表JOIN查询 | 缓存完整列表 | 30分钟 |
| **作业统计数据** | 实时聚合计算 | 缓存计算结果 | 10分钟 |
| **题库筛选结果** | 每次筛选查数据库 | 缓存筛选条件+结果 | 30分钟 |

### 优先级2 - 考试暂存（特殊用法）

| 场景 | 当前方式 | Redis策略 | 说明 |
|-----|---------|---------|------|
| **考试答题暂存** | 未启用（原计划每30秒写MySQL） | **写入缓冲层** | 答案变化即保存到Redis，提交时才写MySQL |

**这不是传统缓存，是断电保护：**
```
答题变化 → 立即存Redis（防抖3秒）
提交试卷 → Redis数据刷入MySQL
掉线刷新 → 重新进入从Redis恢复答案
```

### 优先级3 - 建议缓存（中等收益）

| 场景 | 缓存时长 |
|-----|---------|
| 课程章节内容 | 1小时 |
| 公告列表 | 10分钟 |
| 试卷题目内容（学生答题时） | 考试期间 |

### 不需要缓存

- 作业提交、考试最终提交 → 写操作
- 单条记录简单查询（`WHERE id = ?`）→ 直接查MySQL更快
- 学生名单实时更新 → 频繁变化

---

## 二、考试暂存功能设计（变化即保存）

### 2.1 设计思路

**问题：** 原计划每30秒全量保存，存在大量无意义重复写入

**方案：** 答案变化时立即保存（防抖3秒）

| 方案 | 写入次数 | 数据一致性 | 复杂度 |
|-----|---------|-----------|-------|
| 全量30秒 | 多（很多重复） | 好 | 低 |
| **变化即保存** | 少（只写变化的） | 最好 | 中 |

### 2.2 数据流程

```
┌─────────────┐     答案变化      ┌─────────────┐
│   前端页面   │ ───────────────→ │   防抖3秒    │
│  (take.vue) │                  │   延迟触发   │
└─────────────┘                  └─────────────┘
                                           │
                                           ▼
┌─────────────┐     API调用      ┌─────────────┐
│   保存提示   │ ←────────────────│  调用后端API │
│  "保存中..." │                  │ /save-progress│
└─────────────┘                  └─────────────┘
                                           │
                                           ▼
┌─────────────┐     写入Redis     ┌─────────────┐
│   提交试卷   │ ←────────────────│  Redis暂存   │
│  刷入MySQL  │                  │ key:进度数据 │
└─────────────┘                  └─────────────┘
                                           │
                                           ▼
┌─────────────┐     恢复答案      ┌─────────────┐
│  掉线重连   │ ←────────────────│  重新进入考试 │
│  加载暂存   │                  │  从Redis读取 │
└─────────────┘                  └─────────────┘
```

---

## 三、需要修改/新增的文件

### 新增文件

```
backend/
└── app/
    └── core/
        └── redis.py          # Redis连接和缓存工具函数
```

### 修改文件

```
backend/
├── requirements.txt           # 添加Redis依赖
├── .env                       # 添加Redis配置
├── app/
│   ├── core/
│   │   └── config.py         # 添加Redis配置项
│   ├── api/
│   │   └── deps.py           # 用户认证添加缓存
│   └── api/v1/endpoints/
│       ├── course.py         # 班级列表缓存
│       ├── homework.py       # 作业待办缓存
│       └── exam.py           # 考试暂存改为Redis

frontend/
├── package.json               # 添加lodash-es（防抖函数）
├── src/
│   ├── api/
│   │   └── exam.ts           # 确保有saveExamProgress接口
│   └── views/dashboard/student/exams/
│       └── take.vue          # 改为变化即保存
```

---

## 四、具体实现代码

### 4.1 安装Redis服务

```bash
# Windows下载Redis
# 下载地址：https://github.com/microsoftarchive/redis/releases

# 或使用Docker
docker run -d -p 6379:6379 redis

# 验证安装
redis-cli ping  # 应返回 PONG
```

### 4.2 添加Python依赖

**`backend/requirements.txt` 添加：**
```
redis==5.0.1
```

### 4.3 配置Redis连接

**修改 `backend/app/core/config.py`：**
```python
from pydantic import Field

class Settings(BaseSettings):
    # ... 现有配置 ...

    # Redis配置
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
```

**修改 `backend/.env`：**
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=your_password  # 如果有密码
```

### 4.4 创建Redis工具类

**新建 `backend/app/core/redis.py`：**
```python
import redis
import json
import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=redis_pool)


def get_cache(key: str) -> Optional[Any]:
    """获取缓存"""
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Redis读取失败: {e}")
    return None


def set_cache(key: str, value: Any, expire: int = 300) -> bool:
    """设置缓存"""
    try:
        redis_client.setex(key, expire, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.warning(f"Redis写入失败: {e}")
        return False


def delete_cache(key: str) -> bool:
    """删除缓存"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis删除失败: {e}")
        return False


def delete_cache_pattern(pattern: str) -> int:
    """删除匹配模式的所有缓存，返回删除数量"""
    try:
        count = 0
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
            count += 1
        return count
    except Exception as e:
        logger.warning(f"Redis批量删除失败: {e}")
        return 0


# ==================== 考试暂存专用函数 ====================

def EXAM_PROGRESS_KEY(exam_id: int, student_id: int) -> str:
    """生成考试暂存的Redis key"""
    return f"exam_progress:{exam_id}:{student_id}"


def save_exam_progress(exam_id: int, student_id: int, question_id: int, answer: Any) -> bool:
    """
    保存单题答案到Redis（哈希结构）
    返回: 是否保存成功
    """
    key = EXAM_PROGRESS_KEY(exam_id, student_id)
    field = f"q_{question_id}"
    try:
        redis_client.hset(key, field, json.dumps(answer))
        # 设置过期时间：考试结束后24小时
        redis_client.expire(key, 86400)
        return True
    except Exception as e:
        logger.warning(f"保存考试进度失败: {e}")
        return False


def get_exam_progress(exam_id: int, student_id: int) -> dict:
    """
    获取考试暂存的所有答案
    返回: {question_id: answer} 格式的字典
    """
    key = EXAM_PROGRESS_KEY(exam_id, student_id)
    try:
        data = redis_client.hgetall(key)
        result = {}
        for field, value in data.items():
            # field格式: q_123 -> 提取数字
            qid = int(field.replace("q_", ""))
            result[qid] = json.loads(value)
        return result
    except Exception as e:
        logger.warning(f"获取考试进度失败: {e}")
        return {}


def clear_exam_progress(exam_id: int, student_id: int) -> bool:
    """清除考试暂存数据（提交试卷后调用）"""
    key = EXAM_PROGRESS_KEY(exam_id, student_id)
    return delete_cache(key)
```

### 4.5 修改考试暂存接口

**修改 `backend/app/api/v1/endpoints/exam.py`：**

在文件顶部添加导入：
```python
from app.core.redis import save_exam_progress, get_exam_progress, clear_exam_progress
```

修改暂存接口（第970-1007行）：
```python
# [学生端] 暂存单题答案 (变化即保存)
@router.post("/student/save-progress/{exam_id}")
def save_exam_progress_endpoint(
    exam_id: int,
    answers: List[schemas.AnswerSubmit],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    保存单题或多题答案到Redis（断电保护）
    注意：这里不再写MySQL，只在提交时才写入
    """
    # 验证考试记录存在
    record = db.query(models.ExamRecord).filter(
        models.ExamRecord.exam_id == exam_id,
        models.ExamRecord.student_id == current_user.id,
        models.ExamRecord.status == 0  # 进行中
    ).first()

    if not record:
        return {"msg": "无正在进行的考试记录"}

    # 保存到Redis
    saved_count = 0
    for ans in answers:
        if save_exam_progress(exam_id, current_user.id, ans.question_id, ans.answer_content):
            saved_count += 1

    return {"status": "success", "saved_count": saved_count}
```

添加恢复进度接口（新增）：
```python
# [学生端] 获取暂存的答案（重新进入考试时调用）
@router.get("/student/progress/{exam_id}")
def get_exam_progress_endpoint(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """获取Redis中暂存的答案，用于断线重连恢复"""
    # 验证考试记录存在
    record = db.query(models.ExamRecord).filter(
        models.ExamRecord.exam_id == exam_id,
        models.ExamRecord.student_id == current_user.id,
        models.ExamRecord.status == 0
    ).first()

    if not record:
        return {"answers": {}}

    # 从Redis获取暂存数据
    progress = get_exam_progress(exam_id, current_user.id)
    return {"answers": progress}
```

修改提交接口（第872行开始），在提交前从Redis读取答案：
```python
@router.post("/student/submit/{exam_id}")
def submit_exam(
    exam_id: int,
    submit_in: schemas.ExamSubmit,  # 注意：前端可能传空，从Redis读取
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 找到考试记录
    record = db.query(models.ExamRecord).filter(
        models.ExamRecord.exam_id == exam_id,
        models.ExamRecord.student_id == current_user.id,
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="未找到进行中的考试记录")

    # 2. 从Redis获取暂存的答案（如果前端传的为空）
    final_answers = submit_in.answers
    if not final_answers or len(final_answers) == 0:
        redis_progress = get_exam_progress(exam_id, current_user.id)
        final_answers = [
            schemas.AnswerSubmit(question_id=qid, answer_content=ans)
            for qid, ans in redis_progress.items()
        ]

    objective_score = 0

    # 3. 遍历答案并判分（原有逻辑）
    for ans in final_answers:
        # ... 原有判分逻辑 ...

    # 4. 更新记录状态（原有逻辑）
    # ...

    # 5. 清除Redis暂存数据
    clear_exam_progress(exam_id, current_user.id)

    return {"message": "交卷成功", "score": objective_score, "status": record.status}
```

### 4.6 前端实现

**安装依赖（如果没有）：**
```bash
cd frontend
npm install lodash-es
```

**修改 `frontend/src/views/dashboard/student/exams/take.vue`：**

```vue
<script setup lang="ts">
import { debounce } from 'lodash-es';
// ... 其他导入

// 状态变量
const isSaving = ref(false);
const saveTimeout = ref<any>(null);

// 保存单题答案（防抖3秒）
const saveSingleAnswer = debounce(async (questionId: number, answer: any) => {
  isSaving.value = true;
  try {
    await saveExamProgress(examId, [{
      question_id: questionId,
      answer_content: answer
    }]);
  } catch (e) {
    console.error('保存失败:', e);
  } finally {
    setTimeout(() => isSaving.value = false, 1000);
  }
}, 3000);

// 监听answers变化
watch(
  () => answers,
  (newVal, oldVal) => {
    if (!oldVal) return;  // 初始化跳过

    // 遍历所有题目，找出发生变化的
    for (const qid in newVal) {
      if (JSON.stringify(newVal[qid]) !== JSON.stringify(oldVal[qid])) {
        saveSingleAnswer(Number(qid), newVal[qid]);
      }
    }
  },
  { deep: true }
);

// 重新进入考试时，加载暂存的答案
const loadSavedProgress = async () => {
  try {
    const res = await getExamProgress(examId);
    if (res.answers) {
      // 恢复已保存的答案
      for (const [qid, answer] of Object.entries(res.answers)) {
        answers[Number(qid)] = answer;
      }
    }
  } catch (e) {
    console.error('加载暂存失败:', e);
  }
};

// 修改进入考试逻辑
const enterExam = async () => {
  // ... 原有逻辑 ...

  // 加载暂存的答案
  await loadSavedProgress();

  isStarted.value = true;
  startTimer();
  setupAntiCheat();
  // 移除 startAutoSave() 调用
};

// 提交时可以传空数组，后端会从Redis读取
const autoSubmit = async () => {
  clearInterval(timerInterval);

  try {
    // 传空数组，让后端从Redis读取
    await submitExam(examId, { answers: [], cheat_count: cheatCount.value });

    // ... 原有逻辑 ...
  } catch (e) {
    console.error("提交出错：", e);
  }
};

// 清理
onUnmounted(() => {
  clearInterval(timerInterval);
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  window.removeEventListener('blur', handleBlur);
});
</script>

<template>
  <!-- 修改保存状态显示 -->
  <span class="save-status" :class="{ 'saving': isSaving }">
    {{ isSaving ? '💾 保存中...' : '✅ 答案已自动保存' }}
  </span>
</template>
```

**确保API接口存在（`frontend/src/api/exam.ts`）：**
```typescript
// 保存考试进度
export function saveExamProgress(examId: number, answers: Array<{question_id: number, answer_content: any}>) {
  return request({
    url: `/exam/student/save-progress/${examId}`,
    method: 'post',
    data: answers
  });
}

// 获取暂存的进度
export function getExamProgress(examId: number) {
  return request({
    url: `/exam/student/progress/${examId}`,
    method: 'get'
  });
}
```

---

## 五、其他缓存场景示例

### 5.1 用户认证缓存

**修改 `backend/app/api/deps.py`：**
```python
from app.core.redis import get_cache, set_cache

async def get_current_user(
    db: Session = Depends(deps.get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=403, detail="凭证无效")

    # 先尝试从缓存获取
    cache_key = f"user:{username}"
    cached_user = get_cache(cache_key)
    if cached_user:
        return cached_user

    # 缓存未命中，查数据库
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 存入缓存（1小时过期）
    set_cache(cache_key, user, expire=3600)

    return user
```

### 5.2 班级列表缓存

**修改 `backend/app/api/v1/endpoints/course.py`：**
```python
from app.core.redis import get_cache, set_cache, delete_cache_pattern

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

    # 缓存未命中，查询数据库
    # ... 原有查询逻辑 ...

    # 存入缓存（30分钟）
    result = [...]  # 查询结果
    set_cache(cache_key, result, expire=1800)

    return result

# 创建班级时清除缓存
@router.post("/classes")
def create_class(...):
    # ... 创建逻辑 ...
    delete_cache_pattern(f"teacher:{current_user.id}:*")
    return new_class
```

---

## 六、测试验证

### 6.1 测试Redis连接

```bash
# 确保Redis服务运行
redis-cli ping  # 应返回 PONG

# 查看所有key
redis-cli keys "*"

# 查看考试暂存数据
redis-cli hgetall "exam_progress:1:123"
```

### 6.2 测试考试暂存

1. 学生进入考试，作答几道题
2. 等待3秒后检查Redis：
   ```bash
   redis-cli hgetall "exam_progress:{exam_id}:{student_id}"
   ```
3. 刷新页面，重新进入考试，答案是否恢复
4. 提交试卷，检查Redis数据是否清除

### 6.3 监控Redis操作

```bash
# 实时查看所有Redis操作
redis-cli monitor
```

---

## 七、注意事项

1. **Redis故障处理**：Redis操作都加了try-catch，Redis挂了不影响主流程
2. **缓存过期时间**：考试暂存数据设为24小时，考试结束后自动清理
3. **缓存一致性**：写操作后记得清除相关缓存
4. **数据序列化**：使用`json.dumps`的`default=str`处理复杂对象
5. **防抖时间**：3秒是比较合理的值，太短会频繁写入，太长体验差

---

## 八、渐进式实施建议

**阶段1：考试暂存功能（优先）**
- 安装Redis和Python依赖
- 创建Redis工具类
- 修改考试暂存接口
- 前端改为变化即保存

**阶段2：用户认证缓存**
- 修改deps.py添加用户缓存
- 测试验证

**阶段3：其他场景缓存**
- 班级列表缓存
- 统计数据缓存
- 其他高价值场景
