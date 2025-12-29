from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.content import Course
from app.schemas import content as schemas

router = APIRouter()

# ------------------------------------------------------------------
# 1. 获取“我”创建的课程资源库
# ------------------------------------------------------------------
@router.get("/courses/me", response_model=List[schemas.CourseOut])
def read_my_courses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 只有老师能看自己的资源库
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")
        
    courses = db.query(Course).filter(Course.owner_id == current_user.id).all()
    return courses

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