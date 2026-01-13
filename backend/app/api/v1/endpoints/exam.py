import pandas as pd
import io
from fastapi import UploadFile, File
import random
from datetime import datetime, timedelta

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models import exam as models
from app.schemas import exam as schemas
from app.models.user import User
from sqlalchemy import func, cast, String
from app.schemas.exam import QuestionPagination
from app.models.course import Class, Enrollment

router = APIRouter()

# 1. 获取题目列表 (支持筛选)
@router.get("/questions", response_model=QuestionPagination)
def read_questions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    type: Optional[str] = None,
    difficulty: Optional[int] = None,
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    # 1. 构建基础查询
    query = db.query(models.Question).filter(models.Question.teacher_id == current_user.id)
    
    # 2. 应用筛选条件
    if type:
        query = query.filter(models.Question.type == type)
    if difficulty:
        query = query.filter(models.Question.difficulty == difficulty)
        
    # 3. ✅ 应用关键字搜索 (模糊匹配题干)
    if keyword:
        # 使用 ilike (不区分大小写) 或 like
        # 注意：这里主要搜题干，如果你想搜解析也可以加 or_
        query = query.filter(models.Question.content.like(f"%{keyword}%"))

    if tag:
        query = query.filter(cast(models.Question.tags, String).like(f'%{tag}%'))

    # 4. ✅ 计算总数 (用于分页)
    total = query.count()
        
    # 5. 分页与排序
    questions = query.order_by(models.Question.created_at.desc()).offset(skip).limit(limit).all()
    
    # 6. 返回特定结构
    return {
        "total": total,
        "items": questions
    }


# 获取题库统计信息 (Dashboard用)
@router.get("/questions/stats")
def get_question_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 基础查询对象
    base_query = db.query(models.Question).filter(models.Question.teacher_id == current_user.id)
    
    # 1. 总题数
    total = base_query.count()
    
    # 2. 按题型统计
    # SQL: SELECT type, count(*) FROM questions WHERE ... GROUP BY type
    type_stats = db.query(
        models.Question.type, 
        func.count(models.Question.id)
    ).filter(
        models.Question.teacher_id == current_user.id
    ).group_by(models.Question.type).all()
    
    # 转为字典: {'single': 10, 'multiple': 5 ...}
    type_counts = {t[0]: t[1] for t in type_stats}
    
    # 3. 按难度统计
    diff_stats = db.query(
        models.Question.difficulty, 
        func.count(models.Question.id)
    ).filter(
        models.Question.teacher_id == current_user.id
    ).group_by(models.Question.difficulty).all()
    
    diff_counts = {d[0]: d[1] for d in diff_stats} # {1: 5, 2: 10...}

    return {
        "total": total,
        "type_counts": type_counts,
        "difficulty_counts": diff_counts
    }


# -----------------------------------------------------------
# 获取所有已使用的标签 (用于前端下拉筛选)
# -----------------------------------------------------------
@router.get("/questions/tags", response_model=List[str])
def get_all_tags(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 查询该老师所有题目的 tags 字段
    # 注意：这在数据量极大时可能效率一般，但在教学系统中完全够用
    all_questions = db.query(models.Question.tags).filter(
        models.Question.teacher_id == current_user.id
    ).all()
    
    # 提取并去重
    unique_tags = set()
    for q in all_questions:
        if q.tags: # q.tags 是一个 list
            for t in q.tags:
                unique_tags.add(t)
                
    return list(unique_tags)


# -----------------------------------------------------------
# 批量删除
# -----------------------------------------------------------
@router.post("/questions/batch-delete")
def batch_delete_questions(
    ids: List[int], # 接收 ID 列表
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 批量删除属于该老师的指定 ID 题目
    stmt = db.query(models.Question).filter(
        models.Question.id.in_(ids),
        models.Question.teacher_id == current_user.id
    )
    count = stmt.delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {count} 道题目"}

# 2. 创建题目
@router.post("/questions", response_model=schemas.QuestionOut)
def create_question(
    *,
    db: Session = Depends(deps.get_db),
    question_in: schemas.QuestionCreate,
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")

    processed_options = [opt.dict() for opt in question_in.options] if question_in.options else []

    db_obj = models.Question(
        teacher_id=current_user.id,
        type=question_in.type,
        content=question_in.content,
        options=processed_options, # Pydantic 会自动转为 JSON 存入
        answer=question_in.answer,
        analysis=question_in.analysis,
        difficulty=question_in.difficulty,
        tags=question_in.tags
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# 3. 删除题目
@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    if question.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除他人的题目")
        
    db.delete(question)
    db.commit()
    return {"message": "删除成功"}

# 4. 获取题目详情 (用于编辑回显)
@router.get("/questions/{question_id}", response_model=schemas.QuestionOut)
def read_question_detail(
    question_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question

# 5. 更新题目
@router.put("/questions/{question_id}", response_model=schemas.QuestionOut)
def update_question(
    question_id: int,
    question_in: schemas.QuestionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    processed_options = [opt.dict() for opt in question_in.options] if question_in.options else []
    
    # 更新字段
    question.type = question_in.type
    question.content = question_in.content
    question.options = processed_options
    question.answer = question_in.answer
    question.analysis = question_in.analysis
    question.difficulty = question_in.difficulty
    question.tags = question_in.tags
    
    db.commit()
    db.refresh(question)
    return question



# 6. 批量导入题目
@router.post("/questions/batch")
def batch_import_questions(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="权限不足")

    try:
        contents = file.file.read()
        df = pd.read_excel(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="文件格式错误，请上传标准的 .xlsx 文件")

    # 1. 题型映射字典
    type_map = {
        "单选题": "single",
        "多选题": "multiple",
        "判断题": "judge",
        "填空题": "blank",
        "简答题": "essay"
    }

    # 2. 字段校验 (对应模板列名)
    # 选项列支持到 G (7个)
    option_cols = ['选项A', '选项B', '选项C', '选项D', '选项E', '选项F', '选项G']
    required_columns = ['题型', '题干', '正确答案']
    
    if not set(required_columns).issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"模板错误，必须包含：{required_columns}")

    df = df.fillna("") # 将空值替换为空字符串
    success_count = 0
    errors = []

    for index, row in df.iterrows():
        row_num = index + 2
        try:
            q_type_cn = str(row['题型']).strip()
            if q_type_cn not in type_map:
                errors.append(f"第{row_num}行：不支持的题型【{q_type_cn}】")
                continue
            
            q_type = type_map[q_type_cn]
            content = str(row['题干']).strip()
            raw_answer = str(row['正确答案']).strip()
            
            # --- 选项解析 (仅针对选择题) ---
            processed_options = []
            if q_type in ["single", "multiple"]:
                for i, col in enumerate(option_cols):
                    if col in row and str(row[col]).strip():
                        processed_options.append({
                            "label": chr(65 + i), # A, B, C...
                            "text": str(row[col]).strip()
                        })
                if not processed_options:
                    errors.append(f"第{row_num}行：选择题缺少选项内容")
                    continue

            # --- 答案解析 ---
            final_answer = raw_answer
            if q_type == "multiple":
                # 多选题支持 A,B,C 或 ABC 或 A B C 等分隔符
                import re
                final_answer = re.findall(r'[A-G]', raw_answer.upper())
            elif q_type == "judge":
                # 判断题：对/正确/True -> True
                final_answer = True if raw_answer in ["对", "正确", "True", "T", "1"] else False

            # --- 难度解析 ---
            diff_val = 1
            if '难度' in row:
                diff_str = str(row['难度']).strip()
                if "中" in diff_str or "2" in diff_str: diff_val = 2
                if "难" in diff_str or "3" in diff_str: diff_val = 3

            # --- 标签解析 ---
            tags = []
            if '知识点' in row and str(row['知识点']).strip():
                tags = [t.strip() for t in str(row['知识点']).split(',')]

            # --- 写入数据库 ---
            new_q = models.Question(
                teacher_id=current_user.id,
                type=q_type,
                content=content,
                options=processed_options,
                answer=final_answer,
                analysis=str(row.get('解析', '')).strip(),
                difficulty=diff_val,
                tags=tags
            )
            db.add(new_q)
            success_count += 1

        except Exception as e:
            errors.append(f"第{row_num}行：解析异常 - {str(e)}")

    db.commit()
    return {
        "total": len(df),
        "success": success_count,
        "fail": len(errors),
        "logs": errors
    }


# -----------------------------------------------------------
# 创建试卷 (核心接口)
# -----------------------------------------------------------
@router.post("/exams", response_model=schemas.ExamListOut)
def create_exam(
    *,
    db: Session = Depends(deps.get_db),
    exam_in: schemas.ExamCreate,
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 创建试卷主体
    exam = models.Exam(
        title=exam_in.title,
        teacher_id=current_user.id,
        mode=exam_in.mode,
        duration=exam_in.duration,
        pass_score=exam_in.pass_score,
        start_time=exam_in.start_time,
        end_time=exam_in.end_time,
        class_ids=exam_in.class_ids,
        status=1 # 默认为草稿
    )
    db.add(exam)
    db.flush() #以此获得 exam.id

    real_total_score = 0
    question_count = 0

    # 2. 处理手动组卷
    if exam_in.mode == 1:
        for index, item in enumerate(exam_in.questions):
            link = models.ExamQuestion(
                exam_id=exam.id,
                question_id=item.question_id,
                score=item.score,
                sort_order=index
            )
            db.add(link)
            real_total_score += item.score
            question_count += 1

    # 3. 处理随机组卷
    elif exam_in.mode == 2:
        # 保存策略配置
        # 注意：这里需要把 Pydantic list 转为 dict list 存入 JSON
        exam.random_config = [c.dict() for c in exam_in.random_config]
        
        for strategy in exam_in.random_config:
            # 根据策略查询符合条件的题目 ID
            query = db.query(models.Question.id).filter(
                models.Question.teacher_id == current_user.id,
                models.Question.type == strategy.type,
                models.Question.difficulty == strategy.difficulty
            )
            if strategy.tag:
                query = query.filter(cast(models.Question.tags, String).like(f'%{strategy.tag}%'))
            
            candidate_ids = [q[0] for q in query.all()]
            
            # 随机抽取
            if len(candidate_ids) < strategy.count:
                # 题目不够，直接抛错或者取最大值？建议抛错让老师知道
                raise HTTPException(status_code=400, detail=f"题库不足：{strategy.type} 难度{strategy.difficulty} 只有 {len(candidate_ids)} 题，无法抽取 {strategy.count} 题")
            
            selected_ids = random.sample(candidate_ids, strategy.count)
            
            # 写入关联表
            for q_id in selected_ids:
                link = models.ExamQuestion(
                    exam_id=exam.id,
                    question_id=q_id,
                    score=strategy.score,
                    sort_order=question_count # 简单累加排序
                )
                db.add(link)
                real_total_score += strategy.score
                question_count += 1

    # 更新总分
    exam.total_score = real_total_score
    db.commit()
    db.refresh(exam)
    
    # 构造返回 (手动补充 question_count)
    result = schemas.ExamListOut.from_orm(exam)
    result.question_count = question_count
    return result

# -----------------------------------------------------------
# 获取试卷列表
# -----------------------------------------------------------
@router.get("/exams", response_model=List[schemas.ExamListOut])
def read_exams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    exams = db.query(models.Exam).filter(models.Exam.teacher_id == current_user.id).order_by(models.Exam.created_at.desc()).all()
    
    results = []
    for e in exams:
        # 统计题目数
        q_count = db.query(models.ExamQuestion).filter(models.ExamQuestion.exam_id == e.id).count()

        c_names = []
        if e.class_ids:
            # 查询对应的班级名
            class_objs = db.query(Class.name).filter(Class.id.in_(e.class_ids)).all()
            c_names = [c[0] for c in class_objs]
        
        # Pydantic 转换
        item = schemas.ExamListOut.from_orm(e)
        item.question_count = q_count
        item.class_names = c_names
        results.append(item)
        
    return results


# -----------------------------------------------------------
# 删除试卷
# -----------------------------------------------------------
@router.delete("/exams/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    exam = db.query(models.Exam).filter(
        models.Exam.id == exam_id, 
        models.Exam.teacher_id == current_user.id
    ).first()
    
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在或无权操作")
        
    db.delete(exam)
    db.commit()
    return {"message": "试卷已删除"}


# 获取试卷详情 (用于编辑回显)
@router.get("/exams/{exam_id}", response_model=schemas.ExamDetailOut)
def read_exam_detail(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    
    # 1. 查找关联题目
    q_links = db.query(models.ExamQuestion).filter(models.ExamQuestion.exam_id == exam.id).order_by(models.ExamQuestion.sort_order).all()
    
    # 2. 组装题目数据，手动将 Model 转为 Dict 以免序列化报错
    question_list = []
    for link in q_links:
        q = link.question
        question_list.append({
            "id": q.id,
            "question_id": q.id,
            "score": link.score,
            "title": q.content,
            "raw": {
                "id": q.id,
                "type": q.type,
                "content": q.content,
                "options": q.options, # JSON 字段直接赋值
                "answer": q.answer,
                "analysis": q.analysis,
                "difficulty": q.difficulty,
                "tags": q.tags
            }
        })
    
    # 3. 获取班级名称 (详情页也需要显示)
    c_names = []
    if exam.class_ids:
        class_objs = db.query(Class.name).filter(Class.id.in_(exam.class_ids)).all()
        c_names = [c[0] for c in class_objs]
    
    # 4. 构造并返回
    return {
        "id": exam.id,
        "title": exam.title,
        "status": exam.status,
        "mode": exam.mode,
        "duration": exam.duration,
        "pass_score": exam.pass_score,
        "total_score": exam.total_score,
        "start_time": exam.start_time,
        "end_time": exam.end_time,
        "class_ids": exam.class_ids or [],
        "class_names": c_names,
        "questions": question_list,
        "random_config": exam.random_config or [],
        "created_at": exam.created_at
    }

# 更新试卷 (PUT)
@router.put("/exams/{exam_id}")
def update_exam(
    exam_id: int,
    exam_in: schemas.ExamCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    exam_obj = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam_obj:
        raise HTTPException(status_code=404, detail="试卷不存在")
        
    # 1. 更新主表基本信息
    exam_obj.title = exam_in.title
    exam_obj.duration = exam_in.duration
    exam_obj.pass_score = exam_in.pass_score
    exam_obj.total_score = exam_in.total_score
    exam_obj.start_time = exam_in.start_time
    exam_obj.end_time = exam_in.end_time
    exam_obj.class_ids = exam_in.class_ids
    
    # 2. 更新题目关联（先删后增最简单）
    db.query(models.ExamQuestion).filter(models.ExamQuestion.exam_id == exam_id).delete()
    
    if exam_in.mode == 1:
        for index, item in enumerate(exam_in.questions):
            link = models.ExamQuestion(
                exam_id=exam_id,
                question_id=item.question_id,
                score=item.score,
                sort_order=index
            )
            db.add(link)
    
    db.commit()
    return {"message": "更新成功"}



# -----------------------------------------------------------
# [学生端]
# -----------------------------------------------------------
# -----------------------------------------------------------
# [学生端] 获取我的考试列表
# -----------------------------------------------------------
@router.get("/student/list", response_model=List[schemas.StudentExamOut])
def get_student_exams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可访问")

    # 1. 找到学生所在的班级 ID
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    class_ids = [e.class_id for e in enrollments]

    if not class_ids:
        return []

    # 2. 查询发布给这些班级的考试
    # 使用 SQLAlchemy 的 JSON 包含逻辑，或者简单遍历（这里采用兼容性好的过滤逻辑）
    # 注意：这里假设 exams 表的 class_ids 存储的是 ID 列表
    all_exams = db.query(models.Exam).filter(models.Exam.status >= 1).all()
    
    results = []
    for exam in all_exams:
        # 检查考试是否发布给该学生的班级
        if not exam.class_ids or not any(cid in exam.class_ids for cid in class_ids):
            continue
            
        # 3. 查找该学生对该考试的参与记录
        record = db.query(models.ExamRecord).filter(
            models.ExamRecord.exam_id == exam.id,
            models.ExamRecord.student_id == current_user.id
        ).first()

        item = schemas.StudentExamOut.from_orm(exam)
        if record:
            item.my_status = record.status
            item.my_score = record.total_score if record.status == 2 else None
        else:
            item.my_status = -1 # 未开始
            
        results.append(item)
    
    return results

# -----------------------------------------------------------
# [学生端] 开始/进入考试 (创建或获取记录)
# -----------------------------------------------------------
@router.post("/student/enter/{exam_id}")
def enter_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    # 时间校验
    now = datetime.now()
    if exam.start_time and now < exam.start_time:
        raise HTTPException(status_code=400, detail="考试尚未开始")
    if exam.end_time and now > exam.end_time:
        raise HTTPException(status_code=400, detail="考试已结束入口")

    # 查找是否有进行中或已完成的记录
    record = db.query(models.ExamRecord).filter(
        models.ExamRecord.exam_id == exam_id,
        models.ExamRecord.student_id == current_user.id
    ).first()

    if not record:
        # 创建新记录
        record = models.ExamRecord(
            exam_id=exam_id,
            student_id=current_user.id,
            status=0 # 进行中
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    
    return {"record_id": record.id, "status": record.status}

# -----------------------------------------------------------
# [学生端] 获取试卷题目内容 (不含正确答案！)
# -----------------------------------------------------------
@router.get("/student/paper/{exam_id}")
def get_exam_paper(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 逻辑：获取该考试关联的所有题目，但过滤掉答案和解析字段
    q_links = db.query(models.ExamQuestion).filter(
        models.ExamQuestion.exam_id == exam_id
    ).order_by(models.ExamQuestion.sort_order).all()
    
    paper_questions = []
    for link in q_links:
        q = link.question
        paper_questions.append({
            "id": q.id,
            "type": q.type,
            "content": q.content,
            "options": q.options, # 选项是公开的
            "score": link.score,
            "sort_order": link.sort_order
        })
        
    return paper_questions

# -----------------------------------------------------------
# [学生端] 提交试卷并自动判分 (核心逻辑)
# -----------------------------------------------------------
@router.post("/student/submit/{exam_id}")
def submit_exam(
    exam_id: int,
    submit_in: schemas.ExamSubmit,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 1. 找到考试记录
    record = db.query(models.ExamRecord).filter(
        models.ExamRecord.exam_id == exam_id,
        models.ExamRecord.student_id == current_user.id,
        models.ExamRecord.status == 0
    ).first()
    
    if not record:
        raise HTTPException(status_code=400, detail="未找到进行中的考试记录")

    objective_score = 0
    
    # 2. 遍历学生提交的答案
    for ans in submit_in.answers:
        # 获取题目详情（包含正确答案）
        question = db.query(models.Question).filter(models.Question.id == ans.question_id).first()
        # 获取该题在试卷中的分值
        q_link = db.query(models.ExamQuestion).filter(
            models.ExamQuestion.exam_id == exam_id,
            models.ExamQuestion.question_id == ans.question_id
        ).first()
        
        if not question or not q_link: continue

        is_correct = False
        earned_score = 0

        # --- 自动判分逻辑 ---
        if question.type in ["single", "judge"]:
            # 单选和判断：完全匹配
            if str(ans.answer_content) == str(question.answer):
                is_correct = True
                earned_score = q_link.score
                
        elif question.type == "multiple":
            # 多选：集合对比 (必须完全一致)
            if set(ans.answer_content) == set(question.answer):
                is_correct = True
                earned_score = q_link.score

        # 3. 记录到答题明细表
        db_ans = models.ExamAnswer(
            record_id=record.id,
            question_id=ans.question_id,
            answer_content=ans.answer_content,
            is_correct=is_correct,
            score=earned_score
        )
        db.add(db_ans)
        
        if question.type in ["single", "multiple", "judge"]:
            objective_score += earned_score

    # 4. 更新记录状态
    record.status = 1 # 已提交
    record.submit_time = datetime.now()
    record.objective_score = objective_score
    record.total_score = objective_score # 初始总分为客观题分，主观题批改后再加
    record.cheat_count = submit_in.cheat_count
    
    db.commit()
    return {"message": "交卷成功", "score": objective_score}


# [学生端] 暂存答案 (断电保护/每30秒触发)
@router.post("/student/save-progress/{exam_id}")
def save_exam_progress(
    exam_id: int,
    answers: List[schemas.AnswerSubmit],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # 找到记录
    record = db.query(models.ExamRecord).filter(
        models.ExamRecord.exam_id == exam_id,
        models.ExamRecord.student_id == current_user.id,
        models.ExamRecord.status == 0
    ).first()
    
    if not record:
        return {"msg": "无正在进行的考试记录"}

    # 批量更新或插入答案
    for ans in answers:
        # 查找是否已存在该题作答
        db_ans = db.query(models.ExamAnswer).filter(
            models.ExamAnswer.record_id == record.id,
            models.ExamAnswer.question_id == ans.question_id
        ).first()
        
        if db_ans:
            db_ans.answer_content = ans.answer_content
        else:
            new_ans = models.ExamAnswer(
                record_id=record.id,
                question_id=ans.question_id,
                answer_content=ans.answer_content
            )
            db.add(new_ans)
    
    db.commit()
    return {"status": "success", "saved_at": datetime.now()}