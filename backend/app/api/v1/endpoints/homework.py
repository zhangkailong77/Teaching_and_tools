from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.models.course import ClassAssignment, StudentSubmission, Class
from app.models.content import CourseTask, Course
from app.schemas import homework as schemas

router = APIRouter()

# 1. [学生] 提交作业
@router.post("/{assignment_id}/submit")
def submit_homework(
    assignment_id: int,
    submission_in: schemas.SubmissionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可提交")

    # 检查作业是否存在
    assignment = db.query(ClassAssignment).filter(ClassAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
        
    # 检查是否截止 (可选)
    if assignment.deadline and datetime.now() > assignment.deadline:
        # 这里演示允许补交，但在前端提示逾期
        pass 

    # 查找是否已提交过 (支持多次提交覆盖)
    submission = db.query(StudentSubmission).filter(
        StudentSubmission.assignment_id == assignment_id,
        StudentSubmission.student_id == current_user.id
    ).first()

    if not submission:
        submission = StudentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            content=submission_in.content,
            status=0 # 已提交
        )
        db.add(submission)
    else:
        submission.content = submission_in.content
        submission.submitted_at = datetime.now()
        # 如果被打回(status=2)，重交后改为0
        if submission.status == 2:
            submission.status = 0
            
    db.commit()
    return {"message": "作业提交成功"}

# 2. [学生] 获取我的作业待办列表 (用于左侧红点和列表页)
@router.get("/my-todos", response_model=List[schemas.AssignmentCard])
def get_my_homework_todos(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 找到学生加入的所有班级
    enrollments = current_user.enrollments
    class_ids = [e.class_id for e in enrollments]
    
    # 2. 找到这些班级发布的所有作业
    # 联表 CourseTask 获取课程名和课时名
    assignments = db.query(ClassAssignment).join(CourseTask).join(Course)\
        .filter(ClassAssignment.class_id.in_(class_ids))\
        .filter(ClassAssignment.status == 1)\
        .all() # 1: 进行中
        
    results = []
    for assign in assignments:
        # 查提交状态
        sub = db.query(StudentSubmission).filter(
            StudentSubmission.assignment_id == assign.id,
            StudentSubmission.student_id == current_user.id
        ).first()
        
        status = 0 # 未交
        score = None
        if sub:
            status = 1 # 已交
            if sub.status == 1: status = 2 # 已批
            score = sub.score

        # 构造返回
        results.append({
            "id": assign.id,
            "title": assign.title,
            "course_name": assign.origin_task.course.name if assign.origin_task else "自定义",
            "lesson_title": assign.origin_task.lesson.title if assign.origin_task and assign.origin_task.lesson else "单元作业",
            "deadline": assign.deadline,
            "status": status,
            "score": score
        })
        
    return results