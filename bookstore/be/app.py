import os
import sys

# 获取当前脚本所在的目录的上一级目录的上一级目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from be import serve

if __name__ == "__main__":
    serve.be_run()
