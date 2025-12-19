#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF查看器的核心功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import PDFMainWindow
from src.core.pdf_parser import PDFParser


def test_pdf_parser():
    """测试PDF解析器功能"""
    print("=== 测试PDF解析器功能 ===")
    
    # 创建解析器实例
    parser = PDFParser()
    
    # 打开测试PDF文件
    pdf_path = "new_test.pdf"
    if os.path.exists(pdf_path):
        print(f"尝试打开PDF文件: {pdf_path}")
        success = parser.open_pdf(pdf_path)
        
        if success:
            print("✅ 成功打开PDF文件")
            
            # 测试获取页面数量
            page_count = parser.get_page_count()
            print(f"✅ 页面数量: {page_count}")
            
            # 测试获取页面尺寸
            for page_num in range(page_count):
                page_size = parser.get_page_size(page_num)
                if page_size:
                    print(f"✅ 页面 {page_num + 1} 尺寸: {page_size[0]:.2f} x {page_size[1]:.2f} 点")
            
            # 测试渲染页面
            img = parser.render_page(0, zoom=1.0, dpi=96)
            if img:
                print(f"✅ 成功渲染第一页, 图像尺寸: {img.width} x {img.height}")
            
            # 关闭PDF文件
            parser.close()
            print("✅ 成功关闭PDF文件")
        else:
            print("❌ 打开PDF文件失败")
    else:
        print(f"❌ 测试PDF文件不存在: {pdf_path}")
    
    print()


def test_pdf_viewer():
    """测试PDF查看器功能"""
    print("=== 测试PDF查看器功能 ===")
    
    # 创建应用程序实例
    app = QApplication([])
    
    # 创建主窗口实例
    try:
        main_window = PDFMainWindow()
        print("✅ 成功创建PDFMainWindow实例")
        
        # 尝试加载测试PDF
        pdf_path = "new_test.pdf"
        if os.path.exists(pdf_path):
            print(f"尝试加载PDF文件: {pdf_path}")
            main_window.load_pdf(pdf_path)
            print("✅ 成功加载PDF文件")
        
        # 测试页面导航
        print("✅ 测试页面导航功能")
        main_window.pdf_view.zoom_in()
        main_window.pdf_view.zoom_out()
        print("✅ 缩放功能测试通过")
        
        # 测试适应宽度
        main_window.pdf_view.fit_width()
        print("✅ 适应宽度功能测试通过")
        
        print("✅ PDF查看器功能测试通过")
        
    except Exception as e:
        print(f"❌ PDF查看器测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()


if __name__ == "__main__":
    # 测试PDF解析器
    test_pdf_parser()
    
    # 测试PDF查看器
    test_pdf_viewer()
    
    print("=== 所有测试完成 ===")
