# backend/app/utils/comfy_runner.py

import paramiko
import time
import socket # 引入 socket 用于捕获底层网络错误

# ... (配置部分保持不变) ...
GPU_HOST = "192.168.150.2"
GPU_PORT = 22
GPU_USER = "yzcube"
GPU_PASSWORD = "Yanzhi2025."
BASE_PATH = "/home/yzcube/cube/comfyui-test/ComfyUI-test"
CONDA_INIT_SCRIPT = "/home/yzcube/anaconda3/etc/profile.d/conda.sh"
CONDA_ENV_NAME = "comfyui"

def start_comfyui_remote(username: str, port: int):
    print(f"========== [DEBUG] 开始流程: {username} (端口: {port}) ==========")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 连接阶段
        print(f"--- [DEBUG] 1. 连接 SSH...")
        ssh.connect(GPU_HOST, GPU_PORT, GPU_USER, GPU_PASSWORD, timeout=10)
        
        # 准备启动命令 (优化了 nohup 写法，防止挂起)
        output_dir = f"/home/yzcube/cube/comfyui-test/output_{username}"
        user_dir = f"/home/yzcube/cube/comfyui-test/user_{username}"
        
        cmd = f"""
        source {CONDA_INIT_SCRIPT} && \
        conda activate {CONDA_ENV_NAME} && \
        mkdir -p {output_dir} {user_dir} && \
        if ! lsof -i:{port} -t >/dev/null; then
            cd {BASE_PATH} && \
            nohup python main.py \
                --port {port} \
                --listen 0.0.0.0 \
                --output-directory {output_dir} \
                --user-directory {user_dir} \
                < /dev/null > {output_dir}/startup.log 2>&1 &
            echo "STARTED"
        else
            echo "ALREADY_RUNNING"
        fi
        """
        
        print(f"--- [DEBUG] 2. 发送启动命令...")
        
        try:
            # 尝试执行，设置 30秒超时 (如果30秒还没回音，通常是卡住了)
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
            result = stdout.read().decode().strip()
            print(f"--- [DEBUG] 3. 原生返回: {result}")
            return True

        except socket.timeout:
            # 【核心修复逻辑】如果超时了，不要慌，去检查一下端口到底活没活
            print(f"⚠️ [DEBUG] 启动命令超时！正在进行二次确认...")
            
            # 新开一个简单的检查命令，这个非常快
            check_cmd = f"lsof -i:{port} -t"
            stdin_chk, stdout_chk, stderr_chk = ssh.exec_command(check_cmd, timeout=5)
            check_result = stdout_chk.read().decode().strip()
            
            if check_result:
                print(f"✅ [DEBUG] 二次确认成功！进程 PID: {check_result} 实际上已经启动了。")
                return True
            else:
                print(f"❌ [DEBUG] 二次确认失败，服务真的没启动。")
                return False

    except Exception as e:
        print(f"❌ [DEBUG] 系统错误: {e}")
        return False
    finally:
        ssh.close()
        print(f"========== [DEBUG] 流程结束 ==========")

# --- 【新增】关闭环境函数 ---
def stop_comfyui_remote(username: str, port: int):
    print(f"========== [DEBUG] 停止流程: {username} ==========")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(GPU_HOST, GPU_PORT, GPU_USER, GPU_PASSWORD, timeout=10)
        
        # 构建杀进程命令
        # 逻辑：查找占用端口的 PID，如果有就 kill -9，否则输出 NOT_RUNNING
        cmd = f"""
        if lsof -i:{port} -t >/dev/null; then
            kill -9 $(lsof -i:{port} -t)
            echo "STOPPED"
        else
            echo "NOT_RUNNING"
        fi
        """
        
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
        result = stdout.read().decode().strip()
        print(f"--- [DEBUG] 停止结果: {result}")
        return True
        
    except Exception as e:
        print(f"❌ [DEBUG] 停止失败: {e}")
        return False
    finally:
        ssh.close()