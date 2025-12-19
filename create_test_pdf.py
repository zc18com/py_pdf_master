#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建测试PDF文件的脚本
"""

import fitz
import os

def create_test_pdf():
    """创建一个简单的测试PDF文件"""
    # 创建新的PDF文档
    doc = fitz.open()
    
    # 添加第1页
    page1 = doc.new_page()
    text1 = "这是测试PDF文件的第1页\n\n用于测试PDF编辑器的水印功能\n\nPDF全能工具箱"
    page1.insert_text((50, 100), text1, fontname="helv", fontsize=24, color=(0, 0, 0))
    
    # 添加第2页
    page2 = doc.new_page()
    text2 = "这是测试PDF文件的第2页\n\n水印功能测试\n\n支持文本水印和图像水印"
    page2.insert_text((50, 100), text2, fontname="helv", fontsize=24, color=(0, 0, 0))
    
    # 添加第3页
    page3 = doc.new_page()
    text3 = "这是测试PDF文件的第3页\n\n水印参数配置\n\n- 透明度\n- 位置\n- 旋转角度\n- 字体大小\n- 颜色"
    page3.insert_text((50, 100), text3, fontname="helv", fontsize=24, color=(0, 0, 0))
    
    # 保存PDF文件
    doc.save("test.pdf")
    doc.close()
    
    print("已创建测试PDF文件: test.pdf")

if __name__ == "__main__":
    create_test_pdf()
