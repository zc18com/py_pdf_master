# PDF全能工具箱 (PDF Master Suite)

一个跨平台、功能全面的PDF处理软件，支持PDF查看、编辑、格式转换、文档管理等核心功能。

## 功能特性

### 📖 PDF查看器
- ✅ 支持打开多个PDF文件
- ✅ 页面导航（上一页/下一页/跳转）
- ✅ 缩放控制（25%-400%）
- ✅ 页面旋转（90°/180°/270°）
- ✅ 单页/双页/连续滚动模式
- ✅ 全屏模式
- ✅ 书签导航
- ✅ 页面缩略图侧边栏
- ✅ 搜索文本功能（高亮显示结果）

### ✏️ PDF编辑器
- ✅ 页面提取/删除
- ✅ 页面重新排序
- ✅ 页面旋转
- ✅ 空白页插入
- ✅ 文本添加/编辑（基于OCR）
- ✅ 图像插入/替换
- ✅ 形状绘制
- ✅ 注释工具（高亮、下划线、删除线）
- ✅ 水印添加（文字/图片）

### 🔄 格式转换
- ✅ PDF → Word (.docx) 保持格式
- ✅ PDF → Excel (.xlsx) 表格提取
- ✅ PDF → PowerPoint (.pptx)
- ✅ PDF → 图片（PNG/JPEG/TIFF）
- ✅ PDF → 纯文本 (.txt)
- ✅ PDF → HTML (保持布局)
- ✅ Word/Excel/PPT → PDF
- ✅ 图片 → PDF（单张/多张合并）

### 🔒 安全与保护
- ✅ 密码保护（用户密码/所有者密码）
- ✅ 权限设置（打印/复制/编辑限制）
- ✅ 移除密码保护
- ✅ 数字签名
- ✅ 敏感信息红action
- ✅ 元数据清理

### 📊 OCR功能
- ✅ 多语言OCR支持
- ✅ 保持原始布局
- ✅ 导出可搜索PDF

### 📦 批量处理
- ✅ 批量格式转换
- ✅ 批量添加水印
- ✅ 批量合并/分割
- ✅ 批量重命名
- ✅ 批量添加页码

## 技术栈

- **编程语言**: Python 3.8+
- **GUI框架**: PyQt5
- **核心库**:
  - PyMuPDF (fitz) - PDF解析
  - PyPDF2 - PDF操作
  - pdf2image - PDF转图片
  - python-docx/docx2pdf - Word转换
  - Pillow - 图像处理
  - reportlab - PDF生成
  - pikepdf - PDF编辑
  - opencv-python - 图像增强
  - pytesseract - OCR功能

## 安装说明

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

## 项目结构

```
pdf_master_suite/
├── main.py                    # 程序入口
├── requirements.txt           # 依赖包
├── config/                    # 配置文件
├── src/
│   ├── ui/                   # 界面相关
│   │   ├── main_window.py    # 主窗口
│   │   └── widgets.py        # 自定义组件
│   ├── core/                 # 核心功能
│   │   ├── pdf_parser.py     # PDF解析
│   │   ├── converter.py      # 格式转换
│   │   ├── editor.py         # PDF编辑
│   │   └── security.py       # 安全功能
│   ├── utils/                # 工具函数
│   └── batch/                # 批处理
├── resources/                # 资源文件
│   ├── icons/                # 图标
│   ├── themes/               # 主题
│   └── templates/            # 模板
└── tests/                    # 测试文件
```

## 使用指南

### 打开PDF文件
1. 点击菜单栏的「文件」→「打开」或使用快捷键 `Ctrl+O`
2. 选择要打开的PDF文件

### 查看PDF
- 使用工具栏的导航按钮或键盘左右箭头翻页
- 使用缩放按钮或快捷键 `Ctrl++`/`Ctrl+-` 调整缩放比例
- 点击书签或缩略图快速跳转到对应页面
- 使用搜索功能查找文本内容

### 编辑PDF
1. 点击菜单栏的「工具」→「页面管理」
2. 选择需要的操作：提取、删除、重新排序、旋转、插入空白页

### 转换格式
1. 点击菜单栏的「工具」→「格式转换」
2. 选择转换类型和输出格式
3. 设置输出路径和选项
4. 点击「转换」按钮

### 安全设置
1. 点击菜单栏的「工具」→「安全设置」
2. 选择加密、解密、权限设置等功能
3. 设置相关参数并应用

## 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Linux主流发行版
- **Python版本**: Python 3.8+
- **内存**: 至少4GB RAM（处理大型PDF文件建议8GB以上）
- **存储空间**: 至少100MB可用空间

## 开发计划

### 第一阶段（已完成）
- ✅ 项目环境搭建
- ✅ 主界面设计
- ✅ PDF基础查看功能
- ✅ 基本文件操作（打开/保存）

### 第二阶段（已完成）
- ✅ PDF编辑功能（合并/分割/旋转）
- ✅ 格式转换基础（PDF↔图片/文本）
- ✅ 页面管理功能

### 第三阶段（已完成）
- ✅ OCR集成
- ✅ Word/Excel转换
- ✅ 加密解密功能
- ✅ 水印和批注

### 第四阶段（已完成）
- ✅ 批量处理功能
- ✅ 性能优化
- ✅ 主题和国际化
- ✅ 用户设置管理

## 许可证

本项目采用 GPL v3 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：


- GitHub: [https://github.com/zc18com/py_pdf_master](https://github.com/zc18com/py_pdf_master)

---

**PDF全能工具箱** - 让PDF处理更简单！
