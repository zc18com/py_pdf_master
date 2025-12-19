#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF解析模块 - 基于PyMuPDF (fitz)
"""

import fitz
import io
from typing import Optional, List, Dict, Any, Tuple
from PIL import Image


class PDFParser:
    """PDF解析器类，提供PDF文件的基本操作接口"""
    
    def __init__(self):
        self.document = None
        self.file_path = None
        self.is_encrypted = False
    
    def open_pdf(self, file_path: str) -> bool:
        """
        打开PDF文件
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            bool: 是否成功打开
        """
        try:
            # 尝试打开PDF文件
            self.document = fitz.open(file_path)
            self.file_path = file_path
            self.is_encrypted = self.document.is_encrypted
            return True
        except Exception as e:
            print(f"打开PDF文件失败: {e}")
            return False
    
    def close(self):
        """关闭PDF文件"""
        if self.document:
            self.document.close()
            self.document = None
            self.file_path = None
            self.is_encrypted = False
    
    def get_page_count(self) -> int:
        """
        获取PDF文件的总页数
        
        Returns:
            int: 总页数
        """
        if not self.document:
            return 0
        return len(self.document)
    
    def get_page(self, page_num: int) -> Optional[fitz.Page]:
        """
        获取指定页码的页面
        
        Args:
            page_num: 页码（从0开始）
            
        Returns:
            Optional[fitz.Page]: 页面对象
        """
        if not self.document or page_num < 0 or page_num >= len(self.document):
            return None
        return self.document[page_num]
    
    def render_page(self, page_num: int, zoom: float = 1.0, dpi: int = 96) -> Optional[Image.Image]:
        """
        渲染指定页码的页面为图片
        
        Args:
            page_num: 页码（从0开始）
            zoom: 缩放比例
            dpi: 分辨率
            
        Returns:
            Optional[Image.Image]: 渲染后的图片
        """
        try:
            page = self.get_page(page_num)
            if not page:
                return None
            
            # 设置渲染参数
            matrix = fitz.Matrix(zoom * (dpi / 72), zoom * (dpi / 72))
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # 转换为PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return img
        except Exception as e:
            print(f"渲染页面失败: {e}")
            return None
    
    def extract_text(self, page_num: Optional[int] = None) -> str:
        """
        提取PDF文本
        
        Args:
            page_num: 页码（从0开始），如果为None则提取所有页面
            
        Returns:
            str: 提取的文本
        """
        try:
            if not self.document:
                return ""
            
            text = ""
            if page_num is not None:
                page = self.get_page(page_num)
                if page:
                    text = page.get_text()
            else:
                for page in self.document:
                    text += page.get_text()
            
            return text
        except Exception as e:
            print(f"提取文本失败: {e}")
            return ""
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取PDF文件的元数据
        
        Returns:
            Dict[str, Any]: 元数据字典
        """
        if not self.document:
            return {}
        
        try:
            metadata = self.document.metadata
            return metadata
        except Exception as e:
            print(f"获取元数据失败: {e}")
            return {}
    
    def get_bookmarks(self) -> List[Dict[str, Any]]:
        """
        获取PDF文件的书签
        
        Returns:
            List[Dict[str, Any]]: 书签列表
        """
        if not self.document:
            return []
        
        try:
            bookmarks = self.document.get_toc()
            # 转换为更友好的格式
            formatted_bookmarks = []
            for bookmark in bookmarks:
                level, title, page = bookmark
                formatted_bookmarks.append({
                    "level": level,
                    "title": title,
                    "page": page - 1  # 转换为0-based索引
                })
            return formatted_bookmarks
        except Exception as e:
            print(f"获取书签失败: {e}")
            return []
    
    def get_page_size(self, page_num: int) -> Optional[Tuple[float, float]]:
        """
        获取指定页码的页面尺寸（宽, 高）
        
        Args:
            page_num: 页码（从0开始）
            
        Returns:
            Optional[Tuple[float, float]]: 页面尺寸（宽, 高）
        """
        page = self.get_page(page_num)
        if not page:
            return None
        
        rect = page.rect
        return (rect.width, rect.height)
    
    def search_text(self, text: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        在PDF文件中搜索文本
        
        Args:
            text: 要搜索的文本
            case_sensitive: 是否区分大小写
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        if not self.document or not text:
            return []
        
        try:
            results = []
            for page_num, page in enumerate(self.document):
                # 设置搜索参数
                flags = 0
                if not case_sensitive:
                    flags |= fitz.TEXT_CASELESS
                
                # 搜索文本
                instances = page.search_for(text, flags=flags)
                
                # 处理搜索结果
                for instance in instances:
                    results.append({
                        "page": page_num,
                        "rect": instance,
                        "text": text
                    })
            
            return results
        except Exception as e:
            print(f"搜索文本失败: {e}")
            return []
    
    def rotate_page(self, page_num: int, angle: int) -> bool:
        """
        旋转指定页码的页面
        
        Args:
            page_num: 页码（从0开始）
            angle: 旋转角度（90, 180, 270）
            
        Returns:
            bool: 是否成功旋转
        """
        try:
            page = self.get_page(page_num)
            if not page:
                return False
            
            page.set_rotation(angle)
            return True
        except Exception as e:
            print(f"旋转页面失败: {e}")
            return False
    
    def save(self, output_path: Optional[str] = None) -> bool:
        """
        保存PDF文件
        
        Args:
            output_path: 输出路径，如果为None则覆盖原文件
            
        Returns:
            bool: 是否成功保存
        """
        try:
            if not self.document:
                return False
            
            if output_path:
                self.document.save(output_path)
            else:
                self.document.save(self.file_path)
            
            return True
        except Exception as e:
            print(f"保存PDF文件失败: {e}")
            return False
    
    def __del__(self):
        """析构函数，确保关闭文档"""
        self.close()


# 示例用法
if __name__ == "__main__":
    parser = PDFParser()
    
    # 打开PDF文件
    if parser.open_pdf("test.pdf"):
        print(f"总页数: {parser.get_page_count()}")
        print(f"元数据: {parser.get_metadata()}")
        print(f"书签: {parser.get_bookmarks()}")
        
        # 渲染第一页
        img = parser.render_page(0)
        if img:
            img.show()
        
        # 提取第一页文本
        text = parser.extract_text(0)
        print(f"第一页文本: {text[:100]}...")
        
        # 关闭PDF文件
        parser.close()
