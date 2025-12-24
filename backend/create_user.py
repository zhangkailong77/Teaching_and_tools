# 使用方法: python create_user.py
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core import security

def create_user(username, password, role="student", nickname=None):
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
            is_active=True
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
    u_name = input("请输入用户名: ")
    u_pass = input("请输入密码: ")
    u_role = input("请输入角色 (student/teacher): ")
    
    if u_role not in ["student", "teacher"]:
        u_role = "student"
        print("提示: 角色输入错误，默认为 student")
        
    create_user(u_name, u_pass, u_role)