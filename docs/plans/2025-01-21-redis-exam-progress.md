# Redis考试暂存功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标：** 实现考试答题的断电保护功能，答案变化时自动保存到Redis，提交时才写入MySQL

**架构：** 前端监听答案变化（防抖3秒）→ 调用后端API → 后端写入Redis哈希结构 → 提交试卷时从Redis读取并写入MySQL

**技术栈：** Redis (Python库), FastAPI, Vue 3, lodash-es (防抖)

---

## 前置准备

### Task 0: 安装Redis服务

**Files:** 无（系统级操作）

**Step 1: 验证Redis是否已安装**

```bash
redis-cli ping
```

Expected: `PONG`

**Step 2: 如未安装，下载并启动Redis**

Windows下载：https://github.com/microsoftarchive/redis/releases
或使用Docker：
```bash
docker run -d -p 6379:6379 redis
```

**Step 3: 验证Redis运行状态**

```bash
redis-cli ping
```

Expected: `PONG`

---

## 阶段一：后端基础设施

### Task 1: 添加Redis依赖

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: 编辑requirements.txt**

在文件末尾添加：
```
redis==5.0.1
```

**Step 2: 安装依赖**

```bash
cd backend
pip install redis==5.0.1
```

Expected: 安装成功，无报错

**Step 3: 验证安装**

```bash
python -c "import redis; print(redis.__version__)"
```

Expected: 输出版本号如 `5.0.1`

**Step 4: Commit**

```bash
cd backend
git add requirements.txt
git commit -m "feat: add redis dependency"
```

---

### Task 2: 添加Redis配置

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/.env`

**Step 1: 修改config.py添加Redis配置字段**

在`Settings`类中添加（找到现有配置字段的位置）：

```python
# Redis配置
redis_host: str = Field(default="localhost", env="REDIS_HOST")
redis_port: int = Field(default=6379, env="REDIS_PORT")
redis_db: int = Field(default=0, env="REDIS_DB")
redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
```

**Step 2: 修改.env文件添加Redis配置**

在`backend/.env`文件末尾添加：
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

**Step 3: 验证配置加载**

```bash
cd backend
python -c "from app.core.config import settings; print(f'Redis: {settings.redis_host}:{settings.redis_port}')"
```

Expected: `Redis: localhost:6379`

**Step 4: Commit**

```bash
git add backend/app/core/config.py backend/.env
git commit -m "feat: add redis configuration"
```

---

### Task 3: 创建Redis工具类

**Files:**
- Create: `backend/app/core/redis.py`

**Step 1: 创建Redis工具类文件**

创建 `backend/app/core/redis.py`，完整内容如下：

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
    """删除匹配模式的所有缓存"""
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
            qid = int(field.replace("q_", ""))
            result[qid] = json.loads(value)
        return result
    except Exception as e:
        logger.warning(f"获取考试进度失败: {e}")
        return {}


def clear_exam_progress(exam_id: int, student_id: int) -> bool:
    """清除考试暂存数据"""
    key = EXAM_PROGRESS_KEY(exam_id, student_id)
    return delete_cache(key)
```

**Step 2: 测试Redis连接**

```bash
cd backend
python -c "from app.core.redis import redis_client; print(redis_client.ping())"
```

Expected: `True`

**Step 3: 测试基本读写**

```bash
cd backend
python -c "
from app.core.redis import set_cache, get_cache
set_cache('test_key', {'value': 'hello'}, 10)
print(get_cache('test_key'))
"
```

Expected: `{'value': 'hello'}`

**Step 4: Commit**

```bash
git add backend/app/core/redis.py
git commit -m "feat: add redis utility module"
```

---

## 阶段二：后端API修改

### Task 4: 修改考试暂存接口（使用Redis）

**Files:**
- Modify: `backend/app/api/v1/endpoints/exam.py`

**Step 1: 添加Redis导入**

在文件顶部找到导入区域，添加：
```python
from app.core.redis import save_exam_progress, get_exam_progress, clear_exam_progress
```

**Step 2: 修改暂存接口（约第970-1007行）**

找到 `save_exam_progress` 函数，替换为：

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
    不再写MySQL，只在提交时才写入
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

**Step 3: 添加恢复进度接口（新接口）**

在 `save_exam_progress_endpoint` 函数后添加：

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

**Step 4: 修改提交接口（约第872行开始）**

找到 `submit_exam` 函数，修改提交前从Redis读取答案的逻辑：

在函数开头，找到 `final_answers = submit_in.answers` 后，添加：

```python
    # 从Redis获取暂存的答案（如果前端传的为空）
    final_answers = submit_in.answers
    if not final_answers or len(final_answers) == 0:
        redis_progress = get_exam_progress(exam_id, current_user.id)
        final_answers = [
            schemas.AnswerSubmit(question_id=qid, answer_content=ans)
            for qid, ans in redis_progress.items()
        ]
```

在函数末尾，`return` 语句前添加清除Redis的逻辑：

```python
    # 清除Redis暂存数据
    clear_exam_progress(exam_id, current_user.id)
```

**Step 5: 启动后端验证无语法错误**

```bash
cd backend
python -c "from app.api.v1.endpoints.exam import router; print('Import success')"
```

Expected: `Import success`

**Step 6: Commit**

```bash
git add backend/app/api/v1/endpoints/exam.py
git commit -m "feat: modify exam progress to use Redis"
```

---

## 阶段三：前端实现

### Task 5: 添加前端依赖

**Files:**
- Modify: `frontend/package.json`

**Step 1: 检查lodash-es是否已安装**

```bash
cd frontend
npm list lodash-es
```

**Step 2: 如未安装，添加依赖**

```bash
cd frontend
npm install lodash-es
```

Expected: 安装成功

**Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "feat: add lodash-es for debounce"
```

---

### Task 6: 添加前端API接口

**Files:**
- Modify: `frontend/src/api/exam.ts`

**Step 1: 检查exam.ts文件是否存在**

```bash
cat frontend/src/api/exam.ts
```

**Step 2: 添加/确保API接口存在**

确保 `frontend/src/api/exam.ts` 包含以下接口：

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

**Step 3: Commit**

```bash
git add frontend/src/api/exam.ts
git commit -m "feat: add exam progress API endpoints"
```

---

### Task 7: 修改考试答题页面

**Files:**
- Modify: `frontend/src/views/dashboard/student/exams/take.vue`

**Step 1: 修改导入语句**

在 `<script setup lang="ts">` 区域，添加 debounce 导入：

```typescript
import { debounce } from 'lodash-es';
```

**Step 2: 移除定时器相关代码**

找到并删除以下变量和函数：
- 删除 `saveInterval` 变量
- 删除 `startAutoSave` 函数（约第300-309行）

**Step 3: 添加保存单题答案函数**

在 `isSaving` 变量定义后添加：

```typescript
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
```

**Step 4: 添加监听答案变化**

在 `onMounted` 之前添加：

```typescript
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
```

**Step 5: 添加加载暂存函数**

在 `onMounted` 之前添加：

```typescript
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
```

**Step 6: 修改startExam函数**

找到 `startExam` 函数，移除 `startAutoSave()` 调用：

```typescript
const startExam = () => {
    // ... 全屏逻辑 ...
    isStarted.value = true;
    startTimer();
    // startAutoSave();  // 删除这行
    setupAntiCheat();
};
```

**Step 7: 修改onMounted加载暂存**

找到 `onMounted`，在初始化答案后添加：

```typescript
onMounted(async () => {
  try {
    // ... 现有的试卷加载逻辑 ...

    // 初始化答案结构
    questions.value.forEach(q => {
      if (q.type === 'multiple') answers[q.id] = [];
      else answers[q.id] = '';
    });

    // 加载暂存的答案
    await loadSavedProgress();

    // ... 监控网络等其他逻辑 ...
  } catch (e) {
    ElMessage.error('无法加载试卷内容');
  }
});
```

**Step 8: 修改onUnmounted清理**

找到 `onUnmounted`，移除 `saveInterval` 的清理：

```typescript
onUnmounted(() => {
  clearInterval(timerInterval);
  // clearInterval(saveInterval);  // 删除这行
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  window.removeEventListener('blur', handleBlur);
});
```

**Step 9: Commit**

```bash
git add frontend/src/views/dashboard/student/exams/take.vue
git commit -m "feat: implement answer auto-save on change"
```

---

## 阶段四：测试验证

### Task 8: 后端接口测试

**Files:** 无

**Step 1: 启动后端服务**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 2: 启动Redis监控（新终端）**

```bash
redis-cli monitor
```

**Step 3: 测试保存进度接口**

```bash
curl -X POST "http://localhost:8000/api/v1/exam/student/save-progress/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"question_id": 101, "answer_content": "A"}]'
```

Expected: 返回 `{"status": "success", "saved_count": 1}`

**Step 4: 检查Redis数据**

```bash
redis-cli hgetall "exam_progress:1:STUDENT_ID"
```

Expected: `{ "q_101": "\"A\"" }`

**Step 5: 测试获取进度接口**

```bash
curl -X GET "http://localhost:8000/api/v1/exam/student/progress/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: 返回保存的答案

---

### Task 9: 前端功能测试

**Files:** 无

**Step 1: 启动前端服务**

```bash
cd frontend
npm run dev
```

**Step 2: 打开浏览器开发者工具**

进入考试页面，打开Network和Console标签

**Step 3: 答题测试**

1. 选择一道题的答案
2. 等待3秒
3. 观察Network是否有 `save-progress` 请求
4. 观察页面是否显示"保存中..."然后变为"答案已自动保存"

**Step 4: Redis验证**

```bash
redis-cli keys "exam_progress:*"
redis-cli hgetall "exam_progress:EXAM_ID:STUDENT_ID"
```

Expected: 能看到保存的答案

**Step 5: 刷新页面测试**

1. 答几道题，等待保存
2. 刷新页面
3. 重新进入考试
4. 确认答案是否恢复

**Step 6: 提交试卷测试**

1. 完成答题
2. 提交试卷
3. 检查Redis数据是否清除：

```bash
redis-cli keys "exam_progress:*"
```

Expected: 该考试的进度数据已清除

---

## 任务完成检查清单

- [ ] Redis服务已安装并运行
- [ ] Python redis依赖已添加
- [ ] Redis配置已添加到.env和config.py
- [ ] Redis工具类已创建并测试
- [ ] 考试暂存接口已修改为使用Redis
- [ ] 获取进度接口已添加
- [ ] 提交接口已修改为从Redis读取
- [ ] 前端lodash-es已安装
- [ ] 前端API接口已添加
- [ ] 前端take.vue已修改为变化即保存
- [ ] 后端接口测试通过
- [ ] 前端功能测试通过
- [ ] Redis数据持久化验证通过
- [ ] 刷新恢复功能验证通过
- [ ] 提交清除功能验证通过
