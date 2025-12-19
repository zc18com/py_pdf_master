#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCR引擎模块 - 基于Tesseract
"""

import os
import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
import fitz
from typing import List, Dict, Any, Optional, Tuple
from src.core.pdf_parser import PDFParser


class OCREngine:
    """OCR引擎类，提供文本识别功能"""
    
    def __init__(self):
        self.pdf_parser = None
        self.language = "chi_sim+eng"  # 默认中文简体+英文
        self.image_preprocessing = True
        self.tesseract_config = r"--oem 3 --psm 6"
    
    def set_parser(self, parser: PDFParser):
        """设置PDF解析器"""
        self.pdf_parser = parser
    
    def set_language(self, language: str):
        """设置OCR语言
        
        Args:
            language: 语言代码，例如："chi_sim" (中文简体), "eng" (英文), "chi_sim+eng" (中英文混合)
        """
        self.language = language
    
    def set_image_preprocessing(self, enable: bool):
        """设置是否启用图像预处理"""
        self.image_preprocessing = enable
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """图像预处理，提高OCR识别准确率
        
        Args:
            image: 输入图像
            
        Returns:
            Image.Image: 预处理后的图像
        """
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            
            # 转换为灰度图
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # 自适应阈值处理
            gray = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 去噪处理
            gray = cv2.medianBlur(gray, 3)
            
            # 转换回PIL图像
            processed_image = Image.fromarray(gray)
            
            return processed_image
            
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return image
    
    def recognize_text_from_image(self, image: Image.Image) -> Dict[str, Any]:
        """从图像中识别文本
        
        Args:
            image: 输入图像
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        try:
            # 图像预处理
            if self.image_preprocessing:
                image = self.preprocess_image(image)
            
            # 配置Tesseract
            config = self.tesseract_config
            
            # 执行OCR
            result = pytesseract.image_to_data(
                image, 
                lang=self.language, 
                config=config, 
                output_type=pytesseract.Output.DICT
            )
            
            # 获取纯文本
            full_text = pytesseract.image_to_string(
                image, 
                lang=self.language, 
                config=config
            )
            
            result["full_text"] = full_text
            
            return result
            
        except Exception as e:
            print(f"图像文本识别失败: {e}")
            return {"full_text": "", "text": [], "left": [], "top": [], "width": [], "height": []}
    
    def recognize_text_from_page(self, page_num: int) -> Dict[str, Any]:
        """从PDF页面中识别文本
        
        Args:
            page_num: 页码（从0开始）
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return {"full_text": ""}
            
            # 渲染页面为图像
            image = self.pdf_parser.render_page(page_num, dpi=300)
            if not image:
                return {"full_text": ""}
            
            # 执行OCR
            return self.recognize_text_from_image(image)
            
        except Exception as e:
            print(f"页面文本识别失败: {e}")
            return {"full_text": ""}
    
    def recognize_text_from_region(self, page_num: int, region: Tuple[float, float, float, float]) -> Dict[str, Any]:
        """从指定区域识别文本
        
        Args:
            page_num: 页码（从0开始）
            region: 识别区域 (x0, y0, x1, y1)，使用PDF坐标
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return {"full_text": ""}
            
            # 获取页面
            page = self.pdf_parser.get_page(page_num)
            if not page:
                return {"full_text": ""}
            
            # 获取页面尺寸
            page_width, page_height = self.pdf_parser.get_page_size(page_num)
            if not page_width or not page_height:
                return {"full_text": ""}
            
            # 渲染整个页面
            full_image = self.pdf_parser.render_page(page_num, dpi=300)
            if not full_image:
                return {"full_text": ""}
            
            # 计算渲染后的图像尺寸
            rendered_width, rendered_height = full_image.size
            
            # 将PDF坐标转换为图像坐标
            x0, y0, x1, y1 = region
            img_x0 = int(x0 * rendered_width / page_width)
            img_y0 = int(y0 * rendered_height / page_height)
            img_x1 = int(x1 * rendered_width / page_width)
            img_y1 = int(y1 * rendered_height / page_height)
            
            # 裁剪区域
            region_image = full_image.crop((img_x0, img_y0, img_x1, img_y1))
            
            # 执行OCR
            result = self.recognize_text_from_image(region_image)
            
            # 转换坐标回PDF坐标系
            for i in range(len(result["left"])):
                result["left"][i] = (result["left"][i] + img_x0) * page_width / rendered_width
                result["top"][i] = (result["top"][i] + img_y0) * page_height / rendered_height
                result["width"][i] = result["width"][i] * page_width / rendered_width
                result["height"][i] = result["height"][i] * page_height / rendered_height
            
            return result
            
        except Exception as e:
            print(f"区域文本识别失败: {e}")
            return {"full_text": ""}
    
    def export_searchable_pdf(self, output_path: str, page_nums: Optional[List[int]] = None) -> bool:
        """导出可搜索PDF
        
        Args:
            output_path: 输出路径
            page_nums: 页码列表（从0开始），如果为None则处理所有页面
            
        Returns:
            bool: 是否成功导出
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return False
            
            # 创建新的PDF文档
            new_doc = fitz.open()
            
            # 确定要处理的页面
            total_pages = self.pdf_parser.get_page_count()
            if page_nums is None:
                page_nums = list(range(total_pages))
            
            for page_num in page_nums:
                if page_num < 0 or page_num >= total_pages:
                    continue
                
                # 获取原始页面
                original_page = self.pdf_parser.get_page(page_num)
                if not original_page:
                    continue
                
                # 渲染页面为高分辨率图像
                image = self.pdf_parser.render_page(page_num, dpi=300)
                if not image:
                    continue
                
                # 执行OCR获取文本
                ocr_result = self.recognize_text_from_image(image)
                
                # 获取页面尺寸
                page_size = self.pdf_parser.get_page_size(page_num)
                if not page_size:
                    continue
                
                # 创建新页面
                new_page = new_doc.new_page(-1, width=page_size[0], height=page_size[1])
                
                # 将图像添加到新页面
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes = img_bytes.getvalue()
                
                # 计算图像在页面中的位置和大小
                img_rect = fitz.Rect(0, 0, page_size[0], page_size[1])
                new_page.insert_image(img_rect, stream=img_bytes)
                
                # 添加OCR文本作为不可见文本层
                if "text" in ocr_result and "left" in ocr_result and "top" in ocr_result and "width" in ocr_result and "height" in ocr_result:
                    for i in range(len(ocr_result["text"])):
                        text = ocr_result["text"][i]
                        if not text.strip():
                            continue
                        
                        # 获取文本位置和大小
                        left = ocr_result["left"][i]
                        top = ocr_result["top"][i]
                        width = ocr_result["width"][i]
                        height = ocr_result["height"][i]
                        
                        # 转换为PDF坐标
                        rendered_width, rendered_height = image.size
                        pdf_x = left * page_size[0] / rendered_width
                        pdf_y = page_size[1] - (top + height) * page_size[1] / rendered_height  # 转换Y坐标
                        pdf_width = width * page_size[0] / rendered_width
                        pdf_height = height * page_size[1] / rendered_height
                        
                        # 创建文本矩形
                        rect = fitz.Rect(pdf_x, pdf_y, pdf_x + pdf_width, pdf_y + pdf_height)
                        
                        # 添加文本，设置为透明
                        new_page.insert_textbox(rect, text, fontname="helv", fontsize=10, color=(0, 0, 0))
            
            # 保存可搜索PDF
            if new_doc.page_count > 0:
                new_doc.save(output_path)
                new_doc.close()
                return True
            else:
                new_doc.close()
                return False
                
        except Exception as e:
            print(f"导出可搜索PDF失败: {e}")
            return False
    
    def batch_recognize_pages(self, page_nums: Optional[List[int]] = None) -> Dict[int, Dict[str, Any]]:
        """批量识别PDF页面文本
        
        Args:
            page_nums: 页码列表（从0开始），如果为None则处理所有页面
            
        Returns:
            Dict[int, Dict[str, Any]]: 识别结果，键为页码，值为识别结果
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return {}
            
            # 确定要处理的页面
            total_pages = self.pdf_parser.get_page_count()
            if page_nums is None:
                page_nums = list(range(total_pages))
            
            results = {}
            
            for page_num in page_nums:
                if page_num < 0 or page_num >= total_pages:
                    continue
                
                # 识别页面文本
                result = self.recognize_text_from_page(page_num)
                results[page_num] = result
            
            return results
            
        except Exception as e:
            print(f"批量页面识别失败: {e}")
            return {}
    
    def recognize_full_pdf(self) -> Dict[str, Any]:
        """识别整个PDF文件的文本
        
        Returns:
            Dict[str, Any]: 识别结果
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return {"full_text": "", "page_results": {}}
            
            # 批量识别所有页面
            page_results = self.batch_recognize_pages()
            
            # 合并所有文本
            full_text = ""
            for page_num in sorted(page_results.keys()):
                full_text += page_results[page_num].get("full_text", "") + "\n"
            
            return {
                "full_text": full_text,
                "page_results": page_results
            }
            
        except Exception as e:
            print(f"PDF全文识别失败: {e}")
            return {"full_text": "", "page_results": {}}
    
    def get_available_languages(self) -> List[str]:
        """获取Tesseract可用的语言
        
        Returns:
            List[str]: 语言代码列表
        """
        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            print(f"获取可用语言失败: {e}")
            return []
    
    def set_tesseract_config(self, config: str):
        """设置Tesseract配置参数
        
        Args:
            config: Tesseract配置字符串，例如："--oem 3 --psm 6"
        """
        self.tesseract_config = config


# 示例用法
if __name__ == "__main__":
    # 创建PDF解析器和OCR引擎
    parser = PDFParser()
    ocr_engine = OCREngine()
    ocr_engine.set_parser(parser)
    
    # 打开PDF文件
    if parser.open_pdf("test.pdf"):
        # 设置语言
        ocr_engine.set_language("chi_sim+eng")
        
        # 识别第一页文本
        result = ocr_engine.recognize_text_from_page(0)
        print(f"第一页识别结果: {result['full_text'][:500]}...")
        
        # 导出可搜索PDF
        ocr_engine.export_searchable_pdf("searchable.pdf", [0])
        
        # 关闭PDF文件
        parser.close()