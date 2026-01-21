import redis
import json
import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=redis_pool)


def get_cache(key: str) -> Optional[Any]:
    """获取缓存"""
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Redis读取失败: {e}")
    return None


def set_cache(key: str, value: Any, expire: int = 300) -> bool:
    """设置缓存"""
    try:
        redis_client.setex(key, expire, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.warning(f"Redis写入失败: {e}")
        return False


def delete_cache(key: str) -> bool:
    """删除缓存"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis删除失败: {e}")
        return False


def delete_cache_pattern(pattern: str) -> int:
    """删除匹配模式的所有缓存"""
    try:
        count = 0
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
            count += 1
        return count
    except Exception as e:
        logger.warning(f"Redis批量删除失败: {e}")
        return 0


# ==================== 考试暂存专用函数 ====================

def EXAM_PROGRESS_KEY(exam_id: int, student_id: int) -> str:
    """生成考试暂存的Redis key"""
    return f"exam_progress:{exam_id}:{student_id}"


def save_exam_progress(exam_id: int, student_id: int, question_id: int, answer: Any) -> bool:
    """
    保存单题答案到Redis（哈希结构）
    返回: 是否保存成功
    """
    key = EXAM_PROGRESS_KEY(exam_id, student_id)
    field = f"q_{question_id}"
    try:
        redis_client.hset(key, field, json.dumps(answer))
        # 设置过期时间：考试结束后24小时
        redis_client.expire(key, 86400)
        return True
    except Exception as e:
        logger.warning(f"保存考试进度失败: {e}")
        return False


def get_exam_progress(exam_id: int, student_id: int) -> dict:
    """
    获取考试暂存的所有答案
    返回: {question_id: answer} 格式的字典
    """
    key = EXAM_PROGRESS_KEY(exam_id, student_id)
    try:
        data = redis_client.hgetall(key)
        result = {}
        for field, value in data.items():
            qid = int(field.replace("q_", ""))
            result[qid] = json.loads(value)
        return result
    except Exception as e:
        logger.warning(f"获取考试进度失败: {e}")
        return {}


def clear_exam_progress(exam_id: int, student_id: int) -> bool:
    """清除考试暂存数据"""
    key = EXAM_PROGRESS_KEY(exam_id, student_id)
    return delete_cache(key)
