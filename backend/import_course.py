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
SOURCE_DIR = r"D:\zkl\work\vue\2025教学系统研发课程资源\AI+(跨境)电商视觉营销设计"

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

    course_dir_rel = f"course_{course.id}"
    course_dir_abs = os.path.join(TARGET_ROOT, course_dir_rel)

    if os.path.exists(course_dir_abs):
        print(f"🧹 检测到旧文件目录，正在清理: {course_dir_abs}")
        try:
            # shutil.rmtree 会递归删除文件夹及其包含的所有内容
            shutil.rmtree(course_dir_abs)
            print("✅ 清理完成，准备写入新数据...")
        except Exception as e:
            print(f"❌ 清理旧文件失败: {e}")
            return

    # 2. 遍历章节 (一级文件夹)
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

        # 这里的逻辑修改了：不再合并 PDF 和 PPT，而是分别导入
        for f in files:
            name_without_ext, ext = os.path.splitext(f)
            ext = ext.lower()
            
            # --- 核心修改开始 ---
            
            # 1. 如果是 PPT 的预览版 PDF (以 _ppt.pdf 结尾)
            # 逻辑：只复制文件，不入库 (作为"影子"文件存在)
            if f.endswith("_ppt.pdf"):
                src_file = os.path.join(chapter_path, f)
                # 目标路径
                target_dir_rel = f"course_{course.id}/chapter_{chapter.id}"
                target_dir_abs = os.path.join(TARGET_ROOT, target_dir_rel)
                if not os.path.exists(target_dir_abs):
                    os.makedirs(target_dir_abs)
                
                dst_file = os.path.join(target_dir_abs, f)
                shutil.copy(src_file, dst_file)
                print(f"  📎 复制影子文件: {f} (不入库)")
                continue # 跳过数据库操作
            
            # 判断资源类型
            res_type = ''
            if ext == '.pdf':
                res_type = 'pdf'
            elif ext in ['.ppt', '.pptx']:
                res_type = 'ppt'
            elif ext in ['.mp4', '.mov']:
                res_type = 'video'
            else:
                continue # 跳过其他文件

            print(f"  📄 导入资源: {f} ({res_type})")

            # 复制文件
            src_file = os.path.join(chapter_path, f)
            dst_file = os.path.join(target_dir_abs, f)
            shutil.copy(src_file, dst_file)
            
            file_url = f"/{TARGET_ROOT}/{target_dir_rel}/{f}".replace("\\", "/")

            # 创建课时记录
            # 注意：如果是 PPT，我们也把它作为一个 Lesson 存进去
            # 这样在“课件资料”列表里就能查到了
            lesson = CourseLesson(
                chapter_id=chapter.id,
                title=name_without_ext, # 使用文件名作为标题
                resource_type=res_type,
                file_url=file_url,
                sort_order=0, # 排序可以后续调整，或者复用文件排序
                duration="15页" if res_type in ['pdf', 'ppt'] else "10:00"
            )
            db.add(lesson)
            
        db.commit()
    
    print("\n✅ 导入完成！")

if __name__ == "__main__":
    cid = input("请输入要导入的目标课程 ID: ")
    db = get_db()
    import_course(db, int(cid))