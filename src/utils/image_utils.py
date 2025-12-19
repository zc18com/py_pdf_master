#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像工具模块 - 提供图像处理相关的工具函数
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional, Tuple, List, Dict, Any


def load_image(image_path: str) -> Image.Image:
    """加载图像
    
    Args:
        image_path: 图像路径
    
    Returns:
        Image.Image: PIL图像对象
    """
    return Image.open(image_path)


def save_image(image: Image.Image, output_path: str, quality: int = 95) -> bool:
    """保存图像
    
    Args:
        image: PIL图像对象
        output_path: 输出路径
        quality: 保存质量（1-100）
    
    Returns:
        bool: 是否成功保存
    """
    try:
        image.save(output_path, quality=quality)
        return True
    except Exception:
        return False


def convert_to_pil(image: np.ndarray) -> Image.Image:
    """将OpenCV图像转换为PIL图像
    
    Args:
        image: OpenCV图像数组
    
    Returns:
        Image.Image: PIL图像对象
    """
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def convert_to_cv(image: Image.Image) -> np.ndarray:
    """将PIL图像转换为OpenCV图像
    
    Args:
        image: PIL图像对象
    
    Returns:
        np.ndarray: OpenCV图像数组
    """
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def resize_image(image: Image.Image, width: Optional[int] = None, height: Optional[int] = None, keep_aspect_ratio: bool = True) -> Image.Image:
    """调整图像大小
    
    Args:
        image: PIL图像对象
        width: 目标宽度
        height: 目标高度
        keep_aspect_ratio: 是否保持宽高比
    
    Returns:
        Image.Image: 调整后的图像
    """
    if not keep_aspect_ratio:
        return image.resize((width, height), Image.LANCZOS)
    
    original_width, original_height = image.size
    
    if width is None and height is None:
        return image
    
    if width is None:
        ratio = height / original_height
        new_width = int(original_width * ratio)
        return image.resize((new_width, height), Image.LANCZOS)
    
    if height is None:
        ratio = width / original_width
        new_height = int(original_height * ratio)
        return image.resize((width, new_height), Image.LANCZOS)
    
    # 计算最佳比例
    ratio_width = width / original_width
    ratio_height = height / original_height
    ratio = min(ratio_width, ratio_height)
    
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    return image.resize((new_width, new_height), Image.LANCZOS)


def crop_image(image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    """裁剪图像
    
    Args:
        image: PIL图像对象
        left: 左边界
        top: 上边界
        right: 右边界
        bottom: 下边界
    
    Returns:
        Image.Image: 裁剪后的图像
    """
    return image.crop((left, top, right, bottom))


def rotate_image(image: Image.Image, angle: float, expand: bool = True) -> Image.Image:
    """旋转图像
    
    Args:
        image: PIL图像对象
        angle: 旋转角度（度）
        expand: 是否扩展画布以包含整个图像
    
    Returns:
        Image.Image: 旋转后的图像
    """
    return image.rotate(angle, expand=expand, resample=Image.BICUBIC)


def flip_image(image: Image.Image, horizontal: bool = False, vertical: bool = False) -> Image.Image:
    """翻转图像
    
    Args:
        image: PIL图像对象
        horizontal: 是否水平翻转
        vertical: 是否垂直翻转
    
    Returns:
        Image.Image: 翻转后的图像
    """
    if horizontal and vertical:
        return image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)
    elif horizontal:
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    elif vertical:
        return image.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        return image


def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
    """调整图像亮度
    
    Args:
        image: PIL图像对象
        factor: 亮度因子（0.0-2.0）
    
    Returns:
        Image.Image: 调整后的图像
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
    """调整图像对比度
    
    Args:
        image: PIL图像对象
        factor: 对比度因子（0.0-2.0）
    
    Returns:
        Image.Image: 调整后的图像
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def adjust_saturation(image: Image.Image, factor: float) -> Image.Image:
    """调整图像饱和度
    
    Args:
        image: PIL图像对象
        factor: 饱和度因子（0.0-2.0）
    
    Returns:
        Image.Image: 调整后的图像
    """
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)


def adjust_sharpness(image: Image.Image, factor: float) -> Image.Image:
    """调整图像锐度
    
    Args:
        image: PIL图像对象
        factor: 锐度因子（0.0-2.0）
    
    Returns:
        Image.Image: 调整后的图像
    """
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)


def convert_to_grayscale(image: Image.Image) -> Image.Image:
    """将图像转换为灰度图
    
    Args:
        image: PIL图像对象
    
    Returns:
        Image.Image: 灰度图
    """
    return image.convert("L")


def convert_to_binary(image: Image.Image, threshold: int = 128) -> Image.Image:
    """将图像转换为二值图
    
    Args:
        image: PIL图像对象
        threshold: 阈值（0-255）
    
    Returns:
        Image.Image: 二值图
    """
    return image.convert("L").point(lambda p: p > threshold and 255)


def adaptive_threshold(image: Image.Image, block_size: int = 11, C: int = 2) -> Image.Image:
    """自适应阈值处理
    
    Args:
        image: PIL图像对象
        block_size: 块大小
        C: 常数
    
    Returns:
        Image.Image: 处理后的图像
    """
    img_cv = convert_to_cv(image)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C)
    return convert_to_pil(binary)


def denoise_image(image: Image.Image, strength: int = 3) -> Image.Image:
    """去噪处理
    
    Args:
        image: PIL图像对象
        strength: 去噪强度（1-9）
    
    Returns:
        Image.Image: 去噪后的图像
    """
    img_cv = convert_to_cv(image)
    denoised = cv2.medianBlur(img_cv, strength)
    return convert_to_pil(denoised)


def sharpen_image(image: Image.Image, radius: float = 1.0, percent: float = 100.0) -> Image.Image:
    """锐化图像
    
    Args:
        image: PIL图像对象
        radius: 锐化半径
        percent: 锐化百分比
    
    Returns:
        Image.Image: 锐化后的图像
    """
    # 锐化滤镜
    sharpen_filter = ImageFilter.SHARPEN
    return image.filter(sharpen_filter)


def blur_image(image: Image.Image, radius: float = 2.0) -> Image.Image:
    """模糊图像
    
    Args:
        image: PIL图像对象
        radius: 模糊半径
    
    Returns:
        Image.Image: 模糊后的图像
    """
    return image.filter(ImageFilter.GaussianBlur(radius))


def enhance_edges(image: Image.Image) -> Image.Image:
    """增强边缘
    
    Args:
        image: PIL图像对象
    
    Returns:
        Image.Image: 边缘增强后的图像
    """
    return image.filter(ImageFilter.EDGE_ENHANCE_MORE)


def detect_edges(image: Image.Image) -> Image.Image:
    """边缘检测
    
    Args:
        image: PIL图像对象
    
    Returns:
        Image.Image: 边缘图像
    """
    img_cv = convert_to_cv(image)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return convert_to_pil(edges)


def get_image_dimensions(image: Image.Image) -> Tuple[int, int]:
    """获取图像尺寸
    
    Args:
        image: PIL图像对象
    
    Returns:
        Tuple[int, int]: (宽度, 高度)
    """
    return image.size


def get_image_channels(image: Image.Image) -> int:
    """获取图像通道数
    
    Args:
        image: PIL图像对象
    
    Returns:
        int: 通道数（1-灰度图，3-RGB，4-RGBA）
    """
    return len(image.getbands())


def get_image_histogram(image: Image.Image) -> Dict[str, List[int]]:
    """获取图像直方图
    
    Args:
        image: PIL图像对象
    
    Returns:
        Dict[str, List[int]]: 直方图数据
    """
    histogram = {
        "r": [],
        "g": [],
        "b": [],
        "l": []
    }
    
    # 获取RGB通道直方图
    if image.mode == "RGB" or image.mode == "RGBA":
        r, g, b = image.split()
        histogram["r"] = list(r.histogram())
        histogram["g"] = list(g.histogram())
        histogram["b"] = list(b.histogram())
    
    # 获取灰度直方图
    gray_image = image.convert("L")
    histogram["l"] = list(gray_image.histogram())
    
    return histogram


def calculate_image_dpi(image: Image.Image) -> Tuple[int, int]:
    """计算图像DPI
    
    Args:
        image: PIL图像对象
    
    Returns:
        Tuple[int, int]: (x_dpi, y_dpi)
    """
    dpi = image.info.get("dpi", (72, 72))
    return dpi


def set_image_dpi(image: Image.Image, dpi: Tuple[int, int] = (300, 300)) -> Image.Image:
    """设置图像DPI
    
    Args:
        image: PIL图像对象
        dpi: DPI值
    
    Returns:
        Image.Image: 设置DPI后的图像
    """
    image = image.copy()
    image.info["dpi"] = dpi
    return image


def add_watermark(image: Image.Image, watermark: Image.Image, position: Tuple[int, int] = (0, 0), opacity: float = 0.5) -> Image.Image:
    """添加水印
    
    Args:
        image: 原始图像
        watermark: 水印图像
        position: 水印位置 (x, y)
        opacity: 水印透明度（0.0-1.0）
    
    Returns:
        Image.Image: 添加水印后的图像
    """
    # 创建透明图层
    watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    
    # 调整水印大小
    watermark_width, watermark_height = watermark.size
    image_width, image_height = image.size
    
    # 如果水印太大，缩小水印
    if watermark_width > image_width * 0.5 or watermark_height > image_height * 0.5:
        watermark = resize_image(watermark, width=int(image_width * 0.3), height=int(image_height * 0.3))
        watermark_width, watermark_height = watermark.size
    
    # 如果位置超出范围，居中放置
    if position[0] + watermark_width > image_width or position[1] + watermark_height > image_height:
        position = ((image_width - watermark_width) // 2, (image_height - watermark_height) // 2)
    
    # 将水印粘贴到透明图层
    watermark_layer.paste(watermark, position)
    
    # 调整水印透明度
    if watermark.mode != "RGBA":
        watermark_layer = watermark_layer.convert("RGBA")
    
    r, g, b, a = watermark_layer.split()
    a = a.point(lambda p: p * opacity)
    watermark_layer = Image.merge("RGBA", (r, g, b, a))
    
    # 将水印图层与原始图像合并
    result = Image.alpha_composite(image.convert("RGBA"), watermark_layer)
    
    return result.convert(image.mode)


def add_text_watermark(image: Image.Image, text: str, position: Tuple[int, int] = (0, 0), font_path: Optional[str] = None, font_size: int = 36, color: Tuple[int, int, int, int] = (255, 255, 255, 128), rotation: float = 0) -> Image.Image:
    """添加文本水印
    
    Args:
        image: 原始图像
        text: 水印文本
        position: 水印位置 (x, y)
        font_path: 字体路径
        font_size: 字体大小
        color: 字体颜色 (R, G, B, A)
        rotation: 旋转角度
    
    Returns:
        Image.Image: 添加水印后的图像
    """
    from PIL import ImageDraw, ImageFont
    
    # 创建透明图层
    watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    
    # 绘制文本
    draw = ImageDraw.Draw(watermark_layer)
    
    # 加载字体
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # 计算文本位置
    text_width, text_height = draw.textsize(text, font=font)
    image_width, image_height = image.size
    
    # 如果位置超出范围，居中放置
    if position[0] + text_width > image_width or position[1] + text_height > image_height:
        position = ((image_width - text_width) // 2, (image_height - text_height) // 2)
    
    # 绘制文本
    draw.text(position, text, fill=color, font=font)
    
    # 旋转文本
    if rotation != 0:
        watermark_layer = rotate_image(watermark_layer, rotation, expand=False)
    
    # 将水印图层与原始图像合并
    result = Image.alpha_composite(image.convert("RGBA"), watermark_layer)
    
    return result.convert(image.mode)


def extract_text_from_image(image: Image.Image, language: str = "eng") -> str:
    """从图像中提取文本
    
    Args:
        image: PIL图像对象
        language: OCR语言
    
    Returns:
        str: 提取的文本
    """
    try:
        import pytesseract
        return pytesseract.image_to_string(image, lang=language)
    except Exception as e:
        print(f"OCR提取失败: {e}")
        return ""


def compare_images(image1: Image.Image, image2: Image.Image) -> float:
    """比较两张图像的相似度
    
    Args:
        image1: 第一张图像
        image2: 第二张图像
    
    Returns:
        float: 相似度（0.0-1.0）
    """
    # 调整图像大小
    image1 = resize_image(image1, width=512, height=512)
    image2 = resize_image(image2, width=512, height=512)
    
    # 转换为灰度图
    gray1 = convert_to_cv(convert_to_grayscale(image1))
    gray2 = convert_to_cv(convert_to_grayscale(image2))
    
    # 计算直方图
    hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
    
    # 归一化直方图
    cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    
    # 计算相似度
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    
    # 确保相似度在0.0-1.0之间
    similarity = (similarity + 1) / 2
    
    return similarity


def optimize_image(image: Image.Image, quality: int = 85, format: str = "JPEG", progressive: bool = True) -> Image.Image:
    """优化图像
    
    Args:
        image: PIL图像对象
        quality: 图像质量
        format: 图像格式
        progressive: 是否使用渐进式压缩
    
    Returns:
        Image.Image: 优化后的图像
    """
    from io import BytesIO
    
    output = BytesIO()
    image.save(output, format=format, quality=quality, progressive=progressive, optimize=True)
    output.seek(0)
    return Image.open(output)


def get_image_exif_data(image: Image.Image) -> Dict[str, Any]:
    """获取图像EXIF数据
    
    Args:
        image: PIL图像对象
    
    Returns:
        Dict[str, Any]: EXIF数据
    """
    try:
        from PIL.ExifTags import TAGS
        exif_data = {}
        exif = image._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_data[tag] = value
        return exif_data
    except Exception:
        return {}


# 示例用法
if __name__ == "__main__":
    # 测试图像工具函数
    try:
        # 加载示例图像
        test_image = Image.open("test_image.jpg")
    except Exception:
        # 创建测试图像
        test_image = Image.new("RGB", (500, 300), color=(255, 255, 255))
        draw = ImageDraw.Draw(test_image)
        draw.text((50, 50), "Test Image", fill=(0, 0, 0))
    
    print(f"图像尺寸: {get_image_dimensions(test_image)}")
    print(f"图像通道数: {get_image_channels(test_image)}")
    print(f"图像DPI: {calculate_image_dpi(test_image)}")
    
    # 调整大小
    resized = resize_image(test_image, width=300)
    print(f"调整后尺寸: {get_image_dimensions(resized)}")
    
    # 转换为灰度图
    gray = convert_to_grayscale(test_image)
    print(f"灰度图通道数: {get_image_channels(gray)}")
    
    # 保存测试结果
    test_image.save("original.jpg")
    resized.save("resized.jpg")
    gray.save("gray.jpg")
    
    print("测试完成，生成了original.jpg, resized.jpg, gray.jpg")
