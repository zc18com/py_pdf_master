#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF编辑器模块 - 提供PDF页面管理和编辑功能
"""

import fitz
import io
from typing import Optional, List, Tuple, Union
from src.core.pdf_parser import PDFParser


class PDFEditor:
    """PDF编辑器类，提供PDF页面管理和编辑功能"""
    
    def __init__(self):
        self.parser = None
    
    def set_parser(self, parser: PDFParser):
        """设置PDF解析器"""
        self.parser = parser
    
    def extract_pages(self, page_numbers: List[int], output_path: str) -> bool:
        """
        提取指定页码的页面到新的PDF文件
        
        Args:
            page_numbers: 要提取的页码列表（从0开始）
            output_path: 输出PDF文件路径
            
        Returns:
            bool: 是否成功提取
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            # 创建新的PDF文档
            new_doc = fitz.open()
            
            # 提取页面
            for page_num in page_numbers:
                if 0 <= page_num < self.parser.get_page_count():
                    new_doc.insert_pdf(self.parser.document, from_page=page_num, to_page=page_num)
            
            # 保存新文档
            if new_doc.page_count > 0:
                new_doc.save(output_path)
                new_doc.close()
                return True
            else:
                new_doc.close()
                return False
                
        except Exception as e:
            print(f"提取页面失败: {e}")
            return False
    
    def delete_pages(self, page_numbers: List[int]) -> bool:
        """
        删除指定页码的页面
        
        Args:
            page_numbers: 要删除的页码列表（从0开始）
            
        Returns:
            bool: 是否成功删除
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            # 按降序删除页码（避免索引混乱）
            sorted_page_numbers = sorted(set(page_numbers), reverse=True)
            
            for page_num in sorted_page_numbers:
                if 0 <= page_num < self.parser.get_page_count():
                    self.parser.document.delete_page(page_num)
            
            return True
            
        except Exception as e:
            print(f"删除页面失败: {e}")
            return False
    
    def reorder_pages(self, page_order: List[int]) -> bool:
        """
        重新排序页面
        
        Args:
            page_order: 新的页码顺序列表（从0开始）
            
        Returns:
            bool: 是否成功重新排序
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            total_pages = self.parser.get_page_count()
            
            # 验证输入的页码顺序是否有效
            if len(page_order) != total_pages:
                return False
            
            if set(page_order) != set(range(total_pages)):
                return False
            
            # 创建新的PDF文档
            new_doc = fitz.open()
            
            # 按新顺序插入页面
            for page_num in page_order:
                new_doc.insert_pdf(self.parser.document, from_page=page_num, to_page=page_num)
            
            # 替换原文档
            self.parser.document.close()
            self.parser.document = new_doc
            
            return True
            
        except Exception as e:
            print(f"重新排序页面失败: {e}")
            return False
    
    def rotate_pages(self, page_numbers: List[int], angle: int) -> bool:
        """
        旋转指定页码的页面
        
        Args:
            page_numbers: 要旋转的页码列表（从0开始）
            angle: 旋转角度（90, 180, 270）
            
        Returns:
            bool: 是否成功旋转
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            for page_num in page_numbers:
                if 0 <= page_num < self.parser.get_page_count():
                    page = self.parser.document[page_num]
                    page.set_rotation(angle)
            
            return True
            
        except Exception as e:
            print(f"旋转页面失败: {e}")
            return False
    
    def insert_blank_page(self, position: int, width: float = 595.3, height: float = 841.9) -> bool:
        """
        在指定位置插入空白页
        
        Args:
            position: 插入位置（从0开始）
            width: 页面宽度（默认A4宽度）
            height: 页面高度（默认A4高度）
            
        Returns:
            bool: 是否成功插入
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            # 验证位置
            if position < 0:
                position = 0
            elif position > self.parser.get_page_count():
                position = self.parser.get_page_count()
            
            # 插入空白页
            self.parser.document.new_page(-1, width=width, height=height)
            
            # 如果不是插入到最后，需要移动页面
            if position < self.parser.get_page_count() - 1:
                # 移动页面到指定位置
                self.parser.document.move_page(self.parser.get_page_count() - 1, position)
            
            return True
            
        except Exception as e:
            print(f"插入空白页失败: {e}")
            return False
    
    def duplicate_page(self, page_num: int, position: Optional[int] = None) -> bool:
        """
        复制指定页码的页面
        
        Args:
            page_num: 要复制的页码（从0开始）
            position: 复制后的位置（默认插入到原页面后面）
            
        Returns:
            bool: 是否成功复制
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            # 验证页码
            if page_num < 0 or page_num >= self.parser.get_page_count():
                return False
            
            # 确定插入位置
            if position is None:
                position = page_num + 1
            
            # 插入复制的页面
            self.parser.document.insert_pdf(
                self.parser.document, 
                from_page=page_num, 
                to_page=page_num,
                start_at=position
            )
            
            return True
            
        except Exception as e:
            print(f"复制页面失败: {e}")
            return False
    
    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> bool:
        """
        合并多个PDF文件
        
        Args:
            pdf_files: 要合并的PDF文件路径列表
            output_path: 输出PDF文件路径
            
        Returns:
            bool: 是否成功合并
        """
        try:
            # 创建新的PDF文档
            new_doc = fitz.open()
            
            # 合并所有PDF文件
            for pdf_file in pdf_files:
                try:
                    src_doc = fitz.open(pdf_file)
                    new_doc.insert_pdf(src_doc)
                    src_doc.close()
                except Exception as e:
                    print(f"合并文件 {pdf_file} 失败: {e}")
            
            # 保存合并后的文档
            if new_doc.page_count > 0:
                new_doc.save(output_path)
                new_doc.close()
                return True
            else:
                new_doc.close()
                return False
                
        except Exception as e:
            print(f"合并PDF文件失败: {e}")
            return False
    
    def split_by_page(self, page_ranges: List[Tuple[int, int]], output_prefix: str) -> List[str]:
        """
        按页码范围分割PDF文件
        
        Args:
            page_ranges: 页码范围列表（从0开始，包含起始页和结束页）
            output_prefix: 输出文件前缀
            
        Returns:
            List[str]: 生成的PDF文件路径列表
        """
        try:
            if not self.parser or not self.parser.document:
                return []
            
            output_files = []
            
            for i, (start_page, end_page) in enumerate(page_ranges):
                # 验证页码范围
                if start_page < 0:
                    start_page = 0
                if end_page >= self.parser.get_page_count():
                    end_page = self.parser.get_page_count() - 1
                if start_page > end_page:
                    continue
                
                # 创建新的PDF文档
                new_doc = fitz.open()
                new_doc.insert_pdf(self.parser.document, from_page=start_page, to_page=end_page)
                
                # 保存新文档
                output_path = f"{output_prefix}_{i+1}.pdf"
                new_doc.save(output_path)
                new_doc.close()
                
                output_files.append(output_path)
            
            return output_files
            
        except Exception as e:
            print(f"分割PDF文件失败: {e}")
            return []
    
    def split_by_every_n_pages(self, n: int, output_prefix: str) -> List[str]:
        """
        按每N页分割PDF文件
        
        Args:
            n: 每N页分割一次
            output_prefix: 输出文件前缀
            
        Returns:
            List[str]: 生成的PDF文件路径列表
        """
        try:
            if not self.parser or not self.parser.document:
                return []
            
            total_pages = self.parser.get_page_count()
            page_ranges = []
            
            for i in range(0, total_pages, n):
                start = i
                end = min(i + n - 1, total_pages - 1)
                page_ranges.append((start, end))
            
            return self.split_by_page(page_ranges, output_prefix)
            
        except Exception as e:
            print(f"按每N页分割PDF失败: {e}")
            return []
    
    def crop_pages(self, page_numbers: List[int], crop_rect: Tuple[float, float, float, float]) -> bool:
        """
        裁剪指定页码的页面
        
        Args:
            page_numbers: 要裁剪的页码列表（从0开始）
            crop_rect: 裁剪矩形 (x0, y0, x1, y1)
            
        Returns:
            bool: 是否成功裁剪
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            for page_num in page_numbers:
                if 0 <= page_num < self.parser.get_page_count():
                    page = self.parser.document[page_num]
                    page.set_cropbox(fitz.Rect(*crop_rect))
            
            return True
            
        except Exception as e:
            print(f"裁剪页面失败: {e}")
            return False
    
    def add_watermark(self, page_numbers: List[int], watermark_type: str, content: str, 
                      position: Tuple[float, float] = None, font_size: float = 48, 
                      color: Tuple[float, float, float] = (0, 0, 0)) -> bool:
        """
        为指定页码的页面添加水印

        Args:
            page_numbers: 要添加水印的页码列表（从0开始）
            watermark_type: 水印类型 ('text' 或 'image')
            content: 水印内容（文本水印为文本，图像水印为图像文件路径）
            position: 水印位置 (x, y)，默认居中
            font_size: 文本水印字体大小，默认48
            color: 文本水印颜色 (r, g, b)，默认黑色

        Returns:
            bool: 是否成功添加水印
        """
        try:
            if not self.parser or not self.parser.document:
                return False
            
            for page_num in page_numbers:
                if 0 <= page_num < self.parser.get_page_count():
                    page = self.parser.document[page_num]
                    page_rect = page.rect
                    
                    # 确定水印位置
                    if position is None:
                        # 默认居中
                        x = page_rect.x1 / 2
                        y = page_rect.y1 / 2
                    else:
                        x, y = position
                    
                    if watermark_type == 'text':
                        # 添加文本水印
                        r, g, b = color
                        
                        # 设置水印属性
                        text_opts = {
                            "color": (r, g, b),
                            "fontname": "helv",
                            "fontsize": font_size
                        }
                        
                        # 添加文本水印
                        page.insert_text((x, y), content, **text_opts, overlay=True)
                        
                    elif watermark_type == 'image':
                        # 添加图像水印
                        try:
                            # 创建图像矩形
                            img_width = 200
                            img_height = 200
                            img_rect = fitz.Rect(x - img_width/2, y - img_height/2, x + img_width/2, y + img_height/2)
                            
                            # 添加图像水印
                            page.insert_image(img_rect, filename=content, overlay=True)
                        except Exception as img_e:
                            print(f"添加图像水印失败: {img_e}")
                            continue
                    
            return True
            
        except Exception as e:
            print(f"添加水印失败: {e}")
            return False


# 示例用法
if __name__ == "__main__":
    from src.core.pdf_parser import PDFParser
    import os
    
    # 创建PDF解析器和编辑器
    parser = PDFParser()
    editor = PDFEditor()
    editor.set_parser(parser)
    
    # 测试文件路径
    test_pdf_path = "test.pdf"
    
    # 检查测试文件是否存在
    if not os.path.exists(test_pdf_path):
        print(f"测试文件 {test_pdf_path} 不存在，请先创建或提供该文件。")
        exit(1)
    
    # 打开PDF文件
    if parser.open_pdf(test_pdf_path):
        print("成功打开PDF文件")
        
        # 提取页面测试
        print("测试提取页面...")
        editor.extract_pages([0, 1], "extracted.pdf")
        print("提取页面完成")
        
        # 水印功能测试
        print("测试文本水印功能...")
        # 为所有页面添加文本水印
        all_pages = list(range(parser.get_page_count()))
        if editor.add_watermark(all_pages, 'text', '测试水印'):
            print("文本水印添加成功")
        else:
            print("文本水印添加失败")
        
        # 保存带有水印的PDF
        parser.save("watermarked_test.pdf")
        print("已保存带有水印的PDF文件: watermarked_test.pdf")
        
        # 关闭PDF文件
        parser.close()
        print("测试完成")
    else:
        print(f"无法打开PDF文件: {test_pdf_path}")
