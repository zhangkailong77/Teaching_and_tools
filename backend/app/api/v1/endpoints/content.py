import json
from pathlib import Path
from typing import Any, List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.utils.hash import encode_id, decode_id

from app.api import deps
from app.core.redis import get_cache, set_cache, delete_cache_pattern
from app.models.user import User
from app.schemas import content as schemas
from app.models.course import Enrollment, Class, ClassAssignment, StudentSubmission
from app.models.content import Course, CourseChapter, CourseLesson, TeacherCourseAccess, ClassCourseBinding, StudentLearningProgress, CourseTask

router = APIRouter()

# ==================================================================
#                        预览配置常量
# ==================================================================
# 未授权教师可以预览的章节数量
PREVIEW_CHAPTER_COUNT = 1
INTERACTIVE_MANIFEST_PATH = Path("static/interactive/manifest.json")


def _load_interactive_manifest() -> dict:
    if not INTERACTIVE_MANIFEST_PATH.exists():
        return {"courses": {}}
    try:
        with INTERACTIVE_MANIFEST_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"courses": {}}


def _parse_manifest_entry(value) -> Tuple[Optional[str], Optional[str]]:
    version = None
    entry = None
    if isinstance(value, str):
        entry = value
    elif isinstance(value, dict):
        entry = value.get("entry") or value.get("entry_url") or value.get("path")
        version = value.get("version")
    if not entry:
        return None, None
    return str(entry), version


def _extract_entry_from_manifest(
    course_id: int,
    app_type: str,
    lesson_id: Optional[int] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    支持以下 manifest 结构：
    1) {"courses":{"1":{"ppt-test":{"entry":"interactive/1/ppt-test/v1/index.html","version":"v1"}}}}
    2) {"courses":{"1":{"ppt-test":{"entry_url":"/static/interactive/1/ppt-test/v1/index.html"}}}}
    3) {"courses":{"1":{"ppt-test":"/static/interactive/1/ppt-test/v1/index.html"}}}
    """
    manifest = _load_interactive_manifest()
    courses = manifest.get("courses", manifest if isinstance(manifest, dict) else {})
    course_data = courses.get(str(course_id)) if isinstance(courses, dict) else None
    if not course_data:
        return None, None

    app_data = course_data.get(app_type) if isinstance(course_data, dict) else None
    if not app_data:
        return None, None

    # 课时级严格匹配：传入 lesson_id 时，只返回该课时绑定
    if lesson_id is not None and isinstance(app_data, dict):
        lessons = app_data.get("lessons", {})
        if isinstance(lessons, dict):
            lesson_entry = lessons.get(str(lesson_id))
            entry, version = _parse_manifest_entry(lesson_entry)
            if entry:
                return entry, version
        return None, None

    # 回退课程级入口
    entry, version = _parse_manifest_entry(app_data)
    if entry:
        return entry, version

    # 课程级未配置时，再回退到 lessons 里的第一个可用入口
    if isinstance(app_data, dict):
        lessons = app_data.get("lessons", {})
        if isinstance(lessons, dict):
            for _, lesson_val in lessons.items():
                fallback_entry, fallback_version = _parse_manifest_entry(lesson_val)
                if fallback_entry:
                    return fallback_entry, fallback_version

    return None, None


def _extract_available_lesson_ids_from_app_data(app_data: Any) -> List[int]:
    if not isinstance(app_data, dict):
        return []

    lessons = app_data.get("lessons", {})
    if not isinstance(lessons, dict):
        return []

    lesson_ids: List[int] = []
    for lesson_key, lesson_val in lessons.items():
        entry, _ = _parse_manifest_entry(lesson_val)
        if not entry:
            continue
        try:
            lesson_ids.append(int(str(lesson_key)))
        except (TypeError, ValueError):
            continue

    return sorted(set(lesson_ids))


def _extract_available_lesson_ids_from_manifest(course_id: int, app_type: str) -> List[int]:
    manifest = _load_interactive_manifest()
    courses = manifest.get("courses", manifest if isinstance(manifest, dict) else {})
    course_data = courses.get(str(course_id)) if isinstance(courses, dict) else None
    if not isinstance(course_data, dict):
        return []

    app_data = course_data.get(app_type)
    return _extract_available_lesson_ids_from_app_data(app_data)


def _build_interactive_urls(request: Request, entry: str) -> Tuple[str, str]:
    """返回 (relative_url, absolute_url)。"""
    if entry.startswith("http://") or entry.startswith("https://"):
        return entry, entry

    normalized = entry.strip()
    if normalized.startswith("/static/"):
        static_path = normalized[len("/static/"):]
        relative_url = normalized
    elif normalized.startswith("static/"):
        static_path = normalized[len("static/"):]
        relative_url = f"/static/{static_path}"
    elif normalized.startswith("/"):
        # 非 /static 路径，按原样返回
        relative_url = normalized
        absolute_url = str(request.base_url).rstrip("/") + normalized
        return relative_url, absolute_url
    else:
        static_path = normalized
        relative_url = f"/static/{static_path}"

    absolute_url = str(request.url_for("static", path=static_path))
    return relative_url, absolute_url

# ------------------------------------------------------------------
# 1. 获取课程资源库（全部课程 + 锁定状态，用于资源库页面展示）
# ------------------------------------------------------------------
@router.get("/courses/me", response_model=List[schemas.CourseOut])
def read_my_courses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 获取所有课程
    all_courses = db.query(Course).all()

    # 获取当前用户的授权记录
    access_records = db.query(TeacherCourseAccess).filter(
        TeacherCourseAccess.teacher_id == current_user.id
    ).all()

    # 提取已授权的课程 ID 集合
    unlocked_course_ids = {record.course_id for record in access_records}

    results = []
    for course in all_courses:
        course_data = {
            "id": course.id,
            "name": course.name,
            "cover": course.cover,
            "intro": course.intro,
            "task_count": course.task_count,
            "total_duration": course.total_duration,
            "lesson_count": course.lesson_count,
            "course_type": course.course_type,
            "created_at": course.created_at,

            # 附加字段
            "public_id": encode_id(course.id),
            "is_locked": course.id not in unlocked_course_ids  # 添加锁定标记
        }

        results.append(course_data)

    return results

# ------------------------------------------------------------------
# 1-2. 获取可选课程列表（仅已授权，用于创建班级下拉选择）
# ------------------------------------------------------------------
@router.get("/courses/available", response_model=List[schemas.CourseOut])
def read_available_courses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """只返回当前教师已授权的课程，用于创建班级时选择"""
    courses = db.query(Course).join(TeacherCourseAccess).filter(
        TeacherCourseAccess.teacher_id == current_user.id
    ).all()

    results = []
    for course in courses:
        course_data = {
            "id": course.id,
            "name": course.name,
            "cover": course.cover,
            "intro": course.intro,
            "task_count": course.task_count,
            "total_duration": course.total_duration,
            "lesson_count": course.lesson_count,
            "course_type": course.course_type,
            "created_at": course.created_at,

            # 附加字段
            "public_id": encode_id(course.id),
        }

        results.append(course_data)

    return results

# ------------------------------------------------------------------
# 2. 创建新的课程资源包
# ------------------------------------------------------------------
@router.post("/courses/", response_model=schemas.CourseOut)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以创建课程")

    new_course = Course(
        name=course_in.name,
        cover=course_in.cover,
        intro=course_in.intro,
        owner_id=current_user.id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

# ------------------------------------------------------------------
# 3. 删除课程
# ------------------------------------------------------------------
@router.delete("/courses/{course_id}")
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: User = Depends(deps.get_current_user),
):
    # 查找课程
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
        
    # 确认归属权
    if course.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除他人课程")
        
    db.delete(course)
    db.commit()
    return {"message": "删除成功"}


# ------------------------------------------------------------------
# 4. 获取单门课程详情（支持预览模式）
# ------------------------------------------------------------------
@router.get("/courses/{public_id}", response_model=schemas.CourseOut)
def read_course_detail(
    public_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):

    # 1. ✅ 解密 ID
    course_id = decode_id(public_id)
    if not course_id:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 1. 查询课程
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 2. 查询是否已授权
    access = db.query(TeacherCourseAccess).filter(
        TeacherCourseAccess.teacher_id == current_user.id,
        TeacherCourseAccess.course_id == course_id
    ).first()

    is_locked = True if not access else False

    # 3. 构造返回（允许预览，不再抛出403）
    course_data = course.__dict__.copy()
    course_data['public_id'] = public_id
    course_data['is_locked'] = is_locked

    return course_data


# ------------------------------------------------------------------
# 5. 获取课程大纲 (章节+课时，支持预览模式)
# ------------------------------------------------------------------
@router.get("/courses/{public_id}/chapters")
def read_course_chapters(
    public_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    course_id = decode_id(public_id)

    if not course_id:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 1. 检查课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 2. 检查授权状态
    access = db.query(TeacherCourseAccess).filter(
        TeacherCourseAccess.teacher_id == current_user.id,
        TeacherCourseAccess.course_id == course_id
    ).first()
    is_locked = True if not access else False

    # 缓存键需要区分是否已授权
    cache_key = f"course:{course_id}:chapters:preview_{is_locked}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # 3. 查询所有章节 (按 sort_order 排序)
    chapters = db.query(CourseChapter).filter(CourseChapter.course_id == course_id).order_by(CourseChapter.sort_order).all()

    # 4. 计算预览章节的课时总数（前N章的所有课时可预览）
    preview_lesson_count = 0
    if is_locked:
        preview_chapters = chapters[:PREVIEW_CHAPTER_COUNT]
        for ch in preview_chapters:
            preview_lesson_count += db.query(CourseLesson).filter(CourseLesson.chapter_id == ch.id).count()

    # 5. 遍历所有章节构建返回数据
    results = []
    current_lesson_index = 0  # 全局课时索引，用于判断是否在预览范围内

    for chapter in chapters:
        # 查询每个章节下的课时
        lessons = db.query(CourseLesson).filter(CourseLesson.chapter_id == chapter.id).order_by(CourseLesson.sort_order).all()

        lesson_list = []
        for l in lessons:
            current_lesson_index += 1

            # 判断该课时是否可预览（未授权时：前N章的课时可预览）
            is_previewable = not is_locked or current_lesson_index <= preview_lesson_count

            # 预览模式下，不可预览的课时不返回file_url
            file_url = l.file_url if is_previewable else None

            # 预览模式下不返回作业信息
            task_info = None
            if not is_locked and l.task:
                task_info = {
                    "id": l.task.id,
                    "title": l.task.title,
                    "content": l.task.content
                }

            lesson_list.append({
                "id": l.id,
                "title": l.title,
                "type": l.resource_type, # pdf / video / ppt
                "duration": l.duration,
                "is_free": l.is_free,
                "is_previewable": is_previewable,  # 新增字段：标记是否可预览
                "file_url": file_url,
                "task": task_info
            })

        results.append({
            "id": chapter.id,
            "title": chapter.title,
            "isOpen": False, # 前端控制折叠状态
            "lessons": lesson_list
        })

    # 存入缓存（5分钟）
    set_cache(cache_key, results, expire=300)

    return results


@router.get("/courses/{public_id}/interactive-app", response_model=schemas.InteractiveAppOut)
def read_course_interactive_app(
    public_id: str,
    request: Request,
    app_type: str = Query("ppt-test"),
    lesson_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    course_id = decode_id(public_id)
    if not course_id:
        raise HTTPException(status_code=404, detail="课程不存在")

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    available_lesson_ids = _extract_available_lesson_ids_from_manifest(course_id, app_type)
    entry, version = _extract_entry_from_manifest(course_id, app_type, lesson_id=lesson_id)
    if not entry:
        raise HTTPException(status_code=404, detail="未配置交互式资源入口")

    relative_url, absolute_url = _build_interactive_urls(request, entry)
    return {
        "app_type": app_type,
        "entry_url": absolute_url,
        "relative_url": relative_url,
        "version": version,
        "lesson_id": lesson_id,
        "available_lesson_ids": available_lesson_ids,
        "source": "manifest",
    }



# ------------------------------------------------------------------
# 6. 获取课程的标准作业模板列表
# ------------------------------------------------------------------
@router.get("/courses/{public_id}/tasks", response_model=List[schemas.CourseTaskOut])
def read_course_tasks(
    public_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 解密 ID
    course_id = decode_id(public_id)
    if not course_id:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 2. 检查课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 3. 查询作业模板 (按 sort_order 排序)
    tasks = db.query(CourseTask).filter(
        CourseTask.course_id == course_id
    ).order_by(CourseTask.sort_order).all()
    
    return tasks


# ------------------------------------------------------------------
# [教师端] 获取某作业在各班级的发布情况
# ------------------------------------------------------------------
@router.get("/tasks/{task_id}/publish_status", response_model=List[schemas.ClassTaskStatus])
def get_task_publish_status(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 查作业模板
    task = db.query(CourseTask).filter(CourseTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="作业模板不存在")

    # 2. 查该老师名下，绑定了该课程的所有班级
    # 逻辑：Class -> ClassCourseBinding -> Course (id == task.course_id)
    relevant_classes = db.query(Class).join(ClassCourseBinding)\
        .filter(
            Class.teacher_id == current_user.id,
            ClassCourseBinding.course_id == task.course_id
        ).all()

    results = []
    for cls in relevant_classes:
        # 3. 查该班级是否已发布过这个作业
        assignment = db.query(ClassAssignment).filter(
            ClassAssignment.class_id == cls.id,
            ClassAssignment.origin_task_id == task.id
        ).first()

        results.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "deadline": assignment.deadline if assignment else None,
            "is_published": True if assignment else False
        })

    return results


# ------------------------------------------------------------------
# [教师端] 批量设置/更新作业截止时间 (发布作业)
# ------------------------------------------------------------------
@router.post("/tasks/{task_id}/publish")
def publish_task_to_classes(
    task_id: int,
    publish_data: schemas.TaskPublishRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 查作业模板
    task = db.query(CourseTask).filter(CourseTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="作业模板不存在")

    count = 0
    
    for config in publish_data.configs:
        # 2. 校验班级权限 (防止给别人的班级发作业)
        cls = db.query(Class).filter(Class.id == config.class_id, Class.teacher_id == current_user.id).first()
        if not cls:
            continue # 跳过非法班级

        # 3. 查找是否已存在实例 (Upsert 逻辑)
        assignment = db.query(ClassAssignment).filter(
            ClassAssignment.class_id == cls.id,
            ClassAssignment.origin_task_id == task.id
        ).first()

        if assignment:
            # A. 已存在 -> 更新截止时间
            assignment.deadline = config.deadline
            # 如果之前是草稿，改为进行中
            if assignment.status == 0: 
                assignment.status = 1
        else:
            # B. 不存在 -> 创建新实例 (正式发布)
            new_assignment = ClassAssignment(
                class_id=cls.id,
                origin_task_id=task.id,
                title=task.title,
                content=task.content,
                deadline=config.deadline,
                status=1 # 默认为进行中
            )
            db.add(new_assignment)
        
        count += 1

    db.commit()
    return {"message": f"成功更新了 {count} 个班级的作业配置"}


# ==================================================================
#                       学生端专用接口
# ==================================================================

def check_student_permission(db: Session, user_id: int, course_id: int):
    """
    辅助函数：检查学生是否有权访问该课程
    逻辑：学生 -> 选课记录(Enrollment) -> 班级 -> 绑定记录(ClassCourseBinding) -> 课程
    """
    # 联表查询：是否存在一条链路连接该学生和该课程
    has_permission = db.query(Enrollment)\
        .join(ClassCourseBinding, Enrollment.class_id == ClassCourseBinding.class_id)\
        .filter(
            Enrollment.student_id == user_id,
            ClassCourseBinding.course_id == course_id
        ).first()
        
    if not has_permission:
        raise HTTPException(status_code=403, detail="你所在的班级未开通此课程，无权访问")
    
    return True

# ------------------------------------------------------------------
# 6. [学生] 获取课程详情 (用于概览页)
# ------------------------------------------------------------------
@router.get("/student/courses/{public_id}", response_model=schemas.CourseOut)
def read_student_course_detail(
    public_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):

    course_id = decode_id(public_id)
    if not course_id:
        raise HTTPException(status_code=404, detail="课程不存在")

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅限学生访问")

    # 1. 鉴权
    check_student_permission(db, current_user.id, course_id)

    # 2. 查询课程信息
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
        
    
    # 3. 构造返回 (学生端看到的肯定都是解锁的，所以 is_locked=False)
    course_data = course.__dict__.copy()
    course_data['is_locked'] = False
    
    return course_data

# ------------------------------------------------------------------
# 7. [学生] 获取课程章节目录 (用于学习页)
# ------------------------------------------------------------------
@router.get("/student/courses/{public_id}/chapters")
def read_student_course_chapters(
    public_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):

    course_id = decode_id(public_id)
    if not course_id:
        raise HTTPException(status_code=404, detail="课程不存在")

    enrollment = db.query(Enrollment).join(ClassCourseBinding, Enrollment.class_id == ClassCourseBinding.class_id)\
        .filter(
            Enrollment.student_id == current_user.id,
            ClassCourseBinding.course_id == course_id
        ).first()
    
    if not enrollment:
        raise HTTPException(status_code=403, detail="未找到班级关联信息")
    
    current_class_id = enrollment.class_id
        
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅限学生访问")

    # 1. 鉴权
    check_student_permission(db, current_user.id, course_id)

    # 2. 查询章节 (复用之前的逻辑，但这里是独立的接口，方便未来加进度状态)
    chapters = db.query(CourseChapter).filter(CourseChapter.course_id == course_id).order_by(CourseChapter.sort_order).all()
    
    results = []
    for chapter in chapters:
        lessons = db.query(CourseLesson).filter(CourseLesson.chapter_id == chapter.id).order_by(CourseLesson.sort_order).all()
        
        lesson_list = []
        for l in lessons:
            # === ✅ 作业状态计算核心逻辑 ===
            assignment_info = {
                "assignment_id": None,
                "status": "none", # 默认未发布
                "deadline": None,
                "score": None
            }
            
            # A. 检查这节课有没有绑定作业模板
            if l.task:
                # B. 检查班级有没有发布这个作业
                assignment = db.query(ClassAssignment).filter(
                    ClassAssignment.class_id == current_class_id,
                    ClassAssignment.origin_task_id == l.task.id
                ).first()
                
                if assignment:
                    assignment_info["assignment_id"] = assignment.id
                    assignment_info["deadline"] = assignment.deadline
                    
                    # C. 检查学生有没有提交
                    submission = db.query(StudentSubmission).filter(
                        StudentSubmission.assignment_id == assignment.id,
                        StudentSubmission.student_id == current_user.id
                    ).first()
                    
                    if submission:
                        if submission.status == 1: # 已批改
                            assignment_info["status"] = "graded"
                            assignment_info["score"] = submission.score
                        else:
                            assignment_info["status"] = "submitted"
                    else:
                        # 没提交，检查是否过期
                        # 这里简单处理，如果 assignment.status == 2 也可以算 expired
                        assignment_info["status"] = "pending"
            # ==============================

            progress = db.query(StudentLearningProgress).filter(
                StudentLearningProgress.student_id == current_user.id,
                StudentLearningProgress.lesson_id == l.id
            ).first()
            
            p_status = progress.status if progress else 0
            p_position = progress.last_position if progress else 1

            task_info = None
            if l.task:
                task_info = {
                    "id": l.task.id,
                    "title": l.task.title
                }

            lesson_list.append({
                "id": l.id,
                "title": l.title,
                "type": l.resource_type,
                "duration": l.duration,
                "is_free": l.is_free, # 学生端其实都是免费的
                "file_url": l.file_url,
                "task": task_info,
                "status": p_status,
                "last_position": p_position,
                "assignment": assignment_info
                # TODO: 未来在这里添加 "is_finished": True/False
            })

        results.append({
            "id": chapter.id,
            "title": chapter.title,
            "isOpen": False,
            "lessons": lesson_list
        })
        
    return results


@router.get("/student/courses/{public_id}/interactive-app", response_model=schemas.InteractiveAppOut)
def read_student_course_interactive_app(
    public_id: str,
    request: Request,
    app_type: str = Query("ppt-test"),
    lesson_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    course_id = decode_id(public_id)
    if not course_id:
        raise HTTPException(status_code=404, detail="课程不存在")

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅限学生访问")

    check_student_permission(db, current_user.id, course_id)

    available_lesson_ids = _extract_available_lesson_ids_from_manifest(course_id, app_type)
    entry, version = _extract_entry_from_manifest(course_id, app_type, lesson_id=lesson_id)
    if not entry:
        raise HTTPException(status_code=404, detail="未配置交互式资源入口")

    relative_url, absolute_url = _build_interactive_urls(request, entry)
    return {
        "app_type": app_type,
        "entry_url": absolute_url,
        "relative_url": relative_url,
        "version": version,
        "lesson_id": lesson_id,
        "available_lesson_ids": available_lesson_ids,
        "source": "manifest",
    }


# ------------------------------------------------------------------
# 8. [学生端] 更新学习进度
# ------------------------------------------------------------------
@router.post("/student/progress")
def update_student_progress(
    progress_in: schemas.ProgressUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="权限不足")

    # 使用 merge 或 on_conflict 处理
    try:
        # 查找现有记录
        record = db.query(StudentLearningProgress).filter(
            StudentLearningProgress.student_id == current_user.id,
            StudentLearningProgress.lesson_id == progress_in.lesson_id
        ).first()

        if not record:
            # 新增
            record = StudentLearningProgress(
                student_id=current_user.id,
                lesson_id=progress_in.lesson_id,
                status=progress_in.status,
                last_position=progress_in.last_position
            )
            db.add(record)
        else:
            # 更新逻辑：状态只能往前走 (比如已完成不能变回进行中)
            if progress_in.status > record.status:
                record.status = progress_in.status

            # 页码总是更新为最新的
            record.last_position = progress_in.last_position

        db.commit()
        return {"message": "进度已保存"}

    except Exception as e:
        db.rollback()
        # 如果是因为唯一键冲突，先更新再提交
        if "Duplicate entry" in str(e):
            record = db.query(StudentLearningProgress).filter(
                StudentLearningProgress.student_id == current_user.id,
                StudentLearningProgress.lesson_id == progress_in.lesson_id
            ).first()

            if record:
                if progress_in.status > record.status:
                    record.status = progress_in.status
                record.last_position = progress_in.last_position
                db.commit()
                return {"message": "进度已保存（已处理并发）"}

        raise e
