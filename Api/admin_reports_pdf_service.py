from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class AdminReportsPdfService:
    FONT_NAME = "ArialUnicodeAgent4KAdmin"
    FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")

    def __init__(self) -> None:
        self._font_registered = False

    def _ensure_font(self) -> None:
        if self._font_registered:
            return
        if not self.FONT_PATH.exists():
            raise FileNotFoundError(f"Font not found: {self.FONT_PATH}")
        pdfmetrics.registerFont(TTFont(self.FONT_NAME, str(self.FONT_PATH)))
        self._font_registered = True

    def build_pdf(self, reports_response) -> tuple[str, bytes]:
        self._ensure_font()
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "AdminReportsTitle",
            parent=styles["Heading1"],
            fontName=self.FONT_NAME,
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#202334"),
            alignment=TA_LEFT,
            spaceAfter=10,
        )
        subtitle_style = ParagraphStyle(
            "AdminReportsSubtitle",
            parent=styles["BodyText"],
            fontName=self.FONT_NAME,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#6f7690"),
            spaceAfter=10,
        )
        body_style = ParagraphStyle(
            "AdminReportsBody",
            parent=styles["BodyText"],
            fontName=self.FONT_NAME,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#2a2f45"),
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=14 * mm,
            rightMargin=14 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
            title="Подробные отчеты Agent_4K",
            author="Agent_4K",
        )

        story = [
            Paragraph(reports_response.title, title_style),
            Paragraph(reports_response.subtitle, subtitle_style),
            Paragraph(
                f"Всего отчетов: {reports_response.total_items}. "
                f"Средний % по завершенным ассессментам: "
                f"{reports_response.summary_score_percent if reports_response.summary_score_percent is not None else 'Нет данных'}",
                body_style,
            ),
            Spacer(1, 6),
        ]

        table_data = [[
            "Сотрудник / ID",
            "Группа / роль",
            "Статус",
            "4K score",
            "Тип MBTI",
            "Дата",
        ]]

        for item in reports_response.items:
            date_value = item.finished_at or item.started_at
            date_label = date_value.strftime("%d.%m.%Y") if date_value else "Без даты"
            score_label = f"{item.score_percent}%" if item.score_percent is not None else "—"
            table_data.append([
                Paragraph(f"<b>{item.full_name}</b><br/><font size='7'>ID {item.user_id}</font>", body_style),
                Paragraph(f"{item.group_name}<br/><font size='7'>{item.role_name}</font>", body_style),
                Paragraph(item.status, body_style),
                Paragraph(score_label, body_style),
                Paragraph(item.mbti_type or "Нет данных", body_style),
                Paragraph(date_label, body_style),
            ])

        reports_table = Table(
            table_data,
            colWidths=[68 * mm, 58 * mm, 34 * mm, 28 * mm, 28 * mm, 28 * mm],
            repeatRows=1,
        )
        reports_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9ecfb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#202334")),
                    ("FONTNAME", (0, 0), (-1, -1), self.FONT_NAME),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d9def3")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e6e9f6")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(reports_table)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return "admin_detailed_reports.pdf", pdf_bytes


admin_reports_pdf_service = AdminReportsPdfService()
