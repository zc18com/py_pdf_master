#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件工具模块 - 提供文件操作相关的工具函数
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Optional, Tuple, Dict


def get_file_extension(file_path: str) -> str:
    """获取文件扩展名
    
    Args:
        file_path: 文件路径
    
    Returns:
        str: 文件扩展名（不包含点）
    """
    return os.path.splitext(file_path)[1].lower().lstrip('.')


def get_file_name(file_path: str) -> str:
    """获取文件名（包含扩展名）
    
    Args:
        file_path: 文件路径
    
    Returns:
        str: 文件名
    """
    return os.path.basename(file_path)


def get_file_name_without_extension(file_path: str) -> str:
    """获取文件名（不包含扩展名）
    
    Args:
        file_path: 文件路径
    
    Returns:
        str: 文件名（不包含扩展名）
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）
    
    Args:
        file_path: 文件路径
    
    Returns:
        int: 文件大小（字节）
    
    Raises:
        FileNotFoundError: 文件不存在
        PermissionError: 无权限访问文件
    """
    return os.path.getsize(file_path)


def get_file_size_human(file_path: str) -> str:
    """获取人类可读的文件大小
    
    Args:
        file_path: 文件路径
    
    Returns:
        str: 人类可读的文件大小（例如："1.2 MB"）
    """
    size = get_file_size(file_path)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def get_file_mime_type(file_path: str) -> str:
    """获取文件MIME类型
    
    Args:
        file_path: 文件路径
    
    Returns:
        str: 文件MIME类型
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def is_pdf_file(file_path: str) -> bool:
    """检查文件是否为PDF文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否为PDF文件
    """
    # 检查扩展名
    if get_file_extension(file_path) != "pdf":
        return False
    
    # 检查文件头
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False


def is_image_file(file_path: str) -> bool:
    """检查文件是否为图像文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否为图像文件
    """
    image_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif"]
    return get_file_extension(file_path) in image_extensions


def is_word_file(file_path: str) -> bool:
    """检查文件是否为Word文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否为Word文件
    """
    word_extensions = ["doc", "docx"]
    return get_file_extension(file_path) in word_extensions


def is_excel_file(file_path: str) -> bool:
    """检查文件是否为Excel文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否为Excel文件
    """
    excel_extensions = ["xls", "xlsx"]
    return get_file_extension(file_path) in excel_extensions


def is_powerpoint_file(file_path: str) -> bool:
    """检查文件是否为PowerPoint文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否为PowerPoint文件
    """
    ppt_extensions = ["ppt", "pptx"]
    return get_file_extension(file_path) in ppt_extensions


def is_text_file(file_path: str) -> bool:
    """检查文件是否为文本文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否为文本文件
    """
    text_extensions = ["txt", "csv", "md", "rtf"]
    return get_file_extension(file_path) in text_extensions


def list_files(directory: str, extensions: Optional[List[str]] = None, recursive: bool = False) -> List[str]:
    """列出目录中的文件
    
    Args:
        directory: 目录路径
        extensions: 文件扩展名列表（不包含点），如果为None则返回所有文件
        recursive: 是否递归列出子目录中的文件
    
    Returns:
        List[str]: 文件路径列表
    """
    file_list = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if extensions is None or get_file_extension(file) in extensions:
                    file_list.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                if extensions is None or get_file_extension(file) in extensions:
                    file_list.append(file_path)
    
    return file_list


def create_directory(directory: str, exist_ok: bool = True) -> bool:
    """创建目录
    
    Args:
        directory: 目录路径
        exist_ok: 如果目录已存在，是否抛出异常
    
    Returns:
        bool: 是否成功创建
    """
    try:
        os.makedirs(directory, exist_ok=exist_ok)
        return True
    except Exception:
        return False


def delete_file(file_path: str) -> bool:
    """删除文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否成功删除
    """
    try:
        os.remove(file_path)
        return True
    except Exception:
        return False


def delete_directory(directory: str, recursive: bool = False) -> bool:
    """删除目录
    
    Args:
        directory: 目录路径
        recursive: 是否递归删除目录及其内容
    
    Returns:
        bool: 是否成功删除
    """
    try:
        if recursive:
            shutil.rmtree(directory)
        else:
            os.rmdir(directory)
        return True
    except Exception:
        return False


def copy_file(src_path: str, dst_path: str, overwrite: bool = True) -> bool:
    """复制文件
    
    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
        overwrite: 如果目标文件已存在，是否覆盖
    
    Returns:
        bool: 是否成功复制
    """
    try:
        if not overwrite and os.path.exists(dst_path):
            return False
        shutil.copy2(src_path, dst_path)
        return True
    except Exception:
        return False


def move_file(src_path: str, dst_path: str, overwrite: bool = True) -> bool:
    """移动文件
    
    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
        overwrite: 如果目标文件已存在，是否覆盖
    
    Returns:
        bool: 是否成功移动
    """
    try:
        if not overwrite and os.path.exists(dst_path):
            return False
        shutil.move(src_path, dst_path)
        return True
    except Exception:
        return False


def rename_file(file_path: str, new_name: str) -> bool:
    """重命名文件
    
    Args:
        file_path: 文件路径
        new_name: 新文件名（包含扩展名）
    
    Returns:
        bool: 是否成功重命名
    """
    try:
        directory = os.path.dirname(file_path)
        new_path = os.path.join(directory, new_name)
        os.rename(file_path, new_path)
        return True
    except Exception:
        return False


def get_file_hash(file_path: str, hash_algorithm: str = "sha256") -> str:
    """获取文件哈希值
    
    Args:
        file_path: 文件路径
        hash_algorithm: 哈希算法（sha256、md5、sha1等）
    
    Returns:
        str: 文件哈希值
    """
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def get_temp_file_path(suffix: str = "", prefix: str = "", directory: Optional[str] = None) -> str:
    """获取临时文件路径
    
    Args:
        suffix: 文件后缀（包含点）
        prefix: 文件前缀
        directory: 临时文件目录
    
    Returns:
        str: 临时文件路径
    """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, dir=directory, delete=False) as f:
        return f.name


def get_unique_file_path(directory: str, file_name: str) -> str:
    """获取唯一的文件路径（如果文件已存在，添加数字后缀）
    
    Args:
        directory: 目录路径
        file_name: 文件名
    
    Returns:
        str: 唯一的文件路径
    """
    base_name = get_file_name_without_extension(file_name)
    extension = get_file_extension(file_name)
    
    counter = 1
    unique_path = os.path.join(directory, file_name)
    
    while os.path.exists(unique_path):
        unique_name = f"{base_name}_{counter}.{extension}"
        unique_path = os.path.join(directory, unique_name)
        counter += 1
    
    return unique_path


def read_text_file(file_path: str, encoding: str = "utf-8") -> str:
    """读取文本文件
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
    
    Returns:
        str: 文件内容
    """
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def write_text_file(file_path: str, content: str, encoding: str = "utf-8", overwrite: bool = True) -> bool:
    """写入文本文件
    
    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码
        overwrite: 如果文件已存在，是否覆盖
    
    Returns:
        bool: 是否成功写入
    """
    try:
        if not overwrite and os.path.exists(file_path):
            return False
        
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            create_directory(directory)
        
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def append_text_file(file_path: str, content: str, encoding: str = "utf-8") -> bool:
    """追加文本到文件
    
    Args:
        file_path: 文件路径
        content: 要追加的内容
        encoding: 文件编码
    
    Returns:
        bool: 是否成功追加
    """
    try:
        with open(file_path, "a", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def list_subdirectories(directory: str) -> List[str]:
    """列出目录中的子目录
    
    Args:
        directory: 目录路径
    
    Returns:
        List[str]: 子目录路径列表
    """
    subdirs = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            subdirs.append(item_path)
    return subdirs


def get_parent_directory(file_path: str) -> str:
    """获取父目录
    
    Args:
        file_path: 文件或目录路径
    
    Returns:
        str: 父目录路径
    """
    return os.path.dirname(file_path)


def normalize_path(path: str) -> str:
    """规范化路径
    
    Args:
        path: 路径
    
    Returns:
        str: 规范化后的路径
    """
    return os.path.normpath(path)


def absolute_path(path: str) -> str:
    """获取绝对路径
    
    Args:
        path: 路径
    
    Returns:
        str: 绝对路径
    """
    return os.path.abspath(path)


def resolve_path(path: str) -> str:
    """解析路径（规范化并获取绝对路径）
    
    Args:
        path: 路径
    
    Returns:
        str: 解析后的路径
    """
    return os.path.realpath(path)


def path_exists(path: str) -> bool:
    """检查路径是否存在
    
    Args:
        path: 路径
    
    Returns:
        bool: 是否存在
    """
    return os.path.exists(path)


def is_directory(path: str) -> bool:
    """检查路径是否为目录
    
    Args:
        path: 路径
    
    Returns:
        bool: 是否为目录
    """
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    """检查路径是否为文件
    
    Args:
        path: 路径
    
    Returns:
        bool: 是否为文件
    """
    return os.path.isfile(path)


def get_disk_space(drive: str) -> Tuple[int, int, int]:
    """获取磁盘空间信息
    
    Args:
        drive: 驱动器路径（如"C:\"）
    
    Returns:
        Tuple[int, int, int]: 总空间（字节）、已用空间（字节）、可用空间（字节）
    """
    total, used, free = shutil.disk_usage(drive)
    return total, used, free


def get_disk_space_human(drive: str) -> Dict[str, str]:
    """获取人类可读的磁盘空间信息
    
    Args:
        drive: 驱动器路径（如"C:\"）
    
    Returns:
        Dict[str, str]: 包含总空间、已用空间、可用空间的字典
    """
    total, used, free = get_disk_space(drive)
    
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    return {
        "total": format_size(total),
        "used": format_size(used),
        "free": format_size(free)
    }


# 示例用法
if __name__ == "__main__":
    # 测试文件工具函数
    test_file = __file__
    print(f"文件名: {get_file_name(test_file)}")
    print(f"文件名（不含扩展名）: {get_file_name_without_extension(test_file)}")
    print(f"文件扩展名: {get_file_extension(test_file)}")
    print(f"文件大小: {get_file_size(test_file)} 字节")
    print(f"文件大小（人类可读）: {get_file_size_human(test_file)}")
    print(f"文件MIME类型: {get_file_mime_type(test_file)}")
    print(f"是否为PDF文件: {is_pdf_file(test_file)}")
    print(f"是否为Python文件: {get_file_extension(test_file) == 'py'}")
    print(f"文件SHA256哈希值: {get_file_hash(test_file)}")
    print(f"文件绝对路径: {absolute_path(test_file)}")
    print(f"文件所在目录: {get_parent_directory(test_file)}")
