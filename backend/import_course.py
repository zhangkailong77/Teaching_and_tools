from app.core.redis import delete_cache_pattern  # 添加导入
import os
import shutil
import re
import subprocess
import json
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.profile import TeacherProfile, StudentProfile
from app.models.course import Class, Enrollment
from app.models.content import Course, CourseChapter, CourseLesson

# 配置：你的本地源文件夹路径
SOURCE_DIR = "/Users/zhangkailong/Documents/zkl7788/课程资源开发/comfyui/上传到系统的版本/"

# 配置：目标存储路径 (后端静态目录)
TARGET_ROOT = "static/uploads/materials"
INTERACTIVE_ROOT = "static/interactive"
INTERACTIVE_MANIFEST_PATH = Path(INTERACTIVE_ROOT) / "manifest.json"

def get_db():
    return SessionLocal()

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]


def probe_video_duration_text(file_path: str) -> str:
    """使用 ffprobe 读取视频时长，返回 mm:ss。失败时回退到 10:00。"""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        raw = (result.stdout or "").strip()
        seconds = float(raw)
        if seconds <= 0:
            return "10:00"
        total_seconds = int(round(seconds))
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins}:{secs:02d}"
    except Exception:
        return "10:00"


def load_manifest() -> dict:
    if not INTERACTIVE_MANIFEST_PATH.exists():
        return {"courses": {}}
    try:
        with INTERACTIVE_MANIFEST_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"courses": {}}


def save_manifest(manifest: dict):
    INTERACTIVE_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INTERACTIVE_MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def find_interactive_dist_for_lesson(chapter_path: str, lesson_title: str) -> Optional[str]:
    """
    约定优先级（每个课时一个 dist）：
    1) {chapter}/{课时名}/dist/index.html
    2) {chapter}/{课时名}/index.html
    3) {chapter}/{课时名}_interactive/dist/index.html
    """
    candidates = [
        os.path.join(chapter_path, lesson_title, "dist"),
        os.path.join(chapter_path, lesson_title),
        os.path.join(chapter_path, f"{lesson_title}_interactive", "dist"),
    ]
    for path in candidates:
        if os.path.isfile(os.path.join(path, "index.html")):
            return path
    return None

def normalize_dist_index_paths(dist_dir: str):
    """
    将 dist/index.html 中绝对资源路径改为相对路径，避免挂载在子路径下时 404。
    例如:
      /assets/xxx.js -> ./assets/xxx.js
    """
    index_path = os.path.join(dist_dir, "index.html")
    if not os.path.isfile(index_path):
        return
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()
        updated = html
        replacements = [
            ('src="/assets/', 'src="./assets/'),
            ('href="/assets/', 'href="./assets/'),
            ("src='/assets/", "src='./assets/"),
            ("href='/assets/", "href='./assets/"),
            ('src=/assets/', 'src=./assets/'),
            ('href=/assets/', 'href=./assets/'),
        ]
        for old, new in replacements:
            updated = updated.replace(old, new)
        if updated != html:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"  🔧 已修正 dist 资源路径: {index_path}")
    except Exception as e:
        print(f"  ⚠️ 修正 dist 路径失败: {index_path}, {e}")


def write_lesson_interactive_entry(manifest: dict, course_id: int, lesson_id: int, version: str, entry_rel: str):
    courses = manifest.setdefault("courses", {})
    course_data = courses.setdefault(str(course_id), {})
    app_data = course_data.setdefault("ppt-test", {})
    app_data["version"] = version
    # 课程级默认入口：首次写入时自动设置，便于课程级 fallback
    if not app_data.get("entry"):
        app_data["entry"] = entry_rel
    lessons = app_data.setdefault("lessons", {})
    lessons[str(lesson_id)] = {
        "version": version,
        "entry": entry_rel
    }

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

    # 清理该课程旧交互资源目录（可选但推荐）
    interactive_course_abs = os.path.join(INTERACTIVE_ROOT, str(course.id))
    if os.path.exists(interactive_course_abs):
        print(f"🧹 检测到旧交互资源目录，正在清理: {interactive_course_abs}")
        try:
            shutil.rmtree(interactive_course_abs)
            print("✅ 旧交互资源清理完成...")
        except Exception as e:
            print(f"❌ 清理旧交互资源失败: {e}")
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
        # ✅ 清除课程章节缓存，确保数据立即更新
        delete_cache_pattern(f"course:{course.id}:chapters")
        print("✅ 数据库旧记录清理完成，缓存已清除")
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
    manifest = load_manifest()
    # 重置该课程的 ppt-test 映射，避免脏数据
    courses = manifest.setdefault("courses", {})
    course_manifest = courses.setdefault(str(course.id), {})
    course_manifest["ppt-test"] = {"version": "v1.0.0", "lessons": {}}
    
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
            duration = "15页" if res_type in ['pdf', 'ppt'] else probe_video_duration_text(dst_file)
            lesson = CourseLesson(
                chapter_id=chapter.id,
                title=name_without_ext,
                resource_type=res_type,
                file_url=file_url,
                sort_order=0,
                duration=duration
            )
            db.add(lesson)
            db.flush()  # 立即拿到 lesson.id，便于写交互映射

            # 仅视频课时尝试导入交互式 dist
            if res_type == 'video':
                interactive_src = find_interactive_dist_for_lesson(chapter_path, name_without_ext)
                if interactive_src:
                    version = "v1.0.0"
                    interactive_target_rel = f"interactive/{course.id}/ppt-test/lesson_{lesson.id}/{version}"
                    interactive_target_abs = os.path.join(INTERACTIVE_ROOT, str(course.id), "ppt-test", f"lesson_{lesson.id}", version)
                    os.makedirs(interactive_target_abs, exist_ok=True)
                    shutil.copytree(interactive_src, interactive_target_abs, dirs_exist_ok=True)
                    normalize_dist_index_paths(interactive_target_abs)

                    entry_rel = f"{interactive_target_rel}/index.html"
                    write_lesson_interactive_entry(
                        manifest=manifest,
                        course_id=course.id,
                        lesson_id=lesson.id,
                        version=version,
                        entry_rel=entry_rel
                    )
                    print(f"  🧩 绑定交互课件: lesson={lesson.id} -> {entry_rel}")
                else:
                    print(f"  ⚠️ 未找到课时交互 dist: {name_without_ext} (跳过)")
            
        db.commit()
    save_manifest(manifest)
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
