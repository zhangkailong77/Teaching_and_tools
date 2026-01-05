from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.content import Course, TeacherCourseAccess
from app.schemas import content as schemas
from app.models.content import CourseChapter, CourseLesson

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
@router.get("/courses/{course_id}", response_model=schemas.CourseOut)
def read_course_detail(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
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

    # 3. 构造返回
    course_data = course.__dict__.copy()
    course_data['is_locked'] = is_locked
    
    return course_data


# ------------------------------------------------------------------
# 5. 获取课程大纲 (章节+课时)
# ------------------------------------------------------------------
@router.get("/courses/{course_id}/chapters")
def read_course_chapters(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
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
            lesson_list.append({
                "id": l.id,
                "title": l.title,
                "type": l.resource_type, # pdf / video / ppt
                "duration": l.duration,
                "is_free": l.is_free,
                "file_url": l.file_url   # ✅ 这个字段很关键，前端预览要用
            })

        results.append({
            "id": chapter.id,
            "title": chapter.title,
            "isOpen": False, # 前端控制折叠状态
            "lessons": lesson_list
        })
        
    return results