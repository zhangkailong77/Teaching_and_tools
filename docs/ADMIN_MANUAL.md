# 管理员操作手册

> 本文档记录系统部署后的管理员手动操作命令。

---

## 1. 添加教师账号（推荐）

系统部署后，使用整合脚本一次性完成账号创建 + 课程授权：

### 方式一：交互模式（手动输入）

```bash
docker exec -it teaching-backend python /app/create_teacher.py
```

按提示输入：
```
👉 账号(手机号): 138xxxxxxx
👉 密码: xxxxxx
👉 姓名: 张老师
👉 课程ID (可选，多个用逗号分隔): 1,2,3
```

### 方式二：Excel 批量导入

1. 下载模板：
```bash
docker exec -it teaching-backend python /app/create_teacher.py --template
```

2. 编辑模板文件 `teachers_template.xlsx`

3. 批量导入：
```bash
docker cp teachers_template.xlsx teaching-backend:/app/teachers_template.xlsx
docker exec -it teaching-backend python /app/create_teacher.py --file /app/teachers_template.xlsx
```

**Excel 模板格式：**
| username | password | full_name | course_ids |
|----------|----------|-----------|------------|
| 13800138000 | 123456 | 张老师 | 1,2,3 |
| 13800138001 | 123456 | 李老师 | 1,4 |

**参数说明：**
- `teaching-backend` 是后端容器名称
- `course_ids` 可留空（仅创建账号不授权）

---

## 2. 添加学生账号

```bash
docker exec -it teaching-backend python /app/create_user.py
```

按提示输入：
```
请输入登录账号(手机号): 139xxxxxxx
请输入密码: xxxxxx
请输入角色 (student/teacher) [默认student]: student
请输入真实姓名 (可选): 李同学
请输入学号 (可选): 2026001
```

---

## 3. 重新导入课程资源

当需要更新课程章节和 PDF 文件时：

```bash
# 先进入容器
docker exec -it teaching-backend bash

# 进入 backend 目录
cd /app

# 运行导入脚本（需确保源路径存在）
python import_course.py

# 服务器上的文件路径改为   /course-data/AI+(跨境)电商视觉营销设计
```

**注意：** 导入前请先修改 `import_course.py` 中的 `SOURCE_DIR` 为本地源路径。

---

## 4. 进入 MySQL 数据库

```bash
# 方法一：使用 docker exec 直接操作
docker exec -it teaching-mysql mysql -uroot -pteaching2024 teaching_platform

# 方法二：本地使用 MySQL 客户端连接
mysql -h <服务器IP> -uroot -pteaching2024 teaching_platform
```

---

## 5. 查看容器日志

```bash
# 查看后端日志
docker logs -f teaching-backend

# 查看前端日志
docker logs -f teaching-frontend

# 查看最近 100 行日志
docker logs --tail 100 teaching-backend
```

---

## 6. 重启服务

```bash
# 重启后端
docker restart teaching-backend

# 重启前端
docker restart teaching-frontend

# 重启全部服务
docker-compose restart
```

---

## 7. 查看容器状态

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a
```

---

## 8. 进入容器内部

```bash
# 进入后端容器
docker exec -it teaching-backend bash

# 进入 MySQL 容器
docker exec -it teaching-mysql bash
```

输入 `exit` 可退出容器。

---

## 常用容器名称

| 服务 | 容器名称 |
|------|---------|
| 前端 | `teaching-frontend` |
| 后端 | `teaching-backend` |
| MySQL | `teaching-mysql` |
| Redis | `teaching-redis` |

---

> 最后更新：2026-01-30
