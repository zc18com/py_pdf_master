#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF安全模块 - 提供PDF文件的安全与保护功能
"""

import fitz
import pikepdf
import os
import tempfile
from typing import Optional, Dict, Any, List


class PDFSecurity:
    """PDF安全类，提供PDF文件的安全与保护功能"""
    
    def __init__(self):
        self.pdf_parser = None
    
    def set_parser(self, parser):
        """设置PDF解析器"""
        self.pdf_parser = parser
    
    def encrypt(self, 
                user_password: Optional[str] = None,
                owner_password: Optional[str] = None,
                permissions: Optional[Dict[str, bool]] = None,
                output_path: Optional[str] = None
                ) -> bool:
        """
        加密PDF文件
        
        Args:
            user_password: 用户密码（打开密码）
            owner_password: 所有者密码（权限密码）
            permissions: 权限设置
            output_path: 输出路径，如果为None则覆盖原文件
            
        Returns:
            bool: 是否成功加密
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return False
            
            # 权限默认值
            default_permissions = {
                "print": True,
                "modify": True,
                "copy": True,
                "annot_form": True,
                "fill_form": True,
                "extract": True,
                "assemble": True,
                "print_high": True
            }
            
            # 更新权限
            if permissions:
                default_permissions.update(permissions)
            
            # 使用PyMuPDF加密
            doc = self.pdf_parser.document
            
            # 设置权限标志
            permission_flags = 0
            if default_permissions["print"]:
                permission_flags |= 4
            if default_permissions["modify"]:
                permission_flags |= 8
            if default_permissions["copy"]:
                permission_flags |= 16
            if default_permissions["annot_form"]:
                permission_flags |= 32
            if default_permissions["fill_form"]:
                permission_flags |= 256
            if default_permissions["extract"]:
                permission_flags |= 128
            if default_permissions["assemble"]:
                permission_flags |= 512
            if default_permissions["print_high"]:
                permission_flags |= 2048
            
            # 保存加密后的PDF
            if output_path:
                doc.save(output_path, 
                         encryption=permission_flags, 
                         owner_pw=owner_password, 
                         user_pw=user_password)
            else:
                doc.save(self.pdf_parser.file_path, 
                         encryption=permission_flags, 
                         owner_pw=owner_password, 
                         user_pw=user_password)
            
            return True
            
        except Exception as e:
            print(f"加密PDF失败: {e}")
            return False
    
    def decrypt(self, password: str, output_path: Optional[str] = None) -> bool:
        """
        解密PDF文件
        
        Args:
            password: 解密密码（用户密码或所有者密码）
            output_path: 输出路径，如果为None则覆盖原文件
            
        Returns:
            bool: 是否成功解密
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.file_path:
                return False
            
            # 使用pikepdf解密
            with pikepdf.open(self.pdf_parser.file_path, password=password) as pdf:
                if output_path:
                    pdf.save(output_path)
                else:
                    # 保存到临时文件，然后替换原文件
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
                        temp_path = temp.name
                    pdf.save(temp_path)
                    
                    # 关闭当前文档
                    self.pdf_parser.close()
                    
                    # 替换原文件
                    os.replace(temp_path, self.pdf_parser.file_path)
                    
                    # 重新打开文件
                    self.pdf_parser.open_pdf(self.pdf_parser.file_path)
            
            return True
            
        except Exception as e:
            print(f"解密PDF失败: {e}")
            return False
    
    def remove_password(self, output_path: Optional[str] = None) -> bool:
        """
        移除PDF密码保护（如果已知密码）
        
        Args:
            output_path: 输出路径，如果为None则覆盖原文件
            
        Returns:
            bool: 是否成功移除密码
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.file_path:
                return False
            
            # 检查是否加密
            if not self.pdf_parser.is_encrypted:
                return True
            
            # 使用pikepdf尝试解密（无密码）
            try:
                with pikepdf.open(self.pdf_parser.file_path) as pdf:
                    if output_path:
                        pdf.save(output_path)
                    else:
                        # 保存到临时文件，然后替换原文件
                        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
                            temp_path = temp.name
                        pdf.save(temp_path)
                        
                        # 关闭当前文档
                        self.pdf_parser.close()
                        
                        # 替换原文件
                        os.replace(temp_path, self.pdf_parser.file_path)
                        
                        # 重新打开文件
                        self.pdf_parser.open_pdf(self.pdf_parser.file_path)
                
                return True
                
            except pikepdf.PasswordError:
                print("需要密码才能移除保护")
                return False
                
        except Exception as e:
            print(f"移除密码保护失败: {e}")
            return False
    
    def clean_metadata(self, output_path: Optional[str] = None) -> bool:
        """
        清理PDF元数据
        
        Args:
            output_path: 输出路径，如果为None则覆盖原文件
            
        Returns:
            bool: 是否成功清理
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return False
            
            # 获取当前元数据
            metadata = self.pdf_parser.get_metadata()
            
            # 创建新的元数据（仅保留必要字段）
            clean_metadata = {
                "title": "",
                "author": "",
                "subject": "",
                "keywords": "",
                "creator": "PDF Master Suite",
                "producer": "PDF Master Suite",
                "creationDate": metadata.get("creationDate", ""),
                "modDate": metadata.get("modDate", ""),
            }
            
            # 设置清理后的元数据
            doc = self.pdf_parser.document
            doc.set_metadata(clean_metadata)
            
            # 保存文件
            if output_path:
                doc.save(output_path)
            else:
                doc.save(self.pdf_parser.file_path)
            
            return True
            
        except Exception as e:
            print(f"清理元数据失败: {e}")
            return False
    
    def redact_text(self, 
                   page_num: int, 
                   text: str, 
                   color: tuple = (0, 0, 0),  # RGB黑色
                   case_sensitive: bool = False
                   ) -> bool:
        """
        红action（涂黑）指定文本
        
        Args:
            page_num: 页码（从0开始）
            text: 要红action的文本
            color: 红action颜色（RGB）
            case_sensitive: 是否区分大小写
            
        Returns:
            bool: 是否成功红action
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return False
            
            # 获取页面
            page = self.pdf_parser.get_page(page_num)
            if not page:
                return False
            
            # 搜索文本
            flags = 0
            if not case_sensitive:
                flags |= fitz.TEXT_CASELESS
            
            instances = page.search_for(text, flags=flags)
            
            # 红action文本
            for instance in instances:
                # 创建红action区域
                page.add_redact_annot(instance)
            
            # 应用红action
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            
            return True
            
        except Exception as e:
            print(f"红action文本失败: {e}")
            return False
    
    def redact_area(self, 
                   page_num: int, 
                   rect: tuple,  # (x0, y0, x1, y1)
                   color: tuple = (0, 0, 0)  # RGB黑色
                   ) -> bool:
        """
        红action指定区域
        
        Args:
            page_num: 页码（从0开始）
            rect: 红action区域 (x0, y0, x1, y1)
            color: 红action颜色（RGB）
            
        Returns:
            bool: 是否成功红action
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.document:
                return False
            
            # 获取页面
            page = self.pdf_parser.get_page(page_num)
            if not page:
                return False
            
            # 创建红action区域
            page.add_redact_annot(fitz.Rect(*rect))
            
            # 应用红action
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            
            return True
            
        except Exception as e:
            print(f"红action区域失败: {e}")
            return False
    
    def get_permissions(self) -> Optional[Dict[str, bool]]:
        """
        获取PDF文件的权限信息
        
        Returns:
            Optional[Dict[str, bool]]: 权限信息
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.file_path:
                return None
            
            # 使用pikepdf获取权限
            with pikepdf.open(self.pdf_parser.file_path) as pdf:
                permissions = {
                    "encrypted": pdf.is_encrypted,
                    "print": pdf.permissions.print,
                    "modify": pdf.permissions.modify,
                    "copy": pdf.permissions.extract_text,
                    "annot_form": pdf.permissions.modify_annotation,
                    "fill_form": pdf.permissions.fill_form,
                    "extract": pdf.permissions.extract_text,
                    "assemble": pdf.permissions.assemble_document,
                    "print_high": pdf.permissions.print_high_resolution
                }
                
                return permissions
                
        except Exception as e:
            print(f"获取权限信息失败: {e}")
            return None
    
    def repair_pdf(self, output_path: Optional[str] = None) -> bool:
        """
        修复损坏的PDF文件
        
        Args:
            output_path: 输出路径，如果为None则覆盖原文件
            
        Returns:
            bool: 是否成功修复
        """
        try:
            if not self.pdf_parser or not self.pdf_parser.file_path:
                return False
            
            # 使用PyMuPDF尝试修复
            doc = fitz.open(self.pdf_parser.file_path)
            
            # 保存修复后的PDF
            if output_path:
                doc.save(output_path)
            else:
                doc.save(self.pdf_parser.file_path)
            
            doc.close()
            return True
            
        except Exception as e:
            print(f"修复PDF失败: {e}")
            return False


# 示例用法
if __name__ == "__main__":
    from src.core.pdf_parser import PDFParser
    
    # 创建PDF解析器和安全类
    parser = PDFParser()
    security = PDFSecurity()
    security.set_parser(parser)
    
    # 打开PDF文件
    if parser.open_pdf("test.pdf"):
        # 加密PDF
        security.encrypt(
            user_password="user123",
            owner_password="owner123",
            permissions={
                "print": True,
                "copy": False,
                "modify": False
            },
            output_path="encrypted.pdf"
        )
        
        # 关闭PDF文件
        parser.close()
