import os
import sys
import re

# 确保能找到 app 模块
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.db.session import SessionLocal

# ✅ 必须导入所有关联模型，防止报错
from app.models.user import User
from app.models.profile import TeacherProfile, StudentProfile
from app.models.course import Class, Enrollment
from app.models.content import Course, TeacherCourseAccess

def get_db():
    return SessionLocal()

def parse_input_list(input_str):
    """
    将输入字符串解析为列表
    支持逗号、空格、分号分隔
    例如: "user1, user2 user3" -> ['user1', 'user2', 'user3']
    """
    # 使用正则分割，支持 , ; 空格
    return [x.strip() for x in re.split(r'[,\s;]+', input_str) if x.strip()]

def get_teachers_batch(db: Session):
    """批量获取教师对象"""
    print("\n👤 第一步：选择教师")
    print("   提示：输入多个账号请用逗号或空格分隔")
    print("   提示：输入 'all' 可选择系统中所有教师")
    
    while True:
        raw_input = input("👉 请输入【教师账号列表】: ").strip()
        if not raw_input: continue

        selected_teachers = []

        # 模式 A: 所有教师
        if raw_input.lower() == 'all':
            selected_teachers = db.query(User).filter(User.role.in_(['teacher', 'admin'])).all()
            if not selected_teachers:
                print("❌ 系统中没有找到任何教师账号。")
                return None
            print(f"✅ 已选中系统中所有教师，共 {len(selected_teachers)} 人。")
            return selected_teachers

        # 模式 B: 指定教师
        usernames = parse_input_list(raw_input)
        not_found = []

        # 批量查询
        users = db.query(User).filter(User.username.in_(usernames)).all()
        
        # 检查查出来的用户是否合法
        for u in users:
            if u.role in ['teacher', 'admin']:
                selected_teachers.append(u)
            else:
                print(f"⚠️ 跳过账号 '{u.username}'：角色不是教师/管理员")

        # 检查哪些没找到
        found_names = [u.username for u in users]
        for name in usernames:
            if name not in found_names:
                not_found.append(name)

        if not_found:
            print(f"❌ 以下账号未找到: {', '.join(not_found)}")
        
        if not selected_teachers:
            print("❌ 没有选中任何有效教师，请重新输入。")
            continue

        print(f"✅ 已选中 {len(selected_teachers)} 位教师:")
        for t in selected_teachers:
            name = t.full_name or t.username
            if t.teacher_profile and t.teacher_profile.real_name:
                name = t.teacher_profile.real_name
            print(f"   - {name} ({t.username})")
            
        return selected_teachers

def get_courses_batch(db: Session):
    """批量获取课程对象"""
    print("\n📚 第二步：选择课程")
    print("-" * 50)
    
    all_courses = db.query(Course).all()
    if not all_courses:
        print("❌ 数据库无课程。")
        return None

    for c in all_courses:
        print(f"  [ID: {c.id}] {c.name}")
    print("-" * 50)
    print("   提示：输入 'all' 选择所有课程")
    print("   提示：输入多个ID用逗号或空格分隔 (如: 1, 2, 6)")

    while True:
        raw_input = input("👉 请输入【课程 ID 列表】: ").strip()
        if not raw_input: continue

        selected_courses = []

        # 模式 A: 所有课程
        if raw_input.lower() == 'all':
            selected_courses = all_courses
            print(f"✅ 已选中所有课程，共 {len(selected_courses)} 门。")
            return selected_courses

        # 模式 B: 指定 ID
        id_strs = parse_input_list(raw_input)
        ids = []
        for s in id_strs:
            if s.isdigit():
                ids.append(int(s))
        
        if not ids:
            print("❌ 未识别到有效数字 ID")
            continue

        selected_courses = db.query(Course).filter(Course.id.in_(ids)).all()
        
        if not selected_courses:
            print("❌ 未找到对应的课程 ID，请重新输入")
            continue

        print(f"✅ 已选中 {len(selected_courses)} 门课程:")
        for c in selected_courses:
            print(f"   - [ID:{c.id}] {c.name}")
            
        return selected_courses

def execute_batch_grant(db: Session, teachers: list, courses: list):
    """执行 M x N 授权"""
    print(f"\n🚀 第三步：执行授权")
    print(f"   即将为 {len(teachers)} 位教师，每人授权 {len(courses)} 门课程。")
    confirm = input("   确认执行吗？(y/n): ").strip().lower()
    
    if confirm != 'y':
        print("🚫 操作已取消")
        return

    count_new = 0
    count_skip = 0

    for teacher in teachers:
        print(f"\n👤 处理教师: {teacher.username} ...")
        for course in courses:
            # 查重
            exists = db.query(TeacherCourseAccess).filter(
                TeacherCourseAccess.teacher_id == teacher.id,
                TeacherCourseAccess.course_id == course.id
            ).first()

            if exists:
                print(f"   [跳过] 已拥有课程: {course.name}")
                count_skip += 1
            else:
                new_access = TeacherCourseAccess(
                    teacher_id=teacher.id,
                    course_id=course.id
                )
                db.add(new_access)
                print(f"   [新增] 授权课程: {course.name}")
                count_new += 1
    
    db.commit()
    print("\n" + "="*50)
    print(f"🎉 批量处理完成！")
    print(f"   新增授权: {count_new} 条")
    print(f"   跳过重复: {count_skip} 条")
    print("="*50)

if __name__ == "__main__":
    db = get_db()
    
    print("="*50)
    print("  🔐 批量课程授权工具 v3.0 (Multi-Select)")
    print("="*50)

    try:
        # 1. 选人
        teachers = get_teachers_batch(db)
        if not teachers: exit()

        # 2. 选课
        courses = get_courses_batch(db)
        if not courses: exit()

        # 3. 执行
        execute_batch_grant(db, teachers, courses)

    except KeyboardInterrupt:
        print("\n\n🚫 用户强制退出")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()