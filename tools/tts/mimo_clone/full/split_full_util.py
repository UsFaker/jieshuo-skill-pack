"""兼容旧名：数字转汉字，实际实现在 ../textutil.py。"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from textutil import n2c, fixnum, num2cn, D  # noqa: F401
