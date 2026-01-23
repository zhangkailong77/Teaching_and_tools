import redis
import json
import logging
import time
import os
from datetime import datetime
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


# ==================== ComfyUI队列专用函数 ====================

def enqueue_to_comfy_queue(username: str, prompt_data: dict, port: int) -> str:
    """
    将工作流任务加入队列
    返回: task_id
    """
    task_id = f"comfy:task:{username}:{int(time.time()*1000)}"
    task_data = {
        "task_id": task_id,
        "username": username,
        "port": port,
        "prompt_data": prompt_data,
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    try:
        redis_client.rpush("comfy:queue", json.dumps(task_data))
        redis_client.set(f"comfy:task:{task_id}", json.dumps(task_data), ex=3600)
        logger.info(f"[ComfyUI Queue] 任务加入队列: {task_id}")
        return task_id
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 入队失败: {e}")
        raise


def get_comfy_queue_position(task_id: str) -> int:
    """
    获取任务在队列中的位置（从1开始）
    返回: 排队位置，0表示已在执行
    """
    try:
        queue_list = redis_client.lrange("comfy:queue", 0, -1)
        for idx, task_json in enumerate(queue_list):
            task = json.loads(task_json)
            if task.get("task_id") == task_id:
                return idx + 1
        return 0  # 不在队列中，可能在执行
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 获取队列位置失败: {e}")
        return 0


def get_comfy_task_status(task_id: str) -> Optional[dict]:
    """获取任务状态"""
    try:
        data = redis_client.get(f"comfy:task:{task_id}")
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 获取任务状态失败: {e}")
        return None


def update_comfy_task_status(task_id: str, status: str, result: Optional[dict] = None) -> bool:
    """更新任务状态"""
    try:
        task_data = get_comfy_task_status(task_id)
        if task_data:
            task_data["status"] = status
            if result:
                task_data["result"] = result
            task_data["updated_at"] = datetime.now().isoformat()
            redis_client.set(f"comfy:task:{task_id}", json.dumps(task_data), ex=3600)
            return True
        return False
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 更新任务状态失败: {e}")
        return False


def get_comfy_processing_count() -> int:
    """获取当前正在处理的任务数"""
    try:
        count = redis_client.get("comfy:processing_count")
        return int(count) if count else 0
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 获取处理计数失败: {e}")
        return 0


def incr_comfy_processing_count() -> int:
    """增加处理中的任务数"""
    try:
        return redis_client.incr("comfy:processing_count")
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 增加处理计数失败: {e}")
        return 0


def decr_comfy_processing_count() -> int:
    """减少处理中的任务数"""
    try:
        new_count = redis_client.decr("comfy:processing_count")
        return max(0, new_count)
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 减少处理计数失败: {e}")
        return 0


def get_comfy_max_concurrent() -> int:
    """获取最大并发数（从配置读取）"""
    try:
        # 优先使用环境变量，否则使用默认配置
        max_concurrent = os.getenv("COMFY_MAX_CONCURRENT")
        if max_concurrent:
            return int(max_concurrent)
        return settings.comfy_max_concurrent
    except Exception:
        return settings.comfy_max_concurrent


def get_comfy_queue_length() -> int:
    """获取当前队列长度"""
    try:
        return redis_client.llen("comfy:queue")
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 获取队列长度失败: {e}")
        return 0


def pop_comfy_queue() -> Optional[dict]:
    """从队列头部取出一个任务"""
    try:
        task_json = redis_client.lpop("comfy:queue")
        if task_json:
            return json.loads(task_json)
        return None
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 出队失败: {e}")
        return None
