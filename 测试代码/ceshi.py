import multiprocessing
import os

# 获取CPU核心数
cpu_cores = os.cpu_count()
print(f"CPU核心数: {cpu_cores}")

# 使用multiprocessing模块获取CPU核心数
cpu_cores_mp = multiprocessing.cpu_count()
print(f"使用multiprocessing模块获取的CPU核心数: {cpu_cores_mp}")
