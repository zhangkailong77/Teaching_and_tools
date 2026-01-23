import os
import shutil
import re
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.profile import TeacherProfile, StudentProfile
from app.models.course import Class, Enrollment
from app.models.content import Course, CourseChapter, CourseLesson

# 配置：你的本地源文件夹路径
SOURCE_DIR = r"D:\zkl\work\vue\2025教学系统研发课程资源\tiktok"

# 配置：目标存储路径 (后端静态目录)
TARGET_ROOT = "static/uploads/materials"

def get_db():
    return SessionLocal()

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def import_course(db: Session, course_id: int):
    # 1. 查找课程
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        print(f"❌ 课程 ID {course_id} 不存在！")
        return

    print(f"🚀 开始为课程【{course.name}】导入资源...")

    # --- 文件清理 (保持不变) ---
    course_dir_rel = f"course_{course.id}"
    course_dir_abs = os.path.join(TARGET_ROOT, course_dir_rel)

    if os.path.exists(course_dir_abs):
        print(f"🧹 检测到旧文件目录，正在清理: {course_dir_abs}")
        try:
            shutil.rmtree(course_dir_abs)
            print("✅ 文件清理完成...")
        except Exception as e:
            print(f"❌ 清理旧文件失败: {e}")
            return

    # --- ✅ 新增：数据库清理 (解决重复显示问题) ---
    print(f"🧹 正在清理数据库旧记录 (课程ID: {course.id})...")
    try:
        # 删除该课程下的所有章节
        # 注意：因为 CourseLesson 外键关联了 CourseChapter，
        # 如果数据库设置了 ON DELETE CASCADE，删章节会自动删课时。
        # 如果没设置，SQLAlchemy 的 cascade="all, delete-orphan" 也会处理。
        # 为了保险，这里直接删除章节即可。
        db.query(CourseChapter).filter(CourseChapter.course_id == course.id).delete()
        db.commit()
        print("✅ 数据库旧记录清理完成")
    except Exception as e:
        print(f"❌ 数据库清理失败: {e}")
        db.rollback()
        return
    # ---------------------------------------------

    # 2. 遍历章节 (一级文件夹)
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 源路径不存在: {SOURCE_DIR}")
        return

    chapters = sorted(os.listdir(SOURCE_DIR), key=natural_sort_key)
    
    for chapter_idx, chapter_name in enumerate(chapters):
        chapter_path = os.path.join(SOURCE_DIR, chapter_name)
        if not os.path.isdir(chapter_path): continue
        
        print(f"\n📂 处理章节: {chapter_name}")
        
        # 创建章节记录
        chapter = CourseChapter(
            course_id=course.id,
            title=chapter_name,
            sort_order=chapter_idx + 1
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

        # 3. 遍历课时 (文件)
        files = sorted(os.listdir(chapter_path), key=natural_sort_key)
        
        # 目标文件夹
        target_dir_rel = f"course_{course.id}/chapter_{chapter.id}"
        target_dir_abs = os.path.join(TARGET_ROOT, target_dir_rel)
        if not os.path.exists(target_dir_abs):
            os.makedirs(target_dir_abs)

        for f in files:
            name_without_ext, ext = os.path.splitext(f)
            ext = ext.lower()
            
            # 1. 影子文件处理
            if f.endswith("_ppt.pdf"):
                src_file = os.path.join(chapter_path, f)
                # 目标路径
                dst_file = os.path.join(target_dir_abs, f)
                shutil.copy(src_file, dst_file)
                print(f"  📎 复制影子文件: {f} (不入库)")
                continue 
            
            # 判断资源类型
            res_type = ''
            if ext == '.pdf':
                res_type = 'pdf'
            elif ext in ['.ppt', '.pptx']:
                res_type = 'ppt'
            elif ext in ['.mp4', '.mov']:
                res_type = 'video'
            else:
                continue 

            print(f"  📄 导入资源: {f} ({res_type})")

            # 复制文件
            src_file = os.path.join(chapter_path, f)
            dst_file = os.path.join(target_dir_abs, f)
            shutil.copy(src_file, dst_file)
            
            file_url = f"/{TARGET_ROOT}/{target_dir_rel}/{f}".replace("\\", "/")

            # 创建课时记录
            lesson = CourseLesson(
                chapter_id=chapter.id,
                title=name_without_ext,
                resource_type=res_type,
                file_url=file_url,
                sort_order=0,
                duration="15页" if res_type in ['pdf', 'ppt'] else "10:00"
            )
            db.add(lesson)
            
        db.commit()
    
    print("\n✅ 导入完成！")

if __name__ == "__main__":
    db = get_db()
    
    print("\n📚 当前系统已有的课程列表：")
    print("-" * 50)
    
    # 1. 查询所有课程
    courses = db.query(Course).all()
    
    if not courses:
        print("  (暂无课程，请先确保数据库 courses 表有数据)")
    else:
        for c in courses:
            # 打印 ID 和 课程名
            print(f"  [ID: {c.id}] {c.name}")
            
    print("-" * 50)

    # 2. 再让用户输入
    cid = input("👉 请输入要导入的目标课程 ID: ")
    
    if cid.isdigit():
        import_course(db, int(cid))
    else:
        print("❌ 输入错误，请输入数字 ID")