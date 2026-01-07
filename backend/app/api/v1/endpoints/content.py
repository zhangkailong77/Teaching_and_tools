from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.hash import encode_id, decode_id

from app.api import deps
from app.models.user import User
from app.schemas import content as schemas
from app.models.course import Enrollment, Class, ClassAssignment, StudentSubmission
from app.models.content import Course, CourseChapter, CourseLesson, TeacherCourseAccess, ClassCourseBinding, StudentLearningProgress, CourseTask

router = APIRouter()

# ------------------------------------------------------------------
# 1. 获取“我”创建的课程资源库
# ------------------------------------------------------------------
@router.get("/courses/me", response_model=List[schemas.CourseOut])
def read_my_courses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):

    all_courses = db.query(Course).all()

    access_records = db.query(TeacherCourseAccess).filter(
        TeacherCourseAccess.teacher_id == current_user.id
    ).all()

    unlocked_course_ids = {record.course_id for record in access_records}
    
    results = []
    for course in all_courses:
        is_locked = course.id not in unlocked_course_ids
        course_data = course.__dict__.copy()
        course_data['is_locked'] = is_locked
        course_data['public_id'] = encode_id(course.id)
        
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
# 4. 获取单门课程详情
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

    # 2. 查询是否已授权 (复用之前的逻辑)
    # 这一步是为了让详情页也能显示"已授权/未开通"的状态
    access = db.query(TeacherCourseAccess).filter(
        TeacherCourseAccess.teacher_id == current_user.id,
        TeacherCourseAccess.course_id == course_id
    ).first()
    
    is_locked = True if not access else False

    if is_locked:
        # 抛出 403 禁止访问
        raise HTTPException(status_code=403, detail="该课程未开通，无法查看详情")

    # 3. 构造返回
    course_data = course.__dict__.copy()
    course_data['public_id'] = public_id
    course_data['is_locked'] = is_locked
    
    return course_data


# ------------------------------------------------------------------
# 5. 获取课程大纲 (章节+课时)
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

    # 2. 查询章节 (按 sort_order 排序)
    chapters = db.query(CourseChapter).filter(CourseChapter.course_id == course_id).order_by(CourseChapter.sort_order).all()
    
    results = []
    for chapter in chapters:
        # 3. 查询每个章节下的课时
        lessons = db.query(CourseLesson).filter(CourseLesson.chapter_id == chapter.id).order_by(CourseLesson.sort_order).all()
        
        lesson_list = []
        for l in lessons:
            task_info = None
            if l.task:
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
                "file_url": l.file_url,   # ✅ 这个字段很关键，前端预览要用
                "task": task_info
            })

        results.append({
            "id": chapter.id,
            "title": chapter.title,
            "isOpen": False, # 前端控制折叠状态
            "lessons": lesson_list
        })
        
    return results



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