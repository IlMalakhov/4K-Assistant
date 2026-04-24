from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class AdminReportDialoguePdfService:
    FONT_NAME = "ArialUnicodeAgent4KAdminDialogue"
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

    def build_pdf(self, detail) -> tuple[str, bytes]:
        self._ensure_font()
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "AdminDialogueTitle",
            parent=styles["Heading1"],
            fontName=self.FONT_NAME,
            fontSize=20,
            leading=26,
            textColor=colors.HexColor("#202334"),
            alignment=TA_LEFT,
            spaceAfter=10,
        )
        subtitle_style = ParagraphStyle(
            "AdminDialogueSubtitle",
            parent=styles["BodyText"],
            fontName=self.FONT_NAME,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#6f7690"),
            spaceAfter=10,
        )
        section_style = ParagraphStyle(
            "AdminDialogueSection",
            parent=styles["Heading2"],
            fontName=self.FONT_NAME,
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#202334"),
            spaceBefore=8,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "AdminDialogueBody",
            parent=styles["BodyText"],
            fontName=self.FONT_NAME,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#2a2f45"),
            spaceAfter=6,
        )
        label_style = ParagraphStyle(
            "AdminDialogueLabel",
            parent=body_style,
            fontName=self.FONT_NAME,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#6f7690"),
            spaceAfter=3,
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=f"Диалог по кейсам — {detail.full_name}",
            author="Agent_4K",
        )

        story = [
            Paragraph("Диалог пользователя с агентом", title_style),
            Paragraph(
                f"{detail.full_name} • {detail.role_name} • Сессия #{detail.session_id}",
                subtitle_style,
            ),
        ]

        for item in detail.case_items:
            story.append(Spacer(1, 6))
            story.append(
                Paragraph(
                    f"Кейс {item.case_number}. {item.case_title}",
                    section_style,
                )
            )
            if item.personalized_context:
                story.append(Paragraph("Вводные данные", label_style))
                story.append(Paragraph(item.personalized_context.replace("\n", "<br/>"), body_style))
            if item.personalized_task:
                story.append(Paragraph("Что нужно сделать", label_style))
                story.append(Paragraph(item.personalized_task.replace("\n", "<br/>"), body_style))

            if item.dialogue:
                story.append(Paragraph("Диалог", label_style))
                for message in item.dialogue:
                    role_label = "Пользователь" if message.role == "user" else "Ассистент"
                    story.append(
                        Paragraph(
                            f"<b>{role_label}:</b> {(message.message_text or '').replace(chr(10), '<br/>')}",
                            body_style,
                        )
                    )
            else:
                story.append(Paragraph("Диалог по кейсу не сохранен.", body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        raw_name = str(detail.full_name or "user")
        safe_name = "".join(ch if (ch.isascii() and (ch.isalnum() or ch in ("_", "-"))) else "_" for ch in raw_name)
        safe_name = safe_name.strip("_") or "user"
        return f"admin_dialogue_{detail.session_id}_{safe_name}.pdf", pdf_bytes

    def build_case_pdf(self, detail, case_item) -> tuple[str, bytes]:
        self._ensure_font()
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "AdminDialogueCaseTitle",
            parent=styles["Heading1"],
            fontName=self.FONT_NAME,
            fontSize=20,
            leading=26,
            textColor=colors.HexColor("#202334"),
            alignment=TA_LEFT,
            spaceAfter=10,
        )
        subtitle_style = ParagraphStyle(
            "AdminDialogueCaseSubtitle",
            parent=styles["BodyText"],
            fontName=self.FONT_NAME,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#6f7690"),
            spaceAfter=10,
        )
        section_style = ParagraphStyle(
            "AdminDialogueCaseSection",
            parent=styles["Heading2"],
            fontName=self.FONT_NAME,
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#202334"),
            spaceBefore=8,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "AdminDialogueCaseBody",
            parent=styles["BodyText"],
            fontName=self.FONT_NAME,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#2a2f45"),
            spaceAfter=6,
        )
        label_style = ParagraphStyle(
            "AdminDialogueCaseLabel",
            parent=body_style,
            fontName=self.FONT_NAME,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#6f7690"),
            spaceAfter=3,
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
            title=f"Диалог по кейсу — {case_item.case_title}",
            author="Agent_4K",
        )

        story = [
            Paragraph("Диалог по кейсу", title_style),
            Paragraph(
                f"{detail.full_name} • {detail.role_name} • Сессия #{detail.session_id} • Кейс {case_item.case_number}",
                subtitle_style,
            ),
            Paragraph(case_item.case_title or "Кейс без названия", section_style),
        ]

        if case_item.personalized_context:
            story.append(Paragraph("Вводные данные", label_style))
            story.append(Paragraph(case_item.personalized_context.replace("\n", "<br/>"), body_style))
        if case_item.personalized_task:
            story.append(Paragraph("Что нужно сделать", label_style))
            story.append(Paragraph(case_item.personalized_task.replace("\n", "<br/>"), body_style))

        story.append(Paragraph("Диалог", label_style))
        if case_item.dialogue:
            for message in case_item.dialogue:
                role_label = "Пользователь" if message.role == "user" else "Ассистент"
                story.append(
                    Paragraph(
                        f"<b>{role_label}:</b> {(message.message_text or '').replace(chr(10), '<br/>')}",
                        body_style,
                    )
                )
        else:
            story.append(Paragraph("Диалог по кейсу не сохранен.", body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        raw_name = str(detail.full_name or "user")
        safe_name = "".join(ch if (ch.isascii() and (ch.isalnum() or ch in ("_", "-"))) else "_" for ch in raw_name)
        safe_name = safe_name.strip("_") or "user"
        return f"admin_case_dialogue_{detail.session_id}_{case_item.session_case_id}_{safe_name}.pdf", pdf_bytes


admin_report_dialogue_pdf_service = AdminReportDialoguePdfService()
