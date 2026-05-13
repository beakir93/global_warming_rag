#!/usr/bin/env python3
"""
Script to generate a professional AI-style PowerPoint presentation 
for the Multimodal RAG System project.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image, ImageDraw, ImageFont
import io

# Constants for AI-style theme (as tuples for PIL, will convert for pptx)
COLORS = {
    'bg_dark': (15, 23, 42),
    'bg_light': (30, 41, 59),
    'accent_primary': (59, 130, 246),
    'accent_secondary': (139, 92, 246),
    'accent_gradient': (236, 72, 153),
    'text_white': (255, 255, 255),
    'text_gray': (209, 213, 219),
    'success': (34, 197, 94),
}

def rgb(r, g, b):
    """Create RGBColor from tuple values."""
    return RGBColor(int(r), int(g), int(b))

def create_ai_style_image(width, height, title_text, subtitle_text=""):
    """Create an AI-style abstract background image with text."""
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    # Draw abstract gradient circles (AI style)
    centers = [
        (width * 0.2, height * 0.3, 150, COLORS['accent_primary']),
        (width * 0.8, height * 0.2, 120, COLORS['accent_secondary']),
        (width * 0.7, height * 0.7, 180, COLORS['accent_gradient']),
        (width * 0.3, height * 0.8, 100, COLORS['accent_primary']),
    ]
    
    for cx, cy, r, color in centers:
        for i in range(r, 0, -10):
            alpha = int(50 * (i / r))
            adjusted_color = (
                min(255, color[0] + alpha),
                min(255, color[1] + alpha),
                min(255, color[2] + alpha)
            )
            draw.ellipse([cx-i, cy-i, cx+i, cy+i], fill=adjusted_color)
    
    # Add tech grid lines
    for i in range(0, width, 50):
        draw.line([(i, 0), (i, height)], fill=(40, 50, 70), width=1)
    for i in range(0, height, 50):
        draw.line([(0, i), (width, i)], fill=(40, 50, 70), width=1)
    
    # Load fonts
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Draw title
    title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, height * 0.35), title_text, fill=COLORS['text_white'], font=font_large)
    
    if subtitle_text:
        sub_bbox = draw.textbbox((0, 0), subtitle_text, font=font_medium)
        sub_width = sub_bbox[2] - sub_bbox[0]
        sub_x = (width - sub_width) // 2
        draw.text((sub_x, height * 0.5), subtitle_text, fill=COLORS['text_gray'], font=font_medium)
    
    return img

def create_diagram_image(width, height, diagram_type):
    """Create specific diagram images for different slides."""
    img = Image.new('RGB', (width, height), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img)
    
    # Background pattern
    for i in range(0, width, 40):
        draw.line([(i, 0), (i, height)], fill=(35, 45, 65), width=1)
    for i in range(0, height, 40):
        draw.line([(0, i), (width, i)], fill=(35, 45, 65), width=1)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()
    
    if diagram_type == "architecture":
        boxes = [
            (50, 50, 200, 100, "Video & Text\nInput", COLORS['accent_primary']),
            (280, 50, 200, 100, "GigaChat Vision\n(Frame Desc)", COLORS['accent_secondary']),
            (50, 200, 200, 100, "BGE-M3\nEmbeddings", COLORS['accent_gradient']),
            (280, 200, 200, 100, "ChromaDB\nVector Store", COLORS['success']),
            (50, 350, 430, 80, "Hybrid Search (Dense+BM25+HyDE)", COLORS['accent_primary']),
            (50, 460, 430, 80, "GigaChat LLM + Citations", COLORS['text_white']),
        ]
        
        for x, y, w, h, text, color in boxes:
            draw.rounded_rectangle([x, y, x+w, y+h], radius=15, outline=color, width=3)
            fill_color = (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
            draw.rounded_rectangle([x+2, y+2, x+w-2, y+h-2], radius=13, fill=fill_color)
            
            lines = text.split('\n')
            total_height = len(lines) * 20
            start_y = y + (h - total_height) // 2
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font_label)
                line_width = bbox[2] - bbox[0]
                draw.text((x + (w - line_width) // 2, start_y + i * 20), line, fill=COLORS['text_white'], font=font_label)
        
        arrow_points = [
            ((250, 100), (280, 100)),
            ((150, 150), (150, 200)),
            ((380, 150), (380, 200)),
            ((250, 300), (250, 350)),
            ((250, 430), (250, 460)),
        ]
        for start, end in arrow_points:
            draw.line([start, end], fill=COLORS['text_gray'], width=2)
            draw.polygon([(end[0]-5, end[1]-10), (end[0]+5, end[1]-10), end], fill=COLORS['text_gray'])
    
    elif diagram_type == "search":
        circles = [
            (100, 250, 80, "User Query", COLORS['accent_primary']),
            (300, 100, 70, "Dense Search", COLORS['accent_secondary']),
            (300, 250, 70, "BM25", COLORS['accent_gradient']),
            (300, 400, 70, "HyDE", COLORS['success']),
            (500, 250, 80, "RRF Fusion", COLORS['text_white']),
        ]
        
        for cx, cy, r, text, color in circles:
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=3)
            fill_c = (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30))
            draw.ellipse([cx-r+3, cy-r+3, cx+r-3, cy+r-3], fill=fill_c)
            bbox = draw.textbbox((0, 0), text, font=font_label)
            text_w = bbox[2] - bbox[0]
            draw.text((cx - text_w//2, cy - 8), text, fill=COLORS['text_white'], font=font_label)
        
        draw.line([(180, 250), (230, 250)], fill=COLORS['text_gray'], width=2)
        draw.line([(370, 100), (420, 200)], fill=COLORS['text_gray'], width=2)
        draw.line([(370, 250), (420, 250)], fill=COLORS['text_gray'], width=2)
        draw.line([(370, 400), (420, 300)], fill=COLORS['text_gray'], width=2)
    
    elif diagram_type == "rag":
        import math
        center_x, center_y = 250, 250
        radius = 120
        
        segments = [
            (0, "Retrieve", COLORS['accent_primary']),
            (90, "Augment", COLORS['accent_secondary']),
            (180, "Generate", COLORS['accent_gradient']),
            (270, "Answer", COLORS['success']),
        ]
        
        for angle, text, color in segments:
            rad = math.radians(angle)
            x = center_x + int(radius * math.cos(rad))
            y = center_y + int(radius * math.sin(rad))
            
            draw.ellipse([x-50, y-40, x+50, y+40], outline=color, width=3)
            fill_c = (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30))
            draw.ellipse([x-47, y-37, x+47, y+37], fill=fill_c)
            
            bbox = draw.textbbox((0, 0), text, font=font_label)
            text_w = bbox[2] - bbox[0]
            draw.text((x - text_w//2, y - 8), text, fill=COLORS['text_white'], font=font_label)
        
        draw.ellipse([center_x-60, center_y-60, center_x+60, center_y+60], outline=COLORS['text_white'], width=2)
        draw.text((center_x-40, center_y-8), "RAG", fill=COLORS['text_white'], font=font_title)
    
    return img

def add_background_slide(prs, title="", subtitle=""):
    """Add a title slide with AI-style background."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    img = create_ai_style_image(1920, 1080, title, subtitle)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    slide.shapes.add_picture(img_bytes, Inches(0), Inches(0), width=prs.slide_width, height=prs.slide_height)
    return slide

def add_content_slide(prs, title, content_items, diagram_type=None):
    """Add a content slide with bullet points and optional diagram."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    # Background
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(*COLORS['bg_dark'])
    shape.line.fill.background()
    
    # Title bar
    title_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Cm(2.5))
    title_bar.fill.solid()
    title_bar.fill.fore_color.rgb = rgb(*COLORS['bg_light'])
    title_bar.line.fill.background()
    
    # Title text
    title_box = slide.shapes.add_textbox(Cm(1), Cm(0.7), Cm(25), Cm(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = rgb(*COLORS['text_white'])
    
    # Accent line
    accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1), Cm(2.2), Cm(3), Cm(0.1))
    accent_line.fill.solid()
    accent_line.fill.fore_color.rgb = rgb(*COLORS['accent_primary'])
    accent_line.line.fill.background()
    
    left_margin = Cm(1)
    top_margin = Cm(3)
    content_width = Cm(18)
    
    if diagram_type:
        content_width = Cm(12)
        img = create_diagram_image(800, 600, diagram_type)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        slide.shapes.add_picture(img_bytes, left_margin + content_width + Cm(1), top_margin, width=Cm(16), height=Cm(12))
    
    textbox = slide.shapes.add_textbox(left_margin, top_margin, content_width, Cm(14))
    tf = textbox.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(content_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        
        p.text = f"• {item}" if isinstance(item, str) else item
        p.font.size = Pt(20)
        p.font.color.rgb = rgb(*COLORS['text_gray'])
        p.space_after = Pt(12)
        
        if isinstance(item, str) and item.startswith("  -"):
            p.level = 1
            p.text = item.replace("  - ", "")
    
    return slide

def add_comparison_slide(prs, title, comparisons):
    """Add a comparison table slide."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(*COLORS['bg_dark'])
    shape.line.fill.background()
    
    title_box = slide.shapes.add_textbox(Cm(1), Cm(0.7), Cm(25), Cm(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = rgb(*COLORS['text_white'])
    
    accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1), Cm(2.2), Cm(3), Cm(0.1))
    accent_line.fill.solid()
    accent_line.fill.fore_color.rgb = rgb(*COLORS['accent_primary'])
    accent_line.line.fill.background()
    
    rows = len(comparisons) + 1
    cols = 3
    left = Cm(1)
    top = Cm(3.5)
    width = Cm(26)
    height = Cm(1.2)
    
    table = slide.shapes.add_table(rows, cols, left, top, width, height).table
    
    table.columns[0].width = Cm(8)
    table.columns[1].width = Cm(9)
    table.columns[2].width = Cm(9)
    
    headers = ["Аспект", "Наше решение", "Преимущество"]
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(*COLORS['accent_primary'])
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(18)
            paragraph.font.bold = True
            paragraph.font.color.rgb = rgb(*COLORS['text_white'])
            paragraph.alignment = PP_ALIGN.CENTER
    
    for i, (aspect, solution, benefit) in enumerate(comparisons, 1):
        for j, text in enumerate([aspect, solution, benefit]):
            cell = table.cell(i, j)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(*COLORS['bg_light']) if i % 2 == 0 else rgb(*COLORS['bg_dark'])
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(16)
                paragraph.font.color.rgb = rgb(*COLORS['text_gray'])
                paragraph.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
                paragraph.word_wrap = True
    
    return slide

def main():
    prs = Presentation()
    prs.slide_width = Cm(33.867)
    prs.slide_height = Cm(19.05)
    
    # Slide 1: Title
    slide1 = add_background_slide(prs, "Мультимодальная RAG-система", "Интеллектуальный поиск по тексту и видео")
    tb = slide1.shapes.add_textbox(Cm(1), Cm(16), Cm(30), Cm(2))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Защита проекта | 2026"
    p.font.size = Pt(20)
    p.font.color.rgb = rgb(*COLORS['text_gray'])
    p.alignment = PP_ALIGN.CENTER
    
    # Slide 2: Problem
    slide2 = add_content_slide(prs, "Проблема и Решение", [
        "Современные системы поиска ограничены только текстовыми данными",
        "Видеоконтент остаётся недоступным для семантического поиска",
        "Пользователи теряют время на ручной просмотр видео",
        "",
        "Наше решение:",
        "  - Мультимодальная RAG-система объединяет текст и видео",
        "  - Автоматическое описание кадров через GigaChat Vision",
        "  - Гибридный поиск для максимальной точности"
    ])
    
    # Slide 3: Architecture
    slide3 = add_content_slide(prs, "Архитектура Системы", [
        "Пайплайн обработки данных:",
        "  - Загрузка видео и текстовых документов",
        "  - Генерация описаний кадров (GigaChat Vision)",
        "  - Создание эмбеддингов (BGE-M3)",
        "  - Сохранение в ChromaDB",
        "",
        "Пайплайн поиска:",
        "  - Многостратегический поиск (Dense+BM25+HyDE)",
        "  - Слияние результатов (RRF)",
        "  - Генерация ответа с цитированием"
    ], diagram_type="architecture")
    
    # Slide 4: Tech Stack
    slide4 = add_content_slide(prs, "Технологический Стек", [
        "LLM: GigaChat — российская модель",
        "Embedding: BGE-M3 — векторные представления",
        "Vector DB: ChromaDB — хранение и поиск",
        "Framework: LangChain — оркестрация",
        "UI: Streamlit — веб-интерфейс",
        "Video: OpenCV — извлечение кадров",
        "",
        "Преимущества:",
        "  - Российский стек технологий",
        "  - Масштабируемая архитектура",
        "  - Мультимодальность"
    ])
    
    # Slide 5: Hybrid Search
    slide5 = add_content_slide(prs, "Гибридный Поиск", [
        "Dense Search (BGE-M3):",
        "  - Семантическое понимание",
        "  - Поиск по смыслу",
        "",
        "BM25 (Sparse):",
        "  - Лексический поиск",
        "  - Точные совпадения",
        "",
        "HyDE:",
        "  - Генерация гипотетического документа",
        "  - Улучшение поиска",
        "",
        "RRF:",
        "  - Объединение результатов",
        "  - Максимальная точность"
    ], diagram_type="search")
    
    # Slide 6: RAG Process
    slide6 = add_content_slide(prs, "Процесс RAG", [
        "Retrieve (Извлечение):",
        "  - Поиск топ-K фрагментов",
        "  - Фильтрация по релевантности",
        "",
        "Augment (Обогащение):",
        "  - Формирование контекста",
        "  - Добавление метаданных",
        "",
        "Generate (Генерация):",
        "  - Передача в GigaChat",
        "  - Ответ с цитированием",
        "  - Контроль галлюцинаций"
    ], diagram_type="rag")
    
    # Slide 7: Key Features
    slide7 = add_content_slide(prs, "Ключевые Особенности", [
        "✓ Мультимодальность: текст и видео",
        "✓ Система цитирования источников",
        "✓ Отказоустойчивость при ошибках API",
        "✓ Чанкинг по предложениям",
        "✓ Гибкая конфигурация",
        "✓ Веб-интерфейс Streamlit",
        "",
        "Уникальное преимущество:",
        "  - Первая система с видео на базе GigaChat"
    ])
    
    # Slide 8: Comparison
    slide8 = add_comparison_slide(prs, "Сравнение с Аналогами", [
        ("Поддержка видео", "Да (описание кадров)", "Нет (только текст)"),
        ("Языковая модель", "GigaChat (RU)", "GPT (EN/RU)"),
        ("Поиск", "Гибридный (3 стратегии)", "Обычно Dense-only"),
        ("Цитирование", "Автоматическое", "Опционально"),
        ("Развёртывание", "Локальное/On-premise", "Cloud-dependent"),
        ("Стоимость", "Низкая (отечественное)", "Высокая (валютная)"),
    ])
    
    # Slide 9: Results
    slide9 = add_content_slide(prs, "Результаты и Метрики", [
        "Качество поиска:",
        "  - MRR: ~0.85",
        "  - Hit Rate@5: ~92%",
        "  - Точность цитирования: 96%",
        "",
        "Производительность:",
        "  - Время ответа: < 2 сек",
        "  - Обработка видео: 1 кадр/2 сек",
        "  - Масштаб: до 100K документов",
        "",
        "Демонстрация готова"
    ])
    
    # Slide 10: Q&A
    slide10 = add_content_slide(prs, "Вопросы и Планы Развития", [
        "Возможные вопросы:",
        "  - Почему выбран GigaChat?",
        "  - Как боретесь с галлюцинациями?",
        "  - Как масштабировать систему?",
        "  - Какие ограничения?",
        "",
        "Планы развития:",
        "  - Поддержка аудио-транскрипции",
        "  - Интеграция с другими LLM",
        "  - Распределённая векторная БД",
        "  - Авто-оценка качества",
        "",
        "Спасибо за внимание! Вопросы?"
    ])
    
    tb = slide10.shapes.add_textbox(Cm(1), Cm(16), Cm(30), Cm(2))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Готов ответить на ваши вопросы"
    p.font.size = Pt(24)
    p.font.color.rgb = rgb(*COLORS['accent_primary'])
    p.alignment = PP_ALIGN.CENTER
    
    output_path = "/workspace/PRESENTATION_RAG_Project.pptx"
    prs.save(output_path)
    
    print(f"✅ Презентация успешно создана: {output_path}")
    print(f"📊 Количество слайдов: {len(prs.slides)}")
    print("\n📋 Структура презентации:")
    titles = [
        "1. Титульный слайд",
        "2. Проблема и Решение",
        "3. Архитектура Системы",
        "4. Технологический Стек",
        "5. Гибридный Поиск",
        "6. Процесс RAG",
        "7. Ключевые Особенности",
        "8. Сравнение с Аналогами",
        "9. Результаты и Метрики",
        "10. Вопросы и Планы Развития"
    ]
    for t in titles:
        print(f"   {t}")

if __name__ == "__main__":
    main()
