#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志工具模块 - 提供日志记录功能
"""

import os
import sys
import logging
import logging.handlers
import datetime
import json
from typing import Dict, Any, Optional, List


class Logger:
    """日志记录器类"""
    
    def __init__(self, name: str = "PDFMasterSuite", level: int = logging.INFO):
        """初始化日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
        """
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # 避免日志重复输出
        
        # 日志格式
        self.formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 控制台处理器
        self.console_handler = None
        
        # 文件处理器
        self.file_handler = None
        
        # JSON文件处理器
        self.json_file_handler = None
        
        # 初始化控制台输出
        self.enable_console_output()
    
    def set_level(self, level: int):
        """设置日志级别
        
        Args:
            level: 日志级别
        """
        self.logger.setLevel(level)
    
    def enable_console_output(self, level: Optional[int] = None):
        """启用控制台输出
        
        Args:
            level: 日志级别
        """
        if self.console_handler:
            self.logger.removeHandler(self.console_handler)
        
        self.console_handler = logging.StreamHandler(sys.stdout)
        if level:
            self.console_handler.setLevel(level)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)
    
    def disable_console_output(self):
        """禁用控制台输出"""
        if self.console_handler:
            self.logger.removeHandler(self.console_handler)
            self.console_handler = None
    
    def enable_file_output(self, log_file: str, level: Optional[int] = None, max_bytes: int = 10*1024*1024, backup_count: int = 5):
        """启用文件输出
        
        Args:
            log_file: 日志文件路径
            level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 备份文件数量
        """
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self.file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        
        if level:
            self.file_handler.setLevel(level)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
    
    def disable_file_output(self):
        """禁用文件输出"""
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.file_handler = None
    
    def enable_json_file_output(self, log_file: str, level: Optional[int] = None, max_bytes: int = 10*1024*1024, backup_count: int = 5):
        """启用JSON格式文件输出
        
        Args:
            log_file: 日志文件路径
            level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 备份文件数量
        """
        if self.json_file_handler:
            self.logger.removeHandler(self.json_file_handler)
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        class JSONFormatter(logging.Formatter):
            """JSON格式日志格式化器"""
            
            def format(self, record: logging.LogRecord) -> str:
                log_data = {
                    "timestamp": datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f"[:-3]),
                    "name": record.name,
                    "level": record.levelname,
                    "filename": record.filename,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "message": record.getMessage(),
                }
                
                # 添加异常信息
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                
                return json.dumps(log_data, ensure_ascii=False)
        
        self.json_file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        
        json_formatter = JSONFormatter()
        if level:
            self.json_file_handler.setLevel(level)
        self.json_file_handler.setFormatter(json_formatter)
        self.logger.addHandler(self.json_file_handler)
    
    def disable_json_file_output(self):
        """禁用JSON格式文件输出"""
        if self.json_file_handler:
            self.logger.removeHandler(self.json_file_handler)
            self.json_file_handler = None
    
    def debug(self, message: str, **kwargs):
        """记录调试信息
        
        Args:
            message: 日志消息
            **kwargs: 额外参数
        """
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """记录普通信息
        
        Args:
            message: 日志消息
            **kwargs: 额外参数
        """
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告信息
        
        Args:
            message: 日志消息
            **kwargs: 额外参数
        """
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误信息
        
        Args:
            message: 日志消息
            **kwargs: 额外参数
        """
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误信息
        
        Args:
            message: 日志消息
            **kwargs: 额外参数
        """
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, exc_info: bool = True, **kwargs):
        """记录异常信息
        
        Args:
            message: 日志消息
            exc_info: 是否包含异常信息
            **kwargs: 额外参数
        """
        self.logger.exception(message, exc_info=exc_info, **kwargs)
    
    def log(self, level: int, message: str, **kwargs):
        """记录指定级别的日志
        
        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 额外参数
        """
        self.logger.log(level, message, **kwargs)
    
    def __del__(self):
        """关闭日志处理器"""
        if self.console_handler:
            self.console_handler.close()
        
        if self.file_handler:
            self.file_handler.close()
        
        if self.json_file_handler:
            self.json_file_handler.close()


# 全局日志记录器
_global_logger = None


def get_logger(name: str = "PDFMasterSuite", level: int = logging.INFO) -> Logger:
    """获取全局日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    
    Returns:
        Logger: 日志记录器
    """
    global _global_logger
    if not _global_logger:
        _global_logger = Logger(name, level)
    return _global_logger


def set_global_logger(logger: Logger):
    """设置全局日志记录器
    
    Args:
        logger: 日志记录器
    """
    global _global_logger
    _global_logger = logger


def configure_logger(
    name: str = "PDFMasterSuite",
    level: int = logging.INFO,
    console_level: Optional[int] = None,
    log_file: Optional[str] = None,
    file_level: Optional[int] = None,
    max_bytes: int = 10*1024*1024,
    backup_count: int = 5,
    json_log_file: Optional[str] = None,
    json_file_level: Optional[int] = None
) -> Logger:
    """配置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        console_level: 控制台日志级别
        log_file: 日志文件路径
        file_level: 文件日志级别
        max_bytes: 单个日志文件最大字节数
        backup_count: 备份文件数量
        json_log_file: JSON日志文件路径
        json_file_level: JSON文件日志级别
    
    Returns:
        Logger: 配置好的日志记录器
    """
    logger = Logger(name, level)
    
    if console_level:
        logger.enable_console_output(console_level)
    
    if log_file:
        logger.enable_file_output(log_file, file_level, max_bytes, backup_count)
    
    if json_log_file:
        logger.enable_json_file_output(json_log_file, json_file_level, max_bytes, backup_count)
    
    set_global_logger(logger)
    return logger


# 便捷的日志函数
def debug(message: str, **kwargs):
    """记录调试信息
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
    get_logger().debug(message, **kwargs)

def info(message: str, **kwargs):
    """记录普通信息
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
    get_logger().info(message, **kwargs)

def warning(message: str, **kwargs):
    """记录警告信息
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
    get_logger().warning(message, **kwargs)

def error(message: str, **kwargs):
    """记录错误信息
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
    get_logger().error(message, **kwargs)

def critical(message: str, **kwargs):
    """记录严重错误信息
    
    Args:
        message: 日志消息
        **kwargs: 额外参数
    """
    get_logger().critical(message, **kwargs)

def exception(message: str, exc_info: bool = True, **kwargs):
    """记录异常信息
    
    Args:
        message: 日志消息
        exc_info: 是否包含异常信息
        **kwargs: 额外参数
    """
    get_logger().exception(message, exc_info=exc_info, **kwargs)

def log(level: int, message: str, **kwargs):
    """记录指定级别的日志
    
    Args:
        level: 日志级别
        message: 日志消息
        **kwargs: 额外参数
    """
    get_logger().log(level, message, **kwargs)


# 日志级别常量
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


# 示例用法
if __name__ == "__main__":
    # 配置日志记录器
    logger = configure_logger(
        name="PDFMasterSuite",
        level=logging.DEBUG,
        console_level=logging.INFO,
        log_file="./logs/app.log",
        file_level=logging.DEBUG,
        json_log_file="./logs/app.json",
        json_file_level=logging.INFO
    )
    
    # 记录日志
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误信息")
    
    # 记录异常
    try:
        1 / 0
    except Exception as e:
        logger.exception("发生异常")
    
    # 使用便捷函数
    debug("便捷的调试信息")
    info("便捷的普通信息")
    warning("便捷的警告信息")
    error("便捷的错误信息")
    critical("便捷的严重错误信息")
