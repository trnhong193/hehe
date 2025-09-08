# emp_planning_system/report_generator.py

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

# Hàm trợ giúp để đăng ký font tiếng Việt
def _register_vietnamese_font():
    """Đăng ký cả font thường và đậm của DejaVuSans."""
    base_path = os.path.dirname(__file__)
    font_regular_path = os.path.join(base_path, "DejaVuSans.ttf")
    font_bold_path = os.path.join(base_path, "DejaVuSans-Bold.ttf")

    # Đăng ký font thường
    if os.path.exists(font_regular_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_regular_path))
    else:
        print("Cảnh báo: Không tìm thấy font DejaVuSans.ttf")

    # Đăng ký font đậm
    if os.path.exists(font_bold_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))
    else:
        print("Cảnh báo: Không tìm thấy font DejaVuSans-Bold.ttf, sẽ dùng font thường.")
        # Nếu không có font đậm, đăng ký font thường với tên đậm để chương trình không lỗi
        if os.path.exists(font_regular_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_regular_path))

def generate_report(filename, report_data):
    """
    Tạo file báo cáo PDF từ dữ liệu được cung cấp.
    report_data là một dict chứa: emps, obstacles, image_path, altitude
    """
    try:
        # Đăng ký font và tạo các style
        vietnamese_font = _register_vietnamese_font()
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Title_vi', parent=styles['Title'], fontName=vietnamese_font))
        styles.add(ParagraphStyle(name='Heading1_vi', parent=styles['h1'], fontName=vietnamese_font))
        styles.add(ParagraphStyle(name='Normal_vi', parent=styles['Normal'], fontName=vietnamese_font))
        styles.add(ParagraphStyle(name='TableContent_vi', parent=styles['Normal'], fontName='DejaVuSans', alignment=1))
        # Khởi tạo tài liệu
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        # 1. Tiêu đề
        title = Paragraph("BÁO CÁO QUY HOẠCH VÀ CẢNH BÁO NGUY HIỂM DO EMP", styles['Title_vi'])
        story.append(title)
        
        timestamp = datetime.now().strftime("%H:%M:%S Ngày %d-%m-%Y")
        time_p = Paragraph(f"<i>Báo cáo được tạo lúc: {timestamp}</i>", styles['Normal_vi'])
        story.append(time_p)
        story.append(Spacer(1, 0.2 * inch))
        
        # 2. Thông số chung
        story.append(Paragraph(f"Độ cao mặt cắt xét ảnh hưởng: {report_data.get('altitude', 'N/A')} m", styles['Normal_vi']))
        story.append(Spacer(1, 0.2 * inch))

        # 3. Danh sách nguồn EMP
        story.append(Paragraph("Danh sách các nguồn phát EMP", styles['Heading1_vi']))
        emp_table_data = [
            ['ID (rút gọn)', 'Vĩ độ', 'Kinh độ', 'Công suất (W)', 'Độ cao (m)']
        ]
        for emp in report_data.get('emps', []):
            emp_table_data.append([emp.id[:8], f"{emp.lat:.6f}", f"{emp.lon:.6f}", emp.power, emp.height])
        
        emp_table = Table(emp_table_data)
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 0.2 * inch))

        # 4. Danh sách vật cản
        story.append(Paragraph("Danh sách các vật cản", styles['Heading1_vi']))
        obs_table_data = [
            ['ID (rút gọn)', 'Vĩ độ', 'Kinh độ', 'Dài (m)', 'Rộng (m)', 'Cao (m)']
        ]
        for obs in report_data.get('obstacles', []):
            obs_table_data.append([obs.id[:8], f"{obs.lat:.6f}", f"{obs.lon:.6f}", obs.length, obs.width, obs.height])

        obs_table = Table(obs_table_data)
        obs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])) # Dùng lại style của bảng trên
        story.append(obs_table)
        story.append(Spacer(1, 0.4 * inch))
        
        # 5. Hình ảnh minh họa
        story.append(Paragraph("Minh họa vùng ảnh hưởng", styles['Heading1_vi']))
        
        image_path = report_data.get('image_path')
        if image_path and os.path.exists(image_path):
            # Lấy kích thước ảnh và điều chỉnh để vừa với trang
            img = Image(image_path)
            page_width, _ = letter
            img_width, img_height = img.imageWidth, img.imageHeight
            scale = (page_width - 1.5 * inch) / img_width
            img.drawWidth = img_width * scale
            img.drawHeight = img_height * scale
            story.append(img)
        else:
            story.append(Paragraph("<i>Không có hình ảnh vùng ảnh hưởng.</i>", styles['Normal_vi']))
            
        # 6. Kiến nghị (phần tĩnh)
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("Kiến nghị", styles['Heading1_vi']))
        story.append(Paragraph("Dựa trên kết quả mô phỏng, cần xem xét các biện pháp che chắn hoặc di dời các thiết bị nhạy cảm ra khỏi vùng có màu ĐỎ (nguy hiểm cao) và CAM (cảnh báo). Đảm bảo nhân sự không tiếp xúc lâu dài trong các khu vực này.", styles['Normal_vi']))

        # Xây dựng file PDF
        doc.build(story)
        return True, f"Báo cáo đã được lưu thành công tại: {filename}"
    except Exception as e:
        return False, f"Tạo báo cáo thất bại: {e}"