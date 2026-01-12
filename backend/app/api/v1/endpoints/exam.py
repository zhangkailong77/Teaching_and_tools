import pandas as pd
import io
from fastapi import UploadFile, File

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models import exam as models
from app.schemas import exam as schemas
from app.models.user import User
from sqlalchemy import func, cast, String
from app.schemas.exam import QuestionPagination

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


