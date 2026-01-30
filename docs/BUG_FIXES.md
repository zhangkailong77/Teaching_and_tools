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

> 记录日期：2026-01-30
