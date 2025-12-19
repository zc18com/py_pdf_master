#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF全能工具箱 (PDF Master Suite) - 程序入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主窗口
from src.ui.main_window import PDFMainWindow

class PDFMasterSuiteApp(QApplication):
    """PDF全能工具箱应用程序类"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # 设置应用程序信息
        self.setApplicationName("PDF全能工具箱")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("PDF Master Suite")
        #self.setOrganizationDomain("pdfmaster.com")
        
        # 设置全局样式
        self.setStyle("Fusion")
        
    def start(self):
        """启动应用程序"""
        try:
            # 创建并显示主窗口
            main_window = PDFMainWindow()
            main_window.showMaximized()
            
            # 运行应用程序
            return self.exec_()
            
        except Exception as e:
            QMessageBox.critical(None, "错误", f"启动应用程序失败: {str(e)}")
            return 1


def main():
    """主函数"""
    try:
        # 创建应用程序实例
        app = PDFMasterSuiteApp(sys.argv)
        
        # 启动应用程序
        return app.start()
        
    except KeyboardInterrupt:
        print("程序被用户中断")
        return 0
    except Exception as e:
        print(f"程序异常退出: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
