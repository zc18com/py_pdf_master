#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试PDF文件用于验证PDF查看器功能
"""

import fitz  # PyMuPDF
import os

def create_test_pdf():
    """创建一个简单的测试PDF文件"""
    # 创建PDF文档
    doc = fitz.open()
    
    # 添加第一页
    page1 = doc.new_page()
    
    # 添加标题
    page1.insert_text((72, 72), "PDF全能工具箱测试文档", 
                    fontsize=24, fontname="helv", color=(0, 0, 0))
    
    # 添加内容
    page1.insert_text((72, 120), "这是一个测试PDF文件，用于验证PDF查看器的功能。", 
                    fontsize=12, fontname="helv", color=(0, 0, 0))
    
    page1.insert_text((72, 150), "功能测试：", 
                    fontsize=14, fontname="helv", color=(0, 0, 0))
    
    features = [
        "- 页面导航",
        "- 缩放控制",
        "- 适应宽度/高度",
        "- 文件信息显示"
    ]
    
    y = 180
    for feature in features:
        page1.insert_text((90, y), feature, 
                        fontsize=12, fontname="helv", color=(0, 0, 0))
        y += 30
    
    # 添加第二页
    page2 = doc.new_page()
    page2.insert_text((72, 72), "第二页：图像测试", 
                    fontsize=20, fontname="helv", color=(0, 0, 0))
    
    # 添加一些基本图形
    # 矩形
    page2.draw_rect(fitz.Rect(72, 100, 200, 150), 
                   color=(0, 0, 1), fill=(0.8, 0.8, 1))
    
    # 圆形
    page2.draw_circle((300, 125), 30, 
                     color=(0, 1, 0), fill=(0.8, 1, 0.8))
    
    # 线条
    page2.draw_line((72, 200), (300, 200), color=(1, 0, 0), width=2)
    
    # 添加页码
    page2.insert_text((500, 750), "第 2 页", 
                    fontsize=10, fontname="helv", color=(0.5, 0.5, 0.5))
    
    # 保存文档
    output_path = "new_test.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"测试PDF文件已创建：{output_path}")
    print(f"文件路径：{os.path.abspath(output_path)}")
    return output_path

if __name__ == "__main__":
    create_test_pdf()
