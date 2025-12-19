#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主界面UI - PDF全能工具箱主窗口
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDockWidget,
    QTabWidget, QToolBar, QStatusBar, QAction, QMenu, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QScrollArea, QGridLayout,
    QPushButton, QComboBox, QSpinBox, QSlider, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, QRectF, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QColor, QBrush

import io
from src.core.pdf_parser import PDFParser
from src.core.converter import PDFConverter


class PDFViewWidget(QWidget):
    """PDF查看组件"""
    
    page_changed = pyqtSignal(int)  # 当前页码变化信号
    zoom_changed = pyqtSignal(float)  # 缩放比例变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pdf_parser = None
        self.current_page = 0
        self.zoom = 1.0
        self.dpi = 96
        
        # 设置布局
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.layout.addWidget(self.scroll_area)
        
        # 创建渲染区域
        self.render_widget = QWidget()
        self.render_layout = QGridLayout(self.render_widget)
        self.render_layout.setAlignment(Qt.AlignCenter)
        self.render_widget.setLayout(self.render_layout)
        self.scroll_area.setWidget(self.render_widget)
        
        # 页码标签
        self.page_label = QLabel("页码: 1/1", self)
        self.page_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.page_label)
    
    def set_pdf_parser(self, pdf_parser: PDFParser):
        """设置PDF解析器"""
        self.pdf_parser = pdf_parser
        self.current_page = 0
        self.update_view()
    
    def update_view(self):
        """更新视图"""
        if not self.pdf_parser or not self.pdf_parser.document:
            return
        
        # 清除现有内容
        for i in reversed(range(self.render_layout.count())):
            widget = self.render_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 渲染当前页面
        img = self.pdf_parser.render_page(self.current_page, self.zoom, self.dpi)
        if img:
            # 转换为QPixmap
            img_data = io.BytesIO()
            img.save(img_data, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(img_data.getvalue())
            
            # 创建标签显示图片
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            self.render_layout.addWidget(img_label)
        
        # 更新页码标签
        self.page_label.setText(f"页码: {self.current_page + 1}/{self.pdf_parser.get_page_count()}")
        
        # 发射信号
        self.page_changed.emit(self.current_page)
    
    def next_page(self):
        """下一页"""
        if not self.pdf_parser or not self.pdf_parser.document:
            return
        
        if self.current_page < self.pdf_parser.get_page_count() - 1:
            self.current_page += 1
            self.update_view()
    
    def previous_page(self):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_view()
    
    def go_to_page(self, page_num: int):
        """跳转到指定页码"""
        if not self.pdf_parser or not self.pdf_parser.document:
            return
        
        if 0 <= page_num < self.pdf_parser.get_page_count():
            self.current_page = page_num
            self.update_view()
    
    def set_zoom(self, zoom: float):
        """设置缩放比例"""
        self.zoom = zoom
        self.update_view()
        self.zoom_changed.emit(zoom)
    
    def zoom_in(self):
        """放大"""
        self.set_zoom(min(self.zoom + 0.25, 4.0))
    
    def zoom_out(self):
        """缩小"""
        self.set_zoom(max(self.zoom - 0.25, 0.25))
    
    def fit_width(self):
        """适应宽度"""
        if not self.pdf_parser or not self.pdf_parser.document:
            return
        
        # 获取当前页面尺寸
        page_size = self.pdf_parser.get_page_size(self.current_page)
        if not page_size:
            return
        
        # 获取滚动区域的视口宽度
        viewport_width = self.scroll_area.viewport().width()
        
        # 计算缩放比例（减去边距）
        margin = 20  # 左右边距合计
        target_width = viewport_width - margin
        zoom = target_width / page_size[0]
        
        self.set_zoom(zoom)
    
    def fit_height(self):
        """适应高度"""
        if not self.pdf_parser or not self.pdf_parser.document:
            return
        
        # 获取当前页面尺寸
        page_size = self.pdf_parser.get_page_size(self.current_page)
        if not page_size:
            return
        
        # 获取滚动区域的视口高度
        viewport_height = self.scroll_area.viewport().height()
        
        # 计算缩放比例（减去边距）
        margin = 40  # 上下边距合计（包括页码标签）
        target_height = viewport_height - margin
        zoom = target_height / page_size[1]
        
        self.set_zoom(zoom)


class PDFMainWindow(QMainWindow):
    """PDF全能工具箱主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化PDF解析器
        self.pdf_parser = PDFParser()
        
        # 初始化PDF转换器
        self.converter = PDFConverter()
        
        # 设置窗口属性
        self.setWindowTitle("PDF全能工具箱")
        self.setMinimumSize(QSize(1200, 800))
        
        # 初始化PDF查看器
        self.pdf_view = PDFViewWidget(self)
        self.setCentralWidget(self.pdf_view)
        
        # 初始化UI组件
        self.setup_ui()
        
        # 连接信号槽
        self.setup_connections()
    
    def setup_ui(self):
        """设置UI组件"""
        self.setup_menus()
        self.setup_toolbars()
        self.setup_dock_widgets()
        self.setup_statusbar()
    
    def setup_menus(self):
        """设置菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        # 新建
        new_action = QAction("新建", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        # 打开
        open_action = QAction("打开", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # 保存
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        # 另存为
        save_as_action = QAction("另存为...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 关闭
        close_action = QAction("关闭", self)
        close_action.setShortcut("Ctrl+W")
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑")
        
        # 查看菜单
        view_menu = self.menuBar().addMenu("查看")
        
        # 工具菜单
        tool_menu = self.menuBar().addMenu("工具")
        
        # 格式转换子菜单
        convert_submenu = tool_menu.addMenu("格式转换")
        
        # PDF转图片
        pdf_to_img_action = QAction("PDF转图片", self)
        pdf_to_img_action.triggered.connect(self.convert_pdf_to_images)
        convert_submenu.addAction(pdf_to_img_action)
        
        # PDF转Word
        pdf_to_word_action = QAction("PDF转Word", self)
        pdf_to_word_action.triggered.connect(self.convert_pdf_to_word)
        convert_submenu.addAction(pdf_to_word_action)
        
        # PDF转Excel
        pdf_to_excel_action = QAction("PDF转Excel", self)
        pdf_to_excel_action.triggered.connect(self.convert_pdf_to_excel)
        convert_submenu.addAction(pdf_to_excel_action)
        
        # PDF转PPT
        pdf_to_ppt_action = QAction("PDF转PPT", self)
        pdf_to_ppt_action.triggered.connect(self.convert_pdf_to_powerpoint)
        convert_submenu.addAction(pdf_to_ppt_action)
        
        # PDF转HTML
        pdf_to_html_action = QAction("PDF转HTML", self)
        pdf_to_html_action.triggered.connect(self.convert_pdf_to_html)
        convert_submenu.addAction(pdf_to_html_action)
        
        # PDF转文本
        pdf_to_text_action = QAction("PDF转文本", self)
        pdf_to_text_action.triggered.connect(self.convert_pdf_to_text)
        convert_submenu.addAction(pdf_to_text_action)
        
        # 设置菜单
        settings_menu = self.menuBar().addMenu("设置")
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
    
    def setup_toolbars(self):
        """设置工具栏"""
        # 主要工具栏
        main_toolbar = self.addToolBar("主要")
        main_toolbar.setIconSize(QSize(24, 24))
        
        # 打开按钮
        open_btn = QAction(QIcon(), "打开", self)
        open_btn.setShortcut("Ctrl+O")
        open_btn.triggered.connect(self.open_file)
        main_toolbar.addAction(open_btn)
        
        # 保存按钮
        save_btn = QAction(QIcon(), "保存", self)
        save_btn.setShortcut("Ctrl+S")
        main_toolbar.addAction(save_btn)
        
        main_toolbar.addSeparator()
        
        # 上一页按钮
        prev_btn = QAction(QIcon(), "上一页", self)
        prev_btn.setShortcut("Left")
        prev_btn.triggered.connect(self.pdf_view.previous_page)
        main_toolbar.addAction(prev_btn)
        
        # 下一页按钮
        next_btn = QAction(QIcon(), "下一页", self)
        next_btn.setShortcut("Right")
        next_btn.triggered.connect(self.pdf_view.next_page)
        main_toolbar.addAction(next_btn)
        
        main_toolbar.addSeparator()
        
        # 缩放控制
        zoom_out_btn = QAction(QIcon(), "缩小", self)
        zoom_out_btn.setShortcut("Ctrl+-")
        zoom_out_btn.triggered.connect(self.pdf_view.zoom_out)
        main_toolbar.addAction(zoom_out_btn)
        
        zoom_in_btn = QAction(QIcon(), "放大", self)
        zoom_in_btn.setShortcut("Ctrl++")
        zoom_in_btn.triggered.connect(self.pdf_view.zoom_in)
        main_toolbar.addAction(zoom_in_btn)
        
        # 视图工具栏
        view_toolbar = self.addToolBar("视图")
        view_toolbar.setIconSize(QSize(24, 24))
    
    def setup_dock_widgets(self):
        """设置停靠窗口"""
        # 左侧文件浏览器
        file_dock = QDockWidget("文件浏览器", self)
        file_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        file_tree = QTreeWidget()
        file_tree.setHeaderLabel("文件列表")
        file_dock.setWidget(file_tree)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, file_dock)
        
        # 左侧书签
        bookmark_dock = QDockWidget("书签", self)
        bookmark_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        bookmark_tree = QTreeWidget()
        bookmark_tree.setHeaderLabel("书签列表")
        bookmark_dock.setWidget(bookmark_tree)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, bookmark_dock)
        
        # 左侧缩略图
        thumbnail_dock = QDockWidget("缩略图", self)
        thumbnail_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        thumbnail_widget = QWidget()
        thumbnail_layout = QVBoxLayout(thumbnail_widget)
        
        # 添加缩略图显示区域
        thumbnail_scroll = QScrollArea()
        thumbnail_container = QWidget()
        thumbnail_container_layout = QVBoxLayout(thumbnail_container)
        thumbnail_scroll.setWidget(thumbnail_container)
        thumbnail_scroll.setWidgetResizable(True)
        
        thumbnail_layout.addWidget(thumbnail_scroll)
        
        thumbnail_dock.setWidget(thumbnail_widget)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, thumbnail_dock)
        
        # 右侧属性面板
        property_dock = QDockWidget("属性", self)
        property_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        property_widget = QWidget()
        property_layout = QVBoxLayout(property_widget)
        
        # 文件信息
        file_info_label = QLabel("文件信息")
        property_layout.addWidget(file_info_label)
        
        self.page_count_label = QLabel("总页数: 0")
        property_layout.addWidget(self.page_count_label)
        
        self.file_size_label = QLabel("文件大小: 0 KB")
        property_layout.addWidget(self.file_size_label)
        
        property_dock.setWidget(property_widget)
        
        self.addDockWidget(Qt.RightDockWidgetArea, property_dock)
    
    def setup_statusbar(self):
        """设置状态栏"""
        self.statusBar().showMessage("就绪")
        
        # 页码显示
        self.page_label = QLabel("页码: 1/1")
        self.statusBar().addPermanentWidget(self.page_label)
        
        # 缩放显示
        self.zoom_label = QLabel("缩放: 100%")
        self.statusBar().addPermanentWidget(self.zoom_label)
    
    def setup_connections(self):
        """连接信号槽"""
        # PDF查看器信号
        self.pdf_view.page_changed.connect(self.update_page_info)
        self.pdf_view.zoom_changed.connect(self.update_zoom_info)
    
    def open_file(self):
        """打开文件"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开PDF文件", "", "PDF文件 (*.pdf)"
        )
        
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path):
        """加载PDF文件"""
        # 关闭现有文档
        if self.pdf_parser:
            self.pdf_parser.close()
        
        # 打开新文档
        self.pdf_parser = PDFParser()
        if self.pdf_parser.open_pdf(file_path):
            # 设置转换器的解析器
            self.converter.set_parser(self.pdf_parser)
            # 更新标题
            self.setWindowTitle(f"PDF全能工具箱 - {file_path}")
            
            # 设置PDF查看器
            self.pdf_view.set_pdf_parser(self.pdf_parser)
            
            # 更新信息
            self.update_file_info()
            
            # 更新状态栏
            self.statusBar().showMessage(f"已打开: {file_path}")
        else:
            self.statusBar().showMessage(f"打开文件失败: {file_path}")
    
    def update_file_info(self):
        """更新文件信息"""
        if not self.pdf_parser or not self.pdf_parser.document:
            return
        
        # 更新页码信息
        total_pages = self.pdf_parser.get_page_count()
        self.page_count_label.setText(f"总页数: {total_pages}")
        self.page_label.setText(f"页码: 1/{total_pages}")
    
    def update_page_info(self, current_page):
        """更新当前页码信息"""
        if not self.pdf_parser or not self.pdf_parser.document:
            return
        
        total_pages = self.pdf_parser.get_page_count()
        self.page_label.setText(f"页码: {current_page + 1}/{total_pages}")
    
    def update_zoom_info(self, zoom):
        """更新缩放信息"""
        zoom_percent = int(zoom * 100)
        self.zoom_label.setText(f"缩放: {zoom_percent}%")
    
    def closeEvent(self, event):
        """关闭事件"""
        # 关闭PDF文档
        if self.pdf_parser:
            self.pdf_parser.close()
        
        event.accept()
    
    def convert_pdf_to_images(self):
        """PDF转图片"""
        if not self.pdf_parser or not self.pdf_parser.document:
            QMessageBox.warning(self, "提示", "请先打开一个PDF文件")
            return
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if not output_dir:
            return
        
        # 执行转换
        result = self.converter.pdf_to_images(output_dir)
        if result:
            QMessageBox.information(self, "成功", f"转换完成，共生成{len(result)}张图片")
            self.statusBar().showMessage(f"PDF转图片成功，共生成{len(result)}张图片")
        else:
            QMessageBox.warning(self, "失败", "转换失败")
            self.statusBar().showMessage("PDF转图片失败")
    
    def convert_pdf_to_word(self):
        """PDF转Word"""
        if not self.pdf_parser or not self.pdf_parser.document:
            QMessageBox.warning(self, "提示", "请先打开一个PDF文件")
            return
        
        # 选择输出文件
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存Word文件", "", "Word文件 (*.docx)"
        )
        if not output_path:
            return
        
        # 确保文件扩展名为.docx
        if not output_path.endswith(".docx"):
            output_path += ".docx"
        
        # 执行转换
        result = self.converter.pdf_to_word(output_path)
        if result:
            QMessageBox.information(self, "成功", "转换完成")
            self.statusBar().showMessage("PDF转Word成功")
        else:
            QMessageBox.warning(self, "失败", "转换失败")
            self.statusBar().showMessage("PDF转Word失败")
    
    def convert_pdf_to_excel(self):
        """PDF转Excel"""
        if not self.pdf_parser or not self.pdf_parser.document:
            QMessageBox.warning(self, "提示", "请先打开一个PDF文件")
            return
        
        # 选择输出文件
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存Excel文件", "", "Excel文件 (*.xlsx)"
        )
        if not output_path:
            return
        
        # 确保文件扩展名为.xlsx
        if not output_path.endswith(".xlsx"):
            output_path += ".xlsx"
        
        # 执行转换
        result = self.converter.pdf_to_excel(output_path)
        if result:
            QMessageBox.information(self, "成功", "转换完成")
            self.statusBar().showMessage("PDF转Excel成功")
        else:
            QMessageBox.warning(self, "失败", "转换失败")
            self.statusBar().showMessage("PDF转Excel失败")
    
    def convert_pdf_to_powerpoint(self):
        """PDF转PPT"""
        if not self.pdf_parser or not self.pdf_parser.document:
            QMessageBox.warning(self, "提示", "请先打开一个PDF文件")
            return
        
        # 选择输出文件
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存PowerPoint文件", "", "PowerPoint文件 (*.pptx)"
        )
        if not output_path:
            return
        
        # 确保文件扩展名为.pptx
        if not output_path.endswith(".pptx"):
            output_path += ".pptx"
        
        # 执行转换
        result = self.converter.pdf_to_powerpoint(output_path)
        if result:
            QMessageBox.information(self, "成功", "转换完成")
            self.statusBar().showMessage("PDF转PPT成功")
        else:
            QMessageBox.warning(self, "失败", "转换失败")
            self.statusBar().showMessage("PDF转PPT失败")
    
    def convert_pdf_to_html(self):
        """PDF转HTML"""
        if not self.pdf_parser or not self.pdf_parser.document:
            QMessageBox.warning(self, "提示", "请先打开一个PDF文件")
            return
        
        # 选择输出文件
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存HTML文件", "", "HTML文件 (*.html)"
        )
        if not output_path:
            return
        
        # 确保文件扩展名为.html
        if not output_path.endswith(".html"):
            output_path += ".html"
        
        # 执行转换
        result = self.converter.pdf_to_html(output_path)
        if result:
            QMessageBox.information(self, "成功", "转换完成")
            self.statusBar().showMessage("PDF转HTML成功")
        else:
            QMessageBox.warning(self, "失败", "转换失败")
            self.statusBar().showMessage("PDF转HTML失败")
    
    def convert_pdf_to_text(self):
        """PDF转文本"""
        if not self.pdf_parser or not self.pdf_parser.document:
            QMessageBox.warning(self, "提示", "请先打开一个PDF文件")
            return
        
        # 选择输出文件
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存文本文件", "", "文本文件 (*.txt)"
        )
        if not output_path:
            return
        
        # 确保文件扩展名为.txt
        if not output_path.endswith(".txt"):
            output_path += ".txt"
        
        # 执行转换
        result = self.converter.pdf_to_text(output_path)
        if result:
            QMessageBox.information(self, "成功", "转换完成")
            self.statusBar().showMessage("PDF转文本成功")
        else:
            QMessageBox.warning(self, "失败", "转换失败")
            self.statusBar().showMessage("PDF转文本失败")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = PDFMainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
