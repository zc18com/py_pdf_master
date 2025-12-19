#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批处理模块 - 提供批量PDF处理功能
"""

import os
import shutil
import time
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.core.pdf_parser import PDFParser
from src.core.editor import PDFEditor
from src.core.converter import PDFConverter
from src.core.security import PDFSecurity
from src.core.ocr_engine import OCREngine


class BatchProcessor:
    """批处理处理器类，提供多种批量PDF处理功能"""
    
    def __init__(self, max_workers: int = 4):
        """初始化批处理处理器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.pdf_parser = PDFParser()
        self.pdf_editor = PDFEditor()
        self.pdf_editor.set_parser(self.pdf_parser)
        self.pdf_converter = PDFConverter()
        self.pdf_converter.set_parser(self.pdf_parser)
        self.pdf_security = PDFSecurity()
        self.pdf_security.set_parser(self.pdf_parser)
        self.ocr_engine = OCREngine()
        self.ocr_engine.set_parser(self.pdf_parser)
        self.progress_callback: Optional[Callable[[float, str], None]] = None
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """设置进度回调函数
        
        Args:
            callback: 回调函数，参数为进度百分比(float)和当前状态(str)
        """
        self.progress_callback = callback
    
    def _update_progress(self, progress: float, status: str):
        """更新进度
        
        Args:
            progress: 进度百分比 (0.0-1.0)
            status: 当前状态描述
        """
        if self.progress_callback:
            self.progress_callback(progress, status)
    
    def _process_single_file(self, file_path: str, operation: Callable, *args, **kwargs) -> Dict[str, Any]:
        """处理单个文件
        
        Args:
            file_path: 文件路径
            operation: 处理函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            Dict[str, Any]: 处理结果
        """
        result = {
            "file_path": file_path,
            "success": False,
            "message": "",
            "output_file": None,
            "start_time": time.time()
        }
        
        try:
            # 打开PDF文件
            if not self.pdf_parser.open_pdf(file_path):
                result["message"] = "无法打开文件"
                return result
            
            # 执行操作
            output = operation(file_path, *args, **kwargs)
            
            # 关闭PDF文件
            self.pdf_parser.close()
            
            # 更新结果
            result["success"] = True
            result["output_file"] = output
            result["message"] = "处理成功"
            
        except Exception as e:
            result["message"] = str(e)
            if self.pdf_parser.document:
                self.pdf_parser.close()
        
        result["end_time"] = time.time()
        result["duration"] = result["end_time"] - result["start_time"]
        
        return result
    
    def batch_convert(self, input_files: List[str], output_format: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """批量转换PDF文件
        
        Args:
            input_files: 输入PDF文件列表
            output_format: 输出格式 ("docx", "xlsx", "pptx", "png", "jpeg", "tiff", "txt", "html")
            output_dir: 输出目录
            **kwargs: 转换参数
                - dpi: 图像转换时的DPI (默认300)
                - quality: 图像质量 (默认90)
                - language: OCR语言 (默认"chi_sim+eng")
        
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义转换操作
        def convert_operation(file_path, output_format, output_dir, **kwargs):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            output_path = os.path.join(output_dir, f"{base_name}.{output_format}")
            
            success = False
            
            if output_format == "docx":
                success = self.pdf_converter.pdf_to_word(output_path, **kwargs)
            elif output_format == "xlsx":
                success = self.pdf_converter.pdf_to_excel(output_path, **kwargs)
            elif output_format == "pptx":
                success = self.pdf_converter.pdf_to_powerpoint(output_path, **kwargs)
            elif output_format in ["png", "jpeg", "tiff"]:
                success = self.pdf_converter.pdf_to_images(output_path, **kwargs)
            elif output_format == "txt":
                success = self.pdf_converter.pdf_to_text(output_path, **kwargs)
            elif output_format == "html":
                success = self.pdf_converter.pdf_to_html(output_path, **kwargs)
            
            if not success:
                raise Exception(f"转换失败")
            
            return output_path
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, convert_operation, output_format, output_dir, **kwargs): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"转换完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }
    
    def batch_merge(self, input_files: List[str], output_path: str) -> Dict[str, Any]:
        """批量合并PDF文件
        
        Args:
            input_files: 输入PDF文件列表
            output_path: 输出文件路径
        
        Returns:
            Dict[str, Any]: 处理结果
        """
        start_time = time.time()
        
        try:
            success = self.pdf_editor.merge_pdfs(input_files, output_path)
            
            result = {
                "total_files": len(input_files),
                "success": success,
                "output_file": output_path if success else None,
                "total_duration": time.time() - start_time,
                "message": "合并成功" if success else "合并失败"
            }
            
            self._update_progress(1.0, "合并完成")
            
            return result
            
        except Exception as e:
            self._update_progress(1.0, "合并失败")
            return {
                "total_files": len(input_files),
                "success": False,
                "output_file": None,
                "total_duration": time.time() - start_time,
                "message": str(e)
            }
    
    def batch_split(self, input_files: List[str], output_dir: str, split_mode: str = "single", **kwargs) -> Dict[str, Any]:
        """批量分割PDF文件
        
        Args:
            input_files: 输入PDF文件列表
            output_dir: 输出目录
            split_mode: 分割模式 ("single", "range", "size")
            **kwargs:
                - page_ranges: 页面范围列表，例如 [(1, 5), (6, 10)]
                - max_size: 最大文件大小 (MB)
        
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义分割操作
        def split_operation(file_path, output_dir, split_mode, **kwargs):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            file_output_dir = os.path.join(output_dir, base_name)
            os.makedirs(file_output_dir, exist_ok=True)
            
            output_files = []
            
            if split_mode == "single":
                # 每页分割为单独文件
                total_pages = self.pdf_parser.get_page_count()
                for i in range(total_pages):
                    output_file = os.path.join(file_output_dir, f"{base_name}_page_{i+1}.pdf")
                    if self.pdf_editor.extract_pages([i], output_file):
                        output_files.append(output_file)
            
            elif split_mode == "range":
                # 按页面范围分割
                page_ranges = kwargs.get("page_ranges", [])
                for i, (start, end) in enumerate(page_ranges):
                    output_file = os.path.join(file_output_dir, f"{base_name}_pages_{start}-{end}.pdf")
                    if self.pdf_editor.extract_pages(list(range(start-1, end)), output_file):
                        output_files.append(output_file)
            
            elif split_mode == "size":
                # 按大小分割（需要额外实现）
                raise NotImplementedError("按大小分割功能尚未实现")
            
            if not output_files:
                raise Exception("分割失败")
            
            return output_files
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, split_operation, output_dir, split_mode, **kwargs): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"分割完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }
    
    def batch_add_watermark(self, input_files: List[str], output_dir: str, watermark_text: str = None, watermark_image: str = None, **kwargs) -> Dict[str, Any]:
        """批量添加水印
        
        Args:
            input_files: 输入PDF文件列表
            output_dir: 输出目录
            watermark_text: 水印文本（如果是文字水印）
            watermark_image: 水印图像路径（如果是图片水印）
            **kwargs:
                - opacity: 透明度 (0.0-1.0)
                - position: 位置 ("center", "top-left", "top-right", "bottom-left", "bottom-right")
                - rotation: 旋转角度 (0-360)
        
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义添加水印操作
        def add_watermark_operation(file_path, output_dir, watermark_text, watermark_image, **kwargs):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            output_file = os.path.join(output_dir, f"{base_name}_watermarked.pdf")
            
            if watermark_text:
                success = self.pdf_editor.add_watermark(watermark_text=watermark_text, output_path=output_file, **kwargs)
            elif watermark_image:
                success = self.pdf_editor.add_watermark(watermark_image=watermark_image, output_path=output_file, **kwargs)
            else:
                raise Exception("必须提供水印文本或水印图像")
            
            if not success:
                raise Exception("添加水印失败")
            
            return output_file
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, add_watermark_operation, output_dir, watermark_text, watermark_image, **kwargs): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"添加水印完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }
    
    def batch_ocr(self, input_files: List[str], output_dir: str, output_format: str = "pdf", **kwargs) -> Dict[str, Any]:
        """批量OCR处理
        
        Args:
            input_files: 输入PDF文件列表
            output_dir: 输出目录
            output_format: 输出格式 ("pdf", "txt", "docx")
            **kwargs:
                - language: OCR语言 (默认"chi_sim+eng")
                - image_preprocessing: 是否启用图像预处理 (默认True)
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置OCR参数
        language = kwargs.get("language", "chi_sim+eng")
        image_preprocessing = kwargs.get("image_preprocessing", True)
        self.ocr_engine.set_language(language)
        self.ocr_engine.set_image_preprocessing(image_preprocessing)
        
        # 定义OCR操作
        def ocr_operation(file_path, output_dir, output_format):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            
            if output_format == "pdf":
                # 导出可搜索PDF
                output_file = os.path.join(output_dir, f"{base_name}_searchable.pdf")
                if not self.ocr_engine.export_searchable_pdf(output_file):
                    raise Exception("导出可搜索PDF失败")
            
            elif output_format == "txt":
                # 导出纯文本
                output_file = os.path.join(output_dir, f"{base_name}_ocr.txt")
                result = self.ocr_engine.recognize_full_pdf()
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result.get("full_text", ""))
            
            elif output_format == "docx":
                # 导出Word文档
                output_file = os.path.join(output_dir, f"{base_name}_ocr.docx")
                result = self.ocr_engine.recognize_full_pdf()
                # 这里可以添加更复杂的Word文档生成逻辑
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result.get("full_text", ""))
            
            else:
                raise Exception(f"不支持的输出格式: {output_format}")
            
            return output_file
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, ocr_operation, output_dir, output_format): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"OCR完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }
    
    def batch_add_page_numbers(self, input_files: List[str], output_dir: str, **kwargs) -> Dict[str, Any]:
        """批量添加页码
        
        Args:
            input_files: 输入PDF文件列表
            output_dir: 输出目录
            **kwargs:
                - position: 页码位置 ("bottom-center", "bottom-left", "bottom-right", "top-center", "top-left", "top-right")
                - format: 页码格式 ("{page}", "{page}/{total}")
                - font_size: 字体大小
                - color: 颜色 (RGB元组)
        
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义添加页码操作
        def add_page_numbers_operation(file_path, output_dir, **kwargs):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            output_file = os.path.join(output_dir, f"{base_name}_paged.pdf")
            
            # 需要在editor.py中实现add_page_numbers方法
            if not hasattr(self.pdf_editor, "add_page_numbers"):
                raise NotImplementedError("添加页码功能尚未实现")
            
            if not self.pdf_editor.add_page_numbers(output_path=output_file, **kwargs):
                raise Exception("添加页码失败")
            
            return output_file
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, add_page_numbers_operation, output_dir, **kwargs): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"添加页码完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }
    
    def batch_compress(self, input_files: List[str], output_dir: str, quality: int = 85) -> Dict[str, Any]:
        """批量压缩PDF文件
        
        Args:
            input_files: 输入PDF文件列表
            output_dir: 输出目录
            quality: 压缩质量 (0-100)
        
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义压缩操作
        def compress_operation(file_path, output_dir, quality):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            output_file = os.path.join(output_dir, f"{base_name}_compressed.pdf")
            
            # 需要在converter.py或security.py中实现compress_pdf方法
            if hasattr(self.pdf_converter, "compress_pdf"):
                success = self.pdf_converter.compress_pdf(output_file, quality=quality)
            elif hasattr(self.pdf_security, "compress_pdf"):
                success = self.pdf_security.compress_pdf(output_file, quality=quality)
            else:
                raise NotImplementedError("压缩功能尚未实现")
            
            if not success:
                raise Exception("压缩失败")
            
            return output_file
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, compress_operation, output_dir, quality): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"压缩完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }
    
    def batch_encrypt(self, input_files: List[str], output_dir: str, user_password: str, owner_password: str = None, permissions: Dict = None) -> Dict[str, Any]:
        """批量加密PDF文件
        
        Args:
            input_files: 输入PDF文件列表
            output_dir: 输出目录
            user_password: 用户密码
            owner_password: 所有者密码
            permissions: 权限设置
        
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义加密操作
        def encrypt_operation(file_path, output_dir, user_password, owner_password, permissions):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            output_file = os.path.join(output_dir, f"{base_name}_encrypted.pdf")
            
            if not self.pdf_security.encrypt(user_password, output_file, owner_password, permissions):
                raise Exception("加密失败")
            
            return output_file
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, encrypt_operation, output_dir, user_password, owner_password, permissions): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"加密完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }
    
    def batch_decrypt(self, input_files: List[str], output_dir: str, password: str) -> Dict[str, Any]:
        """批量解密PDF文件
        
        Args:
            input_files: 输入PDF文件列表
            output_dir: 输出目录
            password: 密码
        
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        total_files = len(input_files)
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义解密操作
        def decrypt_operation(file_path, output_dir, password):
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0]
            output_file = os.path.join(output_dir, f"{base_name}_decrypted.pdf")
            
            if not self.pdf_security.decrypt(password, output_file):
                raise Exception("解密失败")
            
            return output_file
        
        # 批量处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, decrypt_operation, output_dir, password): file_path
                for file_path in input_files
            }
            
            for i, future in enumerate(as_completed(future_to_file)):
                result = future.result()
                results.append(result)
                
                # 更新进度
                progress = (i + 1) / total_files
                self._update_progress(progress, f"解密完成: {os.path.basename(result['file_path'])}")
        
        # 计算统计信息
        total_duration = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration": total_duration,
            "results": results
        }


# 示例用法
if __name__ == "__main__":
    # 创建批处理处理器
    processor = BatchProcessor(max_workers=2)
    
    # 设置进度回调
    def progress_callback(progress, status):
        print(f"进度: {progress*100:.1f}%, 状态: {status}")
    
    processor.set_progress_callback(progress_callback)
    
    # 批量转换示例
    print("开始批量转换...")
    result = processor.batch_convert(
        input_files=["test1.pdf", "test2.pdf"],
        output_format="txt",
        output_dir="./output"
    )
    print(f"转换完成: {result['success_count']}/{result['total_files']} 成功")
    
    # 批量合并示例
    print("开始批量合并...")
    result = processor.batch_merge(
        input_files=["test1.pdf", "test2.pdf"],
        output_path="./merged.pdf"
    )
    print(f"合并{result['success']}")
