import sys
import os
import shutil
import uuid
from datetime import datetime

# 引入数据库依赖
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

# ✅ 核心修复：导入所有模型类，解决 SQLAlchemy 的映射依赖问题
from app.models.user import User 
from app.models.profile import TeacherProfile  # <--- 必须导这个，User 依赖它
from app.models.course import Class, Enrollment # <--- Class 依赖 User，Enrollment 依赖两者
from app.models.content import Course, ClassCourseBinding # <--- 你的目标模型

# 配置图片存储路径 (与 uploader.py 保持一致)
UPLOAD_DIR_REL = "static/uploads/courses"  # 数据库存的相对路径中间部分
UPLOAD_ROOT = os.path.join("static", "uploads", "courses") # 物理路径

def get_db():
    return SessionLocal()

def list_courses(db: Session):
    """列出所有课程"""
    courses = db.query(Course).all()
    print("\n" + "="*60)
    print(f"{'ID':<5} | {'名称':<30} | {'简介 (前20字)'}")
    print("-" * 60)
    for c in courses:
        intro = (c.intro[:20] + '...') if c.intro else '无'
        print(f"{c.id:<5} | {c.name:<30} | {intro}")
    print("="*60 + "\n")

def handle_image_upload(input_path):
    """
    更严谨的图片处理逻辑
    """
    if not input_path:
        return None
        
    # 去除引号和首尾空格
    input_path = input_path.strip().strip('"').strip("'")
    
    # --- 情况 A: 网络图片 ---
    if input_path.startswith("http"):
        return input_path
    
    # --- 情况 B: 纯文件名复用 (仅当输入不含路径斜杠时) ---
    # 判断标准：输入的内容里不包含 \ 也不包含 /
    if "\\" not in input_path and "/" not in input_path:
        potential_existing_path = os.path.join(UPLOAD_ROOT, input_path)
        if os.path.exists(potential_existing_path):
            print(f"✅ 检测到图片已存在于库中，直接复用。")
            return f"/{UPLOAD_DIR_REL}/{input_path}".replace("\\", "/")
        else:
            print(f"⚠️ 文件名 {input_path} 不在 {UPLOAD_ROOT} 中")
            return None

    # --- 情况 C: 本地绝对/相对路径 (上传并重命名) ---
    if os.path.exists(input_path):
        if not os.path.exists(UPLOAD_ROOT):
            os.makedirs(UPLOAD_ROOT)
        
        # 生成规范的 UUID 文件名
        ext = os.path.splitext(input_path)[1].lower()
        if not ext: ext = ".png"
        new_filename = f"{uuid.uuid4()}{ext}"
        
        # 物理保存路径
        dest_path = os.path.join(UPLOAD_ROOT, new_filename)
        
        try:
            shutil.copy(input_path, dest_path)
            print(f"✅ 图片已成功导入并重新编码为: {new_filename}")
            # 返回标准的相对路径供数据库存储
            return f"/{UPLOAD_DIR_REL}/{new_filename}".replace("\\", "/")
        except Exception as e:
            print(f"❌ 图片处理失败: {e}")
            return None
    else:
        print(f"❌ 找不到指定的本地文件路径，请检查路径是否正确。")
        return None

# 这里修正一下路径拼接，防止上面函数里的 UPLOAD_DIR 未定义
UPLOAD_DIR = "static/uploads/courses" 

def edit_course(db: Session):
    """编辑课程逻辑"""
    try:
        cid = input("请输入要修改的课程 ID: ").strip()
        course = db.query(Course).filter(Course.id == cid).first()
        
        if not course:
            print("❌ 未找到该课程！")
            return

        print(f"\n正在编辑: 【{course.name}】")
        print("提示：如果不修改某项，直接按回车跳过")
        
        # 1. 修改名称
        new_name = input(f"新名称 (原: {course.name}): ").strip()
        if new_name:
            course.name = new_name
            
        # 2. 修改简介
        new_intro = input(f"新简介 (原: {course.intro or '空'}): ").strip()
        if new_intro:
            course.intro = new_intro
            
        # 3. 修改封面 (核心功能)
        print(f"当前封面: {course.cover}")
        img_input = input("新封面 (输入本地图片路径 或 网络URL): ").strip()
        
        new_cover_path = handle_image_upload(img_input)
        if new_cover_path:
            course.cover = new_cover_path

        # 提交保存
        db.commit()
        print("\n✅ 修改成功！")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")

def create_new_course(db: Session):
    """创建新课程"""
    print("\n--- 新建课程 ---")
    name = input("课程名称 (必填): ").strip()
    if not name:
        print("名称不能为空")
        return
        
    intro = input("课程简介: ").strip()
    
    img_input = input("封面图片 (本地路径/URL): ").strip()
    cover = handle_image_upload(img_input)
    
    # 假设管理员 ID 为 1 或者 2，这里暂时写死为第一个用户，或者你手动指定
    # 既然是管理员脚本，owner_id 主要是为了外键约束，不影响展示
    owner_id = 2 # 你的教师ID，或者改成 input 输入
    
    new_course = Course(
        name=name,
        intro=intro,
        cover=cover,
        owner_id=owner_id
    )
    db.add(new_course)
    db.commit()
    print(f"✅ 课程【{name}】创建成功！")

def main():
    db = get_db()
    while True:
        print("\n--- 课程资源管理器 (管理员版) ---")
        print("1. 查看所有课程")
        print("2. 修改课程信息 (封面/名称/简介)")
        print("3. 新建课程")
        print("q. 退出")
        
        choice = input("请选择操作: ").strip().lower()
        
        if choice == '1':
            list_courses(db)
        elif choice == '2':
            edit_course(db)
        elif choice == '3':
            create_new_course(db)
        elif choice == 'q':
            break
        else:
            print("无效输入")
    
    db.close()

if __name__ == "__main__":
    main()