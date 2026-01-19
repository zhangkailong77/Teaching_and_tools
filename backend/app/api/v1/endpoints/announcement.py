# backend/app/api/v1/endpoints/announcement.py

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.api import deps
from app.models.user import User
from app.models import announcement as models
from app.models.course import Class, Enrollment
from app.schemas import announcement as schemas

router = APIRouter()

# -----------------------------------------------------------
# 1. [教师] 发布公告
# -----------------------------------------------------------
@router.post("/", response_model=schemas.AnnouncementListOut)
def create_announcement(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.AnnouncementCreate,
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")

    # 1. 创建主表记录
    db_obj = models.Announcement(
        title=item_in.title,
        content=item_in.content,
        type=item_in.type,
        target_type=item_in.target_type,
        is_pinned=item_in.is_pinned,
        publisher_id=current_user.id,
        expires_at=item_in.expires_at
    )
    db.add(db_obj)
    db.flush() # 获取 ID

    # 2. 处理目标班级
    target_class_ids = []
    if item_in.target_type == 'all':
        # 查找该老师所有的班级
        classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()
        target_class_ids = [c.id for c in classes]
    else:
        target_class_ids = item_in.class_ids

    # 写入关联表
    for cid in target_class_ids:
        # 简单校验班级权限(可选)
        target = models.AnnouncementTarget(
            announcement_id=db_obj.id,
            class_id=cid
        )
        db.add(target)

    db.commit()
    db.refresh(db_obj)

    publisher = current_user
    p_name = publisher.full_name or publisher.username
    if publisher.teacher_profile:
        real_name = publisher.teacher_profile.real_name
        title = publisher.teacher_profile.title
        if real_name:
            p_name = real_name
        if title:
            p_name = f"{p_name} · {title}"
    
    # 构造简单返回
    return {
        "id": db_obj.id,
        "title": db_obj.title,
        "type": db_obj.type,
        "is_pinned": db_obj.is_pinned,
        "created_at": db_obj.created_at,
        "publisher_name": p_name
    }

# -----------------------------------------------------------
# 2. [教师] 获取我发布的公告列表
# -----------------------------------------------------------
@router.get("/teacher/list", response_model=List[schemas.AnnouncementListOut])
def get_teacher_announcements(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher": return []

    # 查询该老师发布的所有公告
    anns = db.query(models.Announcement).filter(
        models.Announcement.publisher_id == current_user.id,
        models.Announcement.status == 1
    ).order_by(models.Announcement.is_pinned.desc(), models.Announcement.created_at.desc()).all()

    results = []
    for ann in anns:
        # 统计应读人数 (所有目标班级的学生总和)
        target_class_ids = [t.class_id for t in ann.targets]
        total_count = db.query(func.count(Enrollment.student_id)).filter(
            Enrollment.class_id.in_(target_class_ids)
        ).scalar() or 0

        # 统计已读人数
        read_count = db.query(func.count(models.AnnouncementRead.id)).filter(
            models.AnnouncementRead.announcement_id == ann.id
        ).scalar() or 0

        publisher = current_user # 这里发布者就是当前登录用户
        p_name = publisher.full_name or publisher.username

        if publisher.teacher_profile:
            real_name = publisher.teacher_profile.real_name
            title = publisher.teacher_profile.title
            if real_name:
                p_name = real_name
            if title:
                p_name = f"{p_name} · {title}"

        results.append({
            "id": ann.id,
            "title": ann.title,
            "type": ann.type,
            "is_pinned": ann.is_pinned,
            "created_at": ann.created_at,
            "publisher_name": p_name,
            "read_count": read_count,
            "total_count": total_count,
            "content": ann.content 
        })
    return results


# -----------------------------------------------------------
# 2.5. [教师] 获取公告详情及阅读统计
# -----------------------------------------------------------
@router.get("/{ann_id}/detail")
def get_announcement_detail(
    ann_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """获取公告详情和阅读统计"""
    ann = db.query(models.Announcement).filter(
        models.Announcement.id == ann_id,
        models.Announcement.status == 1
    ).first()
    
    if not ann:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    # 权限检查：教师只能查看自己发布的，学生只能查看自己班级的
    if current_user.role == "teacher" and ann.publisher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看")
    
    # 获取目标班级信息
    target_class_ids = [t.class_id for t in ann.targets]
    classes = db.query(Class).filter(Class.id.in_(target_class_ids)).all()
    class_names = [c.name for c in classes]
    
    # 统计应读人数
    total_count = db.query(func.count(Enrollment.student_id)).filter(
        Enrollment.class_id.in_(target_class_ids)
    ).scalar() or 0
    
    # 统计已读人数
    read_count = db.query(func.count(models.AnnouncementRead.id)).filter(
        models.AnnouncementRead.announcement_id == ann_id
    ).scalar() or 0
    
    # 获取已读学生列表（教师端需要）
    read_students = []
    if current_user.role == "teacher":
        students = db.query(User).join(Enrollment).filter(
            Enrollment.class_id.in_(target_class_ids),
            User.role == 'student'
        ).all()
        
        read_ids = [r.student_id for r in ann.reads]
        
        for stu in students:
            read_students.append({
                "id": stu.id,
                "name": stu.full_name or stu.username,
                "student_number": stu.student_number,
                "is_read": stu.id in read_ids
            })
    
    return {
        "id": ann.id,
        "title": ann.title,
        "content": ann.content,
        "type": ann.type,
        "target_type": ann.target_type,
        "is_pinned": ann.is_pinned,
        "created_at": ann.created_at,
        "expires_at": ann.expires_at,
        "publisher_name": ann.publisher.full_name or ann.publisher.username,
        "class_names": class_names,
        "read_count": read_count,
        "total_count": total_count,
        "students": read_students
    }


# -----------------------------------------------------------
# 3. [学生] 获取我的班级公告
# -----------------------------------------------------------
@router.get("/student/list", response_model=List[schemas.AnnouncementListOut])
def get_student_announcements(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 找到学生所在的班级ID
    enrollment = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).first()
    if not enrollment: return []
    
    class_id = enrollment.class_id

    # 2. 查询发给该班级的公告
    # 关联路径: Announcement -> AnnouncementTarget -> class_id
    anns = db.query(models.Announcement).join(models.AnnouncementTarget).filter(
        models.AnnouncementTarget.class_id == class_id,
        models.Announcement.status == 1
    ).order_by(models.Announcement.is_pinned.desc(), models.Announcement.created_at.desc()).all()

    results = []
    for ann in anns:
        # 检查是否已读
        is_read = db.query(models.AnnouncementRead).filter(
            models.AnnouncementRead.announcement_id == ann.id,
            models.AnnouncementRead.student_id == current_user.id
        ).first() is not None

        publisher = ann.publisher
        p_name = publisher.full_name or publisher.username

        # 如果有教师档案，优先用档案里的 真实姓名 + 职称
        if publisher.teacher_profile:
            real_name = publisher.teacher_profile.real_name
            title = publisher.teacher_profile.title
            
            if real_name:
                p_name = real_name
            if title:
                p_name = f"{p_name} · {title}"

        results.append({
            "id": ann.id,
            "title": ann.title,
            "type": ann.type,
            "is_pinned": ann.is_pinned,
            "created_at": ann.created_at,
            "publisher_name": p_name,
            "is_read": is_read,
            "content": ann.content 
        })
    return results

# -----------------------------------------------------------
# 4. [学生] 标记公告为已读
# -----------------------------------------------------------
@router.post("/{ann_id}/read")
def mark_as_read(
    ann_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 检查记录是否存在
    exists = db.query(models.AnnouncementRead).filter(
        models.AnnouncementRead.announcement_id == ann_id,
        models.AnnouncementRead.student_id == current_user.id
    ).first()
    
    if not exists:
        read_record = models.AnnouncementRead(
            announcement_id=ann_id,
            student_id=current_user.id
        )
        db.add(read_record)
        db.commit()
    
    return {"status": "ok"}


# -----------------------------------------------------------
# 5. [学生] 获取未读消息数量
# -----------------------------------------------------------
@router.get("/student/unread-count")
def get_unread_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """获取学生未读公告数量"""
    
    # 1. 找到学生所在的班级ID
    enrollment = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).first()
    if not enrollment:
        return {"unread_count": 0}
    
    class_id = enrollment.class_id
    
    # 2. 查询该班级的所有公告ID
    ann_ids = db.query(models.Announcement.id).join(models.AnnouncementTarget).filter(
        models.AnnouncementTarget.class_id == class_id,
        models.Announcement.status == 1
    ).all()
    
    ann_ids = [aid[0] for aid in ann_ids]
    
    if not ann_ids:
        return {"unread_count": 0}
    
    # 3. 查询已读的公告ID
    read_ids = db.query(models.AnnouncementRead.announcement_id).filter(
        models.AnnouncementRead.student_id == current_user.id,
        models.AnnouncementRead.announcement_id.in_(ann_ids)
    ).all()
    
    read_ids = [rid[0] for rid in read_ids]
    
    # 4. 计算未读数量
    unread_count = len(ann_ids) - len(read_ids)
    
    return {"unread_count": unread_count}