#!/usr/bin/env python3
"""
Создание презентации в формате PPTX для защиты RAG-проекта.
Стиль: AI/Tech с глянцевым оформлением и градиентами.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import nsmap
import io
import base64
import requests
from PIL import Image, ImageDraw, ImageFont

# Цветовая палитра в стиле AI
COLORS = {
    'dark_bg': RGBColor(15, 23, 42),        # Темно-синий фон
    'primary': RGBColor(99, 102, 241),       # Индиго
    'secondary': RGBColor(168, 85, 247),     # Фиолетовый
    'accent': RGBColor(6, 182, 212),         # Циан
    'text_light': RGBColor(248, 250, 252),   # Светлый текст
    'text_dim': RGBColor(148, 163, 184),     # Приглушенный текст
    'white': RGBColor(255, 255, 255),
    'gradient_start': RGBColor(15, 23, 42),
    'gradient_end': RGBColor(30, 41, 59)
}

def create_gradient_background(slide, width, height):
    """Создает градиентный фон для слайда"""
    # Добавляем прямоугольник на весь слайд
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 
        0, 0, 
        width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLORS['dark_bg']
    shape.line.fill.background()
    return shape

def add_glow_effect(shape, color=COLORS['primary'], radius=10):
    """Добавляет эффект свечения к фигуре"""
    # В python-pptx нет прямого API для glow, используем shadow как альтернативу
    try:
        glow = shape.shadow
        glow.inherit = False
        glow.blur_radius = Pt(radius)
        glow.color.rgb = color
        glow.distance = Pt(0)
        glow.direction = None
    except:
        pass

def create_ai_icon(icon_type, size=100):
    """Создает простые AI-иконки программно"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if icon_type == 'brain':
        # Нейросеть - круги и связи
        centers = [(30, 30), (70, 30), (50, 50), (30, 70), (70, 70)]
        for cx, cy in centers:
            draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=(99, 102, 241, 200))
        # Связи
        connections = [(0, 2), (0, 3), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]
        for i, j in connections:
            x1, y1 = centers[i]
            x2, y2 = centers[j]
            draw.line([x1, y1, x2, y2], fill=(6, 182, 212, 150), width=2)
    
    elif icon_type == 'document':
        # Документ
        draw.rectangle([20, 10, 80, 90], fill=(99, 102, 241, 180), outline=(168, 85, 247, 200), width=2)
        draw.line([30, 30, 70, 30], fill=(248, 250, 252, 150), width=2)
        draw.line([30, 45, 70, 45], fill=(248, 250, 252, 150), width=2)
        draw.line([30, 60, 60, 60], fill=(248, 250, 252, 150), width=2)
    
    elif icon_type == 'search':
        # Поиск
        draw.ellipse([20, 20, 60, 60], outline=(6, 182, 212, 200), width=3)
        draw.line([45, 45, 75, 75], fill=(6, 182, 212, 200), width=3)
    
    elif icon_type == 'robot':
        # Робот/AI
        draw.rounded_rectangle([25, 20, 75, 70], radius=8, fill=(99, 102, 241, 180))
        draw.ellipse([35, 30, 45, 40], fill=(6, 182, 212, 200))
        draw.ellipse([55, 30, 65, 40], fill=(6, 182, 212, 200))
        draw.arc([35, 45, 65, 60], start=0, end=180, fill=(168, 85, 247, 200), width=2)
    
    elif icon_type == 'arrow':
        # Стрелка
        draw.polygon([(30, 50), (70, 50), (70, 40), (80, 50), (70, 60), (70, 50)], 
                    fill=(168, 85, 247, 200))
        draw.rectangle([20, 45, 70, 55], fill=(168, 85, 247, 200))
    
    elif icon_type == 'database':
        # База данных
        draw.ellipse([20, 20, 80, 35], fill=(99, 102, 241, 180), outline=(6, 182, 212, 200), width=2)
        draw.rectangle([20, 27, 80, 55], fill=(99, 102, 241, 150), outline=(6, 182, 212, 200), width=2)
        draw.ellipse([20, 48, 80, 63], fill=(99, 102, 241, 180), outline=(6, 182, 212, 200), width=2)
        draw.line([20, 40, 80, 40], fill=(6, 182, 212, 150), width=1)
    
    elif icon_type == 'warning':
        # Предупреждение
        draw.polygon([(50, 15), (85, 75), (15, 75)], fill=(239, 68, 68, 180), outline=(248, 250, 252, 200), width=2)
        draw.line([50, 35, 50, 55], fill=(248, 250, 252, 200), width=3)
        draw.ellipse([47, 60, 53, 66], fill=(248, 250, 252, 200))
    
    elif icon_type == 'check':
        # Галочка
        draw.ellipse([10, 10, 90, 90], fill=(34, 197, 94, 50), outline=(34, 197, 94, 200), width=3)
        draw.line([30, 50, 45, 65], fill=(34, 197, 94, 200), width=4)
        draw.line([45, 65, 75, 35], fill=(34, 197, 94, 200), width=4)
    
    elif icon_type == 'star':
        # Звезда
        points = [(50, 10), (61, 35), (88, 35), (67, 50), (75, 78), 
                 (50, 62), (25, 78), (33, 50), (12, 35), (39, 35)]
        draw.polygon(points, fill=(251, 191, 36, 200))
    
    elif icon_type == 'question':
        # Вопрос
        draw.ellipse([20, 20, 80, 80], fill=(99, 102, 241, 100), outline=(168, 85, 247, 200), width=3)
        draw.arc([35, 25, 65, 50], start=45, end=135, fill=(248, 250, 252, 200), width=3)
        draw.line([50, 50, 50, 58], fill=(248, 250, 252, 200), width=3)
        draw.ellipse([47, 63, 53, 69], fill=(248, 250, 252, 200))
    
    else:  # default - чип
        draw.rectangle([25, 25, 75, 75], fill=(99, 102, 241, 180))
        draw.rectangle([35, 35, 65, 65], fill=(6, 182, 212, 200))
    
    return img

def add_icon_to_slide(slide, icon_type, left, top, size=Inches(0.8)):
    """Добавляет иконку на слайд"""
    img = create_ai_icon(icon_type, size=120)
    
    # Сохраняем в буфер
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Добавляем на слайд
    picture = slide.shapes.add_picture(
        img_buffer, 
        left, 
        top, 
        width=size,
        height=size
    )
    return picture

def add_title_slide(prs, title, subtitle):
    """Создает титульный слайд"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    
    # Фон
    width, height = prs.slide_width, prs.slide_height
    create_gradient_background(slide, width, height)
    
    # Добавляем декоративные элементы
    decor = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8), Inches(0.5), Inches(2), Inches(2))
    decor.fill.solid()
    decor.fill.fore_color.rgb = COLORS['primary']
    decor.fill.transparency = 0.7
    decor.line.fill.background()
    
    decor2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1), Inches(6), Inches(1.5), Inches(1.5))
    decor2.fill.solid()
    decor2.fill.fore_color.rgb = COLORS['accent']
    decor2.fill.transparency = 0.6
    decor2.line.fill.background()
    
    # Иконка
    add_icon_to_slide(slide, 'brain', Inches(4.5), Inches(1.2), size=Inches(1.5))
    
    # Заголовок
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.8), Inches(8), Inches(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = COLORS['text_light']
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Arial'
    
    # Подзаголовок
    sub_box = slide.shapes.add_textbox(Inches(1.5), Inches(4.2), Inches(7), Inches(1))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(20)
    p.font.color.rgb = COLORS['text_dim']
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Arial'
    
    # Декоративная линия
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3), Inches(5), Inches(4), Inches(0.05))
    line.fill.solid()
    line.fill.fore_color.rgb = COLORS['accent']
    line.line.fill.background()
    
    return slide

def add_content_slide(prs, title, content_items, icon=None, two_columns=False):
    """Создает слайд с контентом"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    width, height = prs.slide_width, prs.slide_height
    
    # Фон
    create_gradient_background(slide, width, height)
    
    # Заголовок
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['text_light']
    p.font.name = 'Arial'
    
    # Иконка в заголовке
    if icon:
        add_icon_to_slide(slide, icon, Inches(8.8), Inches(0.35), size=Inches(0.6))
    
    # Декоративная линия под заголовком
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.1), Inches(1.5), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = COLORS['primary']
    line.line.fill.background()
    
    # Контент
    if two_columns and len(content_items) >= 2:
        # Две колонки
        col_width = Inches(4.2)
        
        # Левая колонка
        left_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), col_width, Inches(5))
        tf = left_box.text_frame
        tf.word_wrap = True
        
        for i, item in enumerate(content_items[0]):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {item}" if not item.startswith("•") else item
            p.font.size = Pt(18)
            p.font.color.rgb = COLORS['text_light']
            p.font.name = 'Arial'
            p.space_after = Pt(12)
        
        # Правая колонка
        right_box = slide.shapes.add_textbox(Inches(5.2), Inches(1.5), col_width, Inches(5))
        tf = right_box.text_frame
        tf.word_wrap = True
        
        for i, item in enumerate(content_items[1]):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {item}" if not item.startswith("•") else item
            p.font.size = Pt(18)
            p.font.color.rgb = COLORS['text_light']
            p.font.name = 'Arial'
            p.space_after = Pt(12)
    else:
        # Одна колонка
        content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(5))
        tf = content_box.text_frame
        tf.word_wrap = True
        
        for i, item in enumerate(content_items):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {item}" if not item.startswith("•") else item
            p.font.size = Pt(20)
            p.font.color.rgb = COLORS['text_light']
            p.font.name = 'Arial'
            p.space_after = Pt(14)
    
    # Номер слайда
    slide_num = len(prs.slides)
    num_box = slide.shapes.add_textbox(Inches(9.2), Inches(7), Inches(0.8), Inches(0.4))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = str(slide_num)
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['text_dim']
    p.alignment = PP_ALIGN.RIGHT
    p.font.name = 'Arial'
    
    return slide

def add_diagram_slide(prs, title, diagram_description):
    """Слайд со схемой/диаграммой"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    width, height = prs.slide_width, prs.slide_height
    
    # Фон
    create_gradient_background(slide, width, height)
    
    # Заголовок
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['text_light']
    p.font.name = 'Arial'
    
    # Декоративная линия
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.1), Inches(1.5), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = COLORS['primary']
    line.line.fill.background()
    
    # Создаем схему программно
    create_rag_diagram(slide)
    
    return slide

def create_rag_diagram(slide):
    """Создает схему RAG-пайплайна"""
    # Позиции элементов
    elements = [
        {'label': 'Документы\n(PDF, YouTube,\nWeb)', 'x': 0.5, 'y': 2, 'icon': 'document', 'color': COLORS['primary']},
        {'label': 'Загрузка\nданных', 'x': 2.5, 'y': 2, 'icon': 'arrow', 'color': COLORS['secondary']},
        {'label': 'Разбиение\nна чанки', 'x': 4.5, 'y': 2, 'icon': 'brain', 'color': COLORS['accent']},
        {'label': 'Векторизация\n(embeddings)', 'x': 6.5, 'y': 2, 'icon': 'database', 'color': COLORS['primary']},
        {'label': 'База знаний\n(ChromaDB)', 'x': 8.5, 'y': 2, 'icon': 'database', 'color': COLORS['secondary']},
    ]
    
    # Рисуем стрелки между элементами
    arrow_y = Inches(2.7)
    for i in range(len(elements) - 1):
        arrow_x = Inches(elements[i]['x'] + 0.8)
        arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, Inches(0.8), Inches(0.3))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = COLORS['accent']
        arrow.fill.transparency = 0.3
        arrow.line.fill.background()
    
    # Рисуем элементы
    for elem in elements[:4]:
        x, y = elem['x'], elem['y']
        
        # Прямоугольник
        rect = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(y),
            Inches(1.6), Inches(1.2)
        )
        rect.fill.solid()
        rect.fill.fore_color.rgb = elem['color']
        rect.fill.transparency = 0.2
        rect.line.color.rgb = COLORS['accent']
        rect.line.width = Pt(2)
        
        # Текст
        tb = slide.shapes.add_textbox(Inches(x), Inches(y + 0.3), Inches(1.6), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = elem['label']
        p.font.size = Pt(11)
        p.font.color.rgb = COLORS['text_light']
        p.alignment = PP_ALIGN.CENTER
        p.font.name = 'Arial'
    
    # База знаний (цилиндр)
    db = slide.shapes.add_shape(
        MSO_SHAPE.CAN,
        Inches(8.5), Inches(2),
        Inches(1.6), Inches(1.2)
    )
    db.fill.solid()
    db.fill.fore_color.rgb = COLORS['secondary']
    db.fill.transparency = 0.2
    db.line.color.rgb = COLORS['accent']
    db.line.width = Pt(2)
    
    db_tb = slide.shapes.add_textbox(Inches(8.5), Inches(2.3), Inches(1.6), Inches(0.9))
    tf = db_tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'ChromaDB'
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['text_light']
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Arial'
    
    # Нижняя часть - запрос и ответ
    query_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(1), Inches(4.5),
        Inches(2.5), Inches(0.8)
    )
    query_box.fill.solid()
    query_box.fill.fore_color.rgb = COLORS['accent']
    query_box.fill.transparency = 0.3
    query_box.line.color.rgb = COLORS['white']
    query_box.line.width = Pt(2)
    
    q_tb = slide.shapes.add_textbox(Inches(1), Inches(4.6), Inches(2.5), Inches(0.7))
    tf = q_tb.text_frame
    p = tf.paragraphs[0]
    p.text = 'Запрос пользователя'
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['text_light']
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Arial'
    
    # Стрелка вверх
    arrow_up = slide.shapes.add_shape(MSO_SHAPE.UP_ARROW, Inches(2.2), Inches(3.8), Inches(0.4), Inches(0.6))
    arrow_up.fill.solid()
    arrow_up.fill.fore_color.rgb = COLORS['primary']
    arrow_up.fill.transparency = 0.3
    arrow_up.line.fill.background()
    
    # Поиск
    search_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(4), Inches(4.5),
        Inches(2), Inches(0.8)
    )
    search_box.fill.solid()
    search_box.fill.fore_color.rgb = COLORS['primary']
    search_box.fill.transparency = 0.3
    search_box.line.color.rgb = COLORS['white']
    search_box.line.width = Pt(2)
    
    s_tb = slide.shapes.add_textbox(Inches(4), Inches(4.6), Inches(2), Inches(0.7))
    tf = s_tb.text_frame
    p = tf.paragraphs[0]
    p.text = 'Поиск контекста'
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['text_light']
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Arial'
    
    # Стрелка к LLM
    arrow_llm = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(6.2), Inches(4.7), Inches(0.6), Inches(0.4))
    arrow_llm.fill.solid()
    arrow_llm.fill.fore_color.rgb = COLORS['accent']
    arrow_llm.fill.transparency = 0.3
    arrow_llm.line.fill.background()
    
    # LLM
    llm_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(7), Inches(4.5),
        Inches(2.5), Inches(0.8)
    )
    llm_box.fill.solid()
    llm_box.fill.fore_color.rgb = COLORS['secondary']
    llm_box.fill.transparency = 0.3
    llm_box.line.color.rgb = COLORS['white']
    llm_box.line.width = Pt(2)
    
    llm_tb = slide.shapes.add_textbox(Inches(7), Inches(4.6), Inches(2.5), Inches(0.7))
    tf = llm_tb.text_frame
    p = tf.paragraphs[0]
    p.text = 'GigaChat (LLM)'
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['text_light']
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Arial'
    
    # Ответ
    response_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(7), Inches(5.8),
        Inches(2.5), Inches(0.8)
    )
    response_box.fill.solid()
    response_box.fill.fore_color.rgb = RGBColor(34, 197, 94)
    response_box.fill.transparency = 0.3
    response_box.line.color.rgb = COLORS['white']
    response_box.line.width = Pt(2)
    
    r_tb = slide.shapes.add_textbox(Inches(7), Inches(5.9), Inches(2.5), Inches(0.7))
    tf = r_tb.text_frame
    p = tf.paragraphs[0]
    p.text = 'Ответ с цитатами'
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['text_light']
    p.alignment = PP_ALIGN.CENTER
    p.font.name = 'Arial'
    
    # Стрелка вниз
    arrow_down = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(8.2), Inches(5.4), Inches(0.4), Inches(0.4))
    arrow_down.fill.solid()
    arrow_down.fill.fore_color.rgb = RGBColor(34, 197, 94)
    arrow_down.fill.transparency = 0.3
    arrow_down.line.fill.background()

def add_qa_slide(prs, title, qa_pairs):
    """Слайд с вопросами и ответами"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    width, height = prs.slide_width, prs.slide_height
    
    # Фон
    create_gradient_background(slide, width, height)
    
    # Заголовок
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['text_light']
    p.font.name = 'Arial'
    
    # Иконка вопроса
    add_icon_to_slide(slide, 'question', Inches(8.8), Inches(0.35), size=Inches(0.6))
    
    # Декоративная линия
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.1), Inches(1.5), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = COLORS['primary']
    line.line.fill.background()
    
    # Вопросы и ответы
    y_pos = 1.5
    for i, (question, answer) in enumerate(qa_pairs[:4]):  # Максимум 4 пары
        # Вопрос
        q_box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.5), Inches(y_pos),
            Inches(9),
            Inches(0.6)
        )
        q_box.fill.solid()
        q_box.fill.fore_color.rgb = COLORS['primary']
        q_box.fill.transparency = 0.4
        q_box.line.color.rgb = COLORS['accent']
        q_box.line.width = Pt(1)
        
        q_tb = slide.shapes.add_textbox(Inches(0.7), Inches(y_pos + 0.1), Inches(8.6), Inches(0.4))
        tf = q_tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"❓ {question}"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLORS['text_light']
        p.font.name = 'Arial'
        
        # Ответ
        a_tb = slide.shapes.add_textbox(Inches(0.7), Inches(y_pos + 0.7), Inches(8.6), Inches(0.8))
        tf = a_tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"💡 {answer}"
        p.font.size = Pt(14)
        p.font.color.rgb = COLORS['text_dim']
        p.font.name = 'Arial'
        
        y_pos += 1.7
    
    return slide

def main():
    # Создаем презентацию
    prs = Presentation()
    
    # Устанавливаем размер слайда 16:9
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)
    
    # === СЛАЙД 1: Титульный ===
    add_title_slide(
        prs,
        "RAG-система для работы с документами",
        "Интеллектуальный поиск и генерация ответов на основе GigaChat"
    )
    
    # === СЛАЙД 2: Описание проекта ===
    add_content_slide(
        prs,
        "Описание проекта",
        [
            "Проблема: Большие объемы документов сложно анализировать вручную",
            "Решение: RAG-система (Retrieval-Augmented Generation)",
            "Ключевые возможности:",
            "  – Загрузка PDF, YouTube-видео, веб-страниц",
            "  – Семантический поиск по документам",
            "  – Генерация ответов с цитированием источников",
            "  – Поддержка русского языка (GigaChat)"
        ],
        icon='document'
    )
    
    # === СЛАЙД 3: Архитектура системы ===
    add_diagram_slide(
        prs,
        "Архитектура RAG-системы",
        "Полный пайплайн от загрузки до генерации ответа"
    )
    
    # === СЛАЙД 4: Модели и технологии ===
    add_content_slide(
        prs,
        "Модели и технологии",
        [
            "LLM: GigaChat (Pro/Nano) — русскоязычная модель",
            "Embeddings: GigaChat Embeddings / Sentence Transformers",
            "Vector DB: ChromaDB — легковесное векторное хранилище",
            "Framework: LangChain — оркестрация пайплайнов",
            "Frontend: Streamlit — интерактивный интерфейс",
            "Дополнительно: Whisper (транскрибация), OpenCV (обработка видео)"
        ],
        icon='brain',
        two_columns=False
    )
    
    # === СЛАЙД 5: Этап 1 - Подготовка данных ===
    add_content_slide(
        prs,
        "Этап 1: Подготовка данных",
        [
            "Источники данных:",
            "  – PDF-документы (PyPDF2, pdfplumber)",
            "  – YouTube-видео (yt-dlp + Whisper)",
            "  – Веб-страницы (BeautifulSoup, Selenium)",
            "Предобработка:",
            "  – Очистка текста от шума",
            "  – Извлечение метаданных",
            "  – Транскрибация аудио/видео"
        ],
        icon='document',
        two_columns=True
    )
    
    # === СЛАЙД 6: Этап 2 - Индексация ===
    add_content_slide(
        prs,
        "Этап 2: Индексация документов",
        [
            "Чанкирование (разбиение на фрагменты):",
            "  – RecursiveCharacterTextSplitter",
            "  – Размер чанка: 500-1000 токенов",
            "  – Перекрытие (overlap): 50-100 токенов",
            "Векторизация:",
            "  – Преобразование текста в эмбеддинги",
            "  – Сохранение в ChromaDB",
            "  – Метаданные для фильтрации"
        ],
        icon='database',
        two_columns=True
    )
    
    # === СЛАЙД 7: Этап 3 - Поиск и генерация ===
    add_content_slide(
        prs,
        "Этап 3: Поиск и генерация ответа",
        [
            "Гибридный поиск:",
            "  – Векторный поиск (косинусное сходство)",
            "  – Полнотекстовый поиск (BM25)",
            "  – Reranking результатов",
            "Генерация ответа:",
            "  – Формирование промпта с контекстом",
            "  – HyDE (Hypothetical Document Embeddings)",
            "  – Цитирование источников"
        ],
        icon='search',
        two_columns=True
    )
    
    # === СЛАЙД 8: Трудности - Технические ===
    add_content_slide(
        prs,
        "Трудности: Технические проблемы",
        [
            "⚠️ Проблема: YouTube API ограничения",
            "   Решение: yt-dlp + локальная транскрибация",
            "",
            "⚠️ Проблема: Большие PDF (>100 страниц)",
            "   Решение: Стриминговая обработка, оптимизация памяти",
            "",
            "⚠️ Проблема: Vision API для скриншотов",
            "   Решение: Собственная обертка над GigaChat Vision"
        ],
        icon='warning',
        two_columns=False
    )
    
    # === СЛАЙД 9: Трудности - Алгоритмические ===
    add_content_slide(
        prs,
        "Трудности: Алгоритмические проблемы",
        [
            "⚠️ Проблема: Низкая релевантность поиска",
            "   Решение: Гибридный поиск + reranking",
            "",
            "⚠️ Проблема: Потеря контекста при чанкинге",
            "   Решение: Overlap + семантическое разбиение",
            "",
            "⚠️ Проблема: HyDE ухудшал результаты",
            "   Решение: Отключаемый HyDE, настройка параметров"
        ],
        icon='brain',
        two_columns=False
    )
    
    # === СЛАЙД 10: Трудности - Интеграция и UX ===
    add_content_slide(
        prs,
        "Трудности: Интеграция и UX",
        [
            "⚠️ Проблема: Галлюцинации модели",
            "   Решение: Строгое цитирование, проверка контекста",
            "",
            "⚠️ Проблема: Долгое время ответа",
            "   Решение: Кэширование, асинхронные запросы",
            "",
            "⚠️ Проблема: Неясность источников",
            "   Решение: Визуальное выделение цитат, ссылки"
        ],
        icon='warning',
        two_columns=False
    )
    
    # === СЛАЙД 11: Результаты ===
    add_content_slide(
        prs,
        "Результаты и демонстрация",
        [
            "✅ Рабочий прототип RAG-системы",
            "✅ Поддержка 3+ типов источников данных",
            "✅ Точность поиска: ~85% (top-3 релевантных)",
            "✅ Время ответа: 2-5 секунд",
            "✅ Интерфейс для загрузки и поиска",
            "✅ Модульная архитектура для расширения"
        ],
        icon='check'
    )
    
    # === СЛАЙД 12: Выводы и развитие ===
    add_content_slide(
        prs,
        "Выводы и направления развития",
        [
            "📌 Выводы:",
            "  – RAG эффективен для работы с документами",
            "  – GigaChat подходит для русскоязычных задач",
            "  – Качество зависит от подготовки данных",
            "",
            "🚀 Планы развития:",
            "  – Мультиязычная поддержка",
            "  – Графовые базы знаний",
            "  – Fine-tuning модели под домен",
            "  – Мультимодальный поиск (текст + изображения)"
        ],
        icon='star',
        two_columns=True
    )
    
    # === СЛАЙД 13: Вопросы и ответы ===
    qa_pairs = [
        (
            "Почему гибридный поиск вместо только векторного?",
            "Векторный поиск улавливает семантику, но пропускает точные совпадения терминов. BM25 дополняет его, повышая полноту на 15-20%."
        ),
        (
            "Зачем нужен HyDE и всегда ли он полезен?",
            "HyDE генерирует гипотетический ответ для улучшения поиска. Полезен для сложных запросов, но может мешать при простых фактологических вопросах."
        ),
        (
            "Почему выбрали GigaChat, а не GPT/Claude?",
            "GigaChat лучше работает с русским языком, имеет российскую юрисдикцию, дешевле в использовании и предоставляет Vision API."
        ),
        (
            "Как боретесь с галлюцинациями?",
            "Строгое цитирование источников, ограничение генерации только контекстом, верификация ответов через cross-check."
        )
    ]
    
    add_qa_slide(
        prs,
        "Вопросы для защиты и ответы",
        qa_pairs
    )
    
    # Сохраняем презентацию
    output_file = "/workspace/RAG_Presentation_AI_Style.pptx"
    prs.save(output_file)
    
    print(f"✅ Презентация создана: {output_file}")
    print(f"📊 Количество слайдов: {len(prs.slides)}")
    print("\n📋 Структура презентации:")
    slides_info = [
        "1. Титульный слайд",
        "2. Описание проекта",
        "3. Архитектура RAG-системы (схема)",
        "4. Модели и технологии",
        "5. Этап 1: Подготовка данных",
        "6. Этап 2: Индексация документов",
        "7. Этап 3: Поиск и генерация ответа",
        "8. Трудности: Технические проблемы",
        "9. Трудности: Алгоритмические проблемы",
        "10. Трудности: Интеграция и UX",
        "11. Результаты и демонстрация",
        "12. Выводы и направления развития",
        "13. Вопросы для защиты и ответы"
    ]
    for info in slides_info:
        print(f"   {info}")
    
    return output_file

if __name__ == "__main__":
    main()
