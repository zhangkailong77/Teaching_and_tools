from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.api import deps
from app.models.user import User
from app.models.course import ClassAssignment, StudentSubmission, Class, Enrollment
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
            status=1 # 已提交
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
            # 打印一下数据库里的真实值
            # print(f"作业[{assign.title}] -> DB Status: {sub.status}")
            
            # 强制逻辑转换
            if sub.status == 2:
                status = 2 # 已批改
            else:
                status = 1 # 已交/待批改
            
            score = sub.score

        # 构造返回
        results.append({
            "id": assign.id,
            "title": assign.title,
            "course_name": assign.origin_task.course.name if assign.origin_task else "自定义",
            "lesson_title": assign.origin_task.lesson.title if assign.origin_task and assign.origin_task.lesson else "单元作业",
            "deadline": assign.deadline,
            "status": status,
            "score": score,
            "course_cover": assign.origin_task.course.cover if assign.origin_task and assign.origin_task.course else None
        })
        
    return results


# 3. [学生] 获取我的历史成绩趋势
@router.get("/my-scores")
def get_my_homework_scores(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 查询已批改(status=2)的提交记录，按批改时间排序，取最近 7 次
    submissions = db.query(StudentSubmission).join(ClassAssignment)\
        .filter(
            StudentSubmission.student_id == current_user.id,
            StudentSubmission.status == 1 # 1代表已批改(注意：我们在Schema里定义的是1是已批改，之前写错了？请确认一下你的数据库定义，假设1是已批改，或者status=2)
            # 修正：根据之前的建表语句，status: 0:未交, 1:已交, 2:已批改。所以这里应该是 status == 2
        ).filter(StudentSubmission.status == 2)\
        .order_by(StudentSubmission.graded_at.asc())\
        .limit(7)\
        .all()

    # 构造返回数据
    data = []
    for sub in submissions:
        data.append({
            "title": sub.assignment.title, # 作业标题
            "score": sub.score,            # 分数
            "date": sub.graded_at.strftime("%m-%d") if sub.graded_at else "" # 批改日期
        })
    
    return data


# ------------------------------------------------------------------
# 4. [教师端] 获取作业管理首页统计数据
# ------------------------------------------------------------------
@router.get("/teacher/stats", response_model=schemas.HomeworkStatsV2) # ✅ 修改 Response Model
def get_teacher_homework_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")

    # A. 全局计数 (饼图数据)
    # 找到该老师发布的所有作业实例 ID
    assign_ids = db.query(ClassAssignment.id).join(Class).filter(Class.teacher_id == current_user.id).all()
    assign_ids = [i[0] for i in assign_ids]

    if not assign_ids:
        return {"pending_count": 0, "pie_data": {"submitted":0, "graded":0, "unsubmitted":0}, "rank_data": []}

    # 统计提交状态
    total_submissions = db.query(StudentSubmission).filter(StudentSubmission.assignment_id.in_(assign_ids)).count()
    graded = db.query(StudentSubmission).filter(StudentSubmission.assignment_id.in_(assign_ids), StudentSubmission.status == 2).count()
    submitted = db.query(StudentSubmission).filter(StudentSubmission.assignment_id.in_(assign_ids), StudentSubmission.status == 1).count()
    
    # 待批改总数
    pending_count = submitted 

    # B. 班级提交率排行 (Bar Chart)
    # 遍历每个班级，计算 (已交+已批) / 总人数
    classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()
    rank_data = []
    
    for cls in classes:
        # 班级总人数
        student_count = db.query(Enrollment).filter(Enrollment.class_id == cls.id).count()
        if student_count == 0: continue
            
        # 该班级发布的作业数
        assign_count = db.query(ClassAssignment).filter(ClassAssignment.class_id == cls.id).count()
        if assign_count == 0: continue
            
        # 理论应交总数 = 学生数 * 作业数
        total_required = student_count * assign_count
        
        # 实际提交总数
        actual_submitted = db.query(StudentSubmission).join(ClassAssignment)\
            .filter(ClassAssignment.class_id == cls.id).count()
            
        rate = int((actual_submitted / total_required) * 100)
        rank_data.append({"class_name": cls.name, "rate": rate})
    
    # 按提交率倒序排，取前5
    rank_data.sort(key=lambda x: x['rate'], reverse=True)

    return {
        "pending_count": pending_count,
        "pie_data": {
            "graded": graded,
            "submitted": submitted,
            # 未提交 = (所有作业的应交总数) - (实交总数) - 这里简化处理，前端画图时不显示未提交也可以
            "unsubmitted": 0 
        },
        "rank_data": rank_data[:5]
    }


# ------------------------------------------------------------------
# 5. [教师端] 获取作业列表 (含进度统计)
# ------------------------------------------------------------------
@router.get("/teacher/list", response_model=List[schemas.ClassHomeworkGroup]) # ✅ 修改 Response Model
def get_teacher_homework_list(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 查出所有班级
    classes = db.query(Class).filter(Class.teacher_id == current_user.id).order_by(Class.created_at.desc()).all()
    
    grouped_results = []
    
    for cls in classes:
        # 查该班级的作业
        assignments = db.query(ClassAssignment).filter(ClassAssignment.class_id == cls.id).order_by(ClassAssignment.created_at.desc()).all()
        
        if not assignments: continue # 如果班级没作业，就不显示在列表里
            
        cls_pending_count = 0
        assign_list = []
        
        # 班级总人数
        total_students = db.query(Enrollment).filter(Enrollment.class_id == cls.id).count()

        for assign in assignments:
            graded = db.query(StudentSubmission).filter(StudentSubmission.assignment_id == assign.id, StudentSubmission.status == 2).count()
            submitted = db.query(StudentSubmission).filter(StudentSubmission.assignment_id == assign.id, StudentSubmission.status == 1).count()
            
            # 累加班级待批数
            cls_pending_count += submitted
            
            course_name = "自定义"
            if assign.origin_task and assign.origin_task.course:
                course_name = assign.origin_task.course.name

            assign_list.append({
                "id": assign.id,
                "title": assign.title,
                "course_name": course_name,
                "deadline": assign.deadline,
                "stats": {
                    "total": total_students,
                    "graded": graded,
                    "submitted": submitted,
                    "unsubmitted": total_students - graded - submitted
                }
            })
            
        grouped_results.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "pending_count": cls_pending_count,
            "assignments": assign_list
        })
        
    return grouped_results


# 6. [教师端] 获取某作业的所有提交记录 (批改列表)
@router.get("/{assignment_id}/submissions")
def get_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")

    # 1. 查作业详情
    assignment = db.query(ClassAssignment).filter(ClassAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    # 2. 查该班级的所有学生 (为了把未交的人也列出来)
    enrollments = db.query(Enrollment).filter(Enrollment.class_id == assignment.class_id).all()
    
    results = []
    for enrollment in enrollments:
        student = enrollment.student
        
        # 3. 查提交记录
        sub = db.query(StudentSubmission).filter(
            StudentSubmission.assignment_id == assignment_id,
            StudentSubmission.student_id == student.id
        ).first()

        ui_status = 0 
        
        if sub:
            # 数据库 status: 1=已提交(待批改), 2=已批改
            
            if sub.status == 1:
                ui_status = 1  # 映射为前端的 "待批改"
                
            elif sub.status == 2:
                ui_status = 2  # 映射为前端的 "已批改"
                
            # 如果还有其他情况(比如0)，可以根据你的数据库实际情况处理
            # 假设之前旧数据有0，也可以归为待批改
            elif sub.status == 0: 
                 ui_status = 1

        results.append({
            "student_id": student.id,
            "student_name": student.full_name or student.username,
            "student_number": student.student_number,
            "avatar": student.student_profile.avatar if student.student_profile else None,
            "status": ui_status, 
            "submission_id": sub.id if sub else None,
            "content": sub.content if sub else None,
            "score": sub.score if sub else None,
            "feedback": sub.feedback if sub else None,
            "submitted_at": sub.submitted_at if sub else None,
            "annotated_content": sub.annotated_content if sub else None,
            "annotations": sub.annotations if sub else []
        })
    
    return {
        "assignment_title": assignment.title,
        "assignment_content": assignment.content,
        "students": results
    }

# 7. [教师端] 提交评分
@router.post("/submissions/{submission_id}/grade")
def grade_submission(
    submission_id: int,
    data: schemas.GradeSubmission, # ✅ 改为使用 Schema 接收
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    sub = db.query(StudentSubmission).filter(StudentSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="提交记录不存在")
        
    # 1. 保存原有字段
    sub.score = data.score
    sub.feedback = data.feedback
    
    # 2. ✅ 保存新增字段 (批注)
    if data.annotated_content:
        sub.annotated_content = data.annotated_content
    
    # 注意：SQLAlchemy 处理 JSON 字段时，最好重新赋值以触发更新检测
    if data.annotations is not None:
        sub.annotations = data.annotations
        
    sub.status = 2 # 标记为已批改
    sub.graded_at = datetime.now()
    
    db.commit()
    return {"message": "评分与批注已保存"}


# ------------------------------------------------------------------
# 8. [学生] 获取作业批改详情 (含批注)
# ------------------------------------------------------------------
@router.get("/{assignment_id}/result")
def get_submission_result(
    assignment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可查看")

    # 1. 查找提交记录
    sub = db.query(StudentSubmission).filter(
        StudentSubmission.assignment_id == assignment_id,
        StudentSubmission.student_id == current_user.id
    ).first()

    if not sub:
        raise HTTPException(status_code=404, detail="未找到提交记录")

    # 2. 查找作业题目信息 (用于回显题目)
    assignment = db.query(ClassAssignment).filter(ClassAssignment.id == assignment_id).first()
    
    # 3. 构造返回数据
    return {
        "submission_id": sub.id,
        "status": sub.status,
        "score": sub.score,
        "feedback": sub.feedback,
        "submitted_at": sub.submitted_at,
        "graded_at": sub.graded_at,
        
        # ✅ 核心：返回批改后的内容
        # 如果老师没做划词批注，annotated_content 是空的，那就退化显示原始 content
        "content": sub.annotated_content if sub.annotated_content else sub.content,
        "annotations": sub.annotations if sub.annotations else [],
        
        # 题目信息
        "assignment_title": assignment.title,
        "assignment_requirement": assignment.content
    }