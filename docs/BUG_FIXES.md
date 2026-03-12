# Bug 修复记录

## 2026-01-30

### 问题1：import_course.py 更新后缓存不失效

**问题描述：**
运行 `import_course.py` 更新课程章节和 PDF 文件后，系统没有立即读取到新数据，而是继续使用缓存中的旧索引，导致无法打开对应的 PDF 文件。

**原因分析：**
- `content.py` 中的 `read_course_chapters` 接口使用了 Redis 缓存，缓存时间 30 分钟
- `import_course.py` 在更新数据库后没有清除对应的缓存
- 导致返回旧缓存数据（file_url 是旧的）

**解决方案：**
1. 在 `import_course.py` 添加缓存清除逻辑：
   ```python
   from app.core.redis import delete_cache_pattern
   delete_cache_pattern(f"course:{course.id}:chapters")
   ```
2. 将缓存时间从 30 分钟缩短到 5 分钟（减少数据不一致窗口期）

**涉及文件：**
- `backend/import_course.py`
- `backend/app/api/v1/endpoints/content.py`

---

### 问题2：课程资源包显示全部而非已授权

**问题描述：**
教师新建班级时，绑定课程资源包的列表显示了全部 8 个资源包，而不是显示该账号已授权的课程资源包列表。

**原因分析：**
- `GET /courses/me` 接口返回了所有课程 (`db.query(Course).all()`)
- 虽然计算了 `is_locked` 标记，但没有过滤未授权的课程
- 前端直接展示返回的全部数据

**解决方案：**
修改查询逻辑，只返回当前教师已授权的课程：
```python
courses = db.query(Course).join(TeacherCourseAccess).filter(
    TeacherCourseAccess.teacher_id == current_user.id
).all()
```

**涉及文件：**
- `backend/app/api/v1/endpoints/content.py`

---

---

### 问题3：教师账号创建和课程授权分开操作

**问题描述：**
创建教师账号需要执行 `create_user.py`，课程授权需要再执行 `teacher_course_access.py`，操作繁琐且容易遗漏授权步骤。

**解决方案：**
创建整合脚本 `create_teacher.py`，支持一键完成：
- 教师账号创建
- 课程资源自动授权

**使用方式：**
```bash
# 交互模式（手动输入）
python create_teacher.py

# Excel 批量导入
python create_teacher.py --file teachers.xlsx
```

**涉及文件：**
- `backend/create_teacher.py` (新增)

---

### 问题4：PDF断点续读位置不准确

**问题描述：**
学生点击"继续学习"后，滚动位置恢复不准确。例如退出时记录77%，恢复时却显示81%。

**原因分析：**
- PDF组件使用懒加载，初始渲染时 `scrollHeight` 只有约2000px
- 随着滚动，懒加载触发更多页面渲染，`scrollHeight` 增长到12000+px
- 之前的实现在PDF首次加载后就立即滚动，此时 `scrollHeight` 尚未稳定
- 导致计算出的滚动位置偏小

**解决方案：**
采用监控滚动高度稳定的策略：
1. 不再立即滚动，等待PDF完全懒加载
2. 使用 `setInterval` 每200ms检测 `scrollHeight` 是否稳定
3. 连续3次检测值相同（600ms），认为渲染完成
4. 此时再根据最终 `scrollContentHeight` 计算正确的滚动位置

**关键代码：**
```typescript
// 每隔200ms检查scrollHeight是否稳定
let stableCount = 0;
const CHECK_INTERVAL = 200;
const STABLE_THRESHOLD = 3;

const checkAndRestore = () => {
  const currentScrollHeight = container.scrollHeight;

  if (currentScrollHeight === lastScrollHeight) {
    stableCount++;
    if (stableCount >= STABLE_THRESHOLD && scrollContentHeight > 0) {
      // 此时 scrollHeight 已稳定，可以正确计算滚动位置
      const targetScrollTop = Math.round((targetPercent / 100) * scrollContentHeight);
      container.scrollTop = targetScrollTop;
    }
  } else {
    stableCount = 0;
    lastScrollHeight = currentScrollHeight;
  }
};
```

**涉及文件：**
- `frontend/src/views/dashboard/student/course-detail.vue`

---

> 记录日期：2026-01-30
