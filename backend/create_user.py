# 使用方法: python create_user.py
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.profile import TeacherProfile
# 导入所有模型，确保 SQLAlchemy 可以解析关联关系
from app.models.course import Class, Enrollment
from app.models.content import Course, ClassCourseBinding
from app.core import security

def create_user(username, password, role="student", full_name=None, student_number=None):
    db: Session = SessionLocal()
    try:
        # 1. 检查是否存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ 错误: 用户 {username} 已存在！")
            return

        # 2. 创建用户
        new_user = User(
            username=username,
            hashed_password=security.get_password_hash(password),
            role=role,
            created_at=datetime.now(),
            is_active=True,
            full_name=full_name,
            student_number=student_number
        )
        # 如果你之前加了 nickname 字段，记得在这里加上
        # nickname=nickname 
        
        db.add(new_user)
        db.commit()
        print(f"✅ 成功: 用户 {username} ({role}) 创建完毕！")
        
    except Exception as e:
        print(f"❌ 发生异常: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("--- 教学管理平台账号生成器 ---")
    # 1. 基础信息
    u_name = input("请输入登录账号(手机号): ").strip()
    if not u_name:
        print("账号不能为空")
        sys.exit(1)
        
    u_pass = input("请输入密码: ").strip()
    if not u_pass:
        print("密码不能为空")
        sys.exit(1)
        
    u_role = input("请输入角色 (student/teacher) [默认student]: ").strip()
    if u_role not in ["student", "teacher"]:
        u_role = "student"
    
    # 2. 补充信息 (新增)
    u_fullname = input("请输入真实姓名 (可选): ").strip()
    
    u_number = None
    if u_role == "student":
        u_number = input("请输入学号 (可选): ").strip()
    
    # 处理空字符串为 None
    if not u_fullname: u_fullname = None
    if not u_number: u_number = None

    # 3. 执行创建
    create_user(u_name, u_pass, u_role, u_fullname, u_number)