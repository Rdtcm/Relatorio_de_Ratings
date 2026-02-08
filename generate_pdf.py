from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm

from dataclasses import asdict
from datetime import datetime
import pandas as pd
import os


class GeneratePDF:

    @staticmethod
    def _week_label_from_df(df):
        dates = pd.to_datetime(df["Data"], format="%d %b %Y", errors="coerce")
        dates = dates.dropna()

        if dates.empty:
            return ""

        start = dates.min()
        end = dates.max()

        meses = [
            "janeiro", "fevereiro", "março", "abril",
            "maio", "junho", "julho", "agosto",
            "setembro", "outubro", "novembro", "dezembro"
        ]

        mes = meses[end.month - 1]

        return f"({start.day} a {end.day} de {mes})"

    @classmethod
    def generate_pdf(cls, records, output_path="ratings.pdf"):
        """
        records: lista de RatingRecord
        """

        os.makedirs("output", exist_ok=True)
        output_path = os.path.join("output", output_path)

        # -------------------------
        # Converter para DataFrame
        # -------------------------
        df = pd.DataFrame([asdict(r) for r in records])

        df.rename(columns={
            "date": "Data",
            "company": "Emissor",
            "agency": "Agência",
            "rating_previous": "Rating Anterior",
            "rating_current": "Rating Atual",
            "outlook_previous": "Outlook Anterior",
            "outlook_current": "Outlook Atual",
            "action": "Ação de Rating",
        }, inplace=True)

        df["Rating / Perspectiva Anterior"] = (
            df["Rating Anterior"].fillna("") +
            " / " +
            df["Outlook Anterior"].fillna("")
        )

        df["Rating / Perspectiva Atual"] = (
            df["Rating Atual"].fillna("") +
            " / " +
            df["Outlook Atual"].fillna("")
        )

        df = df[[
            "Data",
            "Emissor",
            "Agência",  # acabei de adicionar, voce deve ajustar
            "Rating / Perspectiva Anterior",
            "Rating / Perspectiva Atual",
            "Ação de Rating"
        ]]

        # -------------------------
        # Documento
        # -------------------------
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        styles = getSampleStyleSheet()

        cell_style = ParagraphStyle(
            "cell",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            spaceAfter=0,
        )

        header_style = ParagraphStyle(
            "header",
            parent=styles["Normal"],
            fontSize=10,
            alignment=1,  # centro
            textColor=colors.white,
            spaceAfter=0,
            leading=12,
        )

        cell_center_style = ParagraphStyle(
            "cell_center",
            parent=cell_style,
            alignment=1,
        )

        title_style = ParagraphStyle(
            "title",
            parent=styles["Heading1"],
            alignment=TA_LEFT,
            fontSize=16,
            spaceAfter=8,
        )

        subtitle_style = ParagraphStyle(
            "subtitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#E57200"),
            spaceAfter=10,
        )

        footer_style = ParagraphStyle(
            "footer",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
        )

        elements = []

        elements.append(Paragraph("Ratings", title_style))
        week_label = cls._week_label_from_df(df)

        elements.append(
            Paragraph(
                f"Ações de Rating na Semana {week_label}",
                subtitle_style
            )
        )

        elements.append(Spacer(1, 6))

        # -------------------------
        # Tabela
        # -------------------------
        header = [Paragraph(col, header_style) for col in df.columns]

        body = []
        for _, row in df.iterrows():
            body.append([
                Paragraph(str(row["Data"]), cell_center_style),
                Paragraph(str(row["Emissor"]), cell_style),
                Paragraph(str(row["Agência"]), cell_center_style),
                Paragraph(
                    str(row["Rating / Perspectiva Anterior"]), cell_center_style),
                Paragraph(
                    str(row["Rating / Perspectiva Atual"]), cell_center_style),
                Paragraph(str(row["Ação de Rating"]), cell_center_style),
            ])

        table_data = [header] + body

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                25 * mm,   # Data
                85 * mm,   # Emissor
                30 * mm,   # Agência
                55 * mm,   # Rating anterior
                55 * mm,   # Rating atual
                30 * mm,   # Ação
            ]
        )

        style = TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),

            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),

            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.whitesmoke, colors.transparent]),
        ])

        # -------------------------
        # Cor por ação
        # -------------------------
        action_colors = {
            "Upgrade": (colors.HexColor("#C8E6C9"), colors.HexColor("#1B5E20")),
            "Elevado": (colors.HexColor("#C8E6C9"), colors.HexColor("#1B5E20")),

            "Downgrade": (colors.HexColor("#FFCDD2"), colors.HexColor("#B71C1C")),
            "Rebaixado": (colors.HexColor("#FFCDD2"), colors.HexColor("#B71C1C")),

            "Afirmado": (colors.HexColor("#E0E0E0"), colors.HexColor("#424242")),

            "Novo Rating": (colors.HexColor("#BBDEFB"), colors.HexColor("#0D47A1")),
        }

        for i, action in enumerate(df["Ação de Rating"], start=1):
            cfg = action_colors.get(action)
            if not cfg:
                continue

            bg_color, text_color = cfg

            style.add('BACKGROUND', (-1, i), (-1, i), bg_color)
            style.add('TEXTCOLOR', (-1, i), (-1, i), text_color)
            style.add('FONTNAME', (-1, i), (-1, i), 'Helvetica-Bold')

        table.setStyle(style)
        elements.append(table)

        # -------------------------
        # Rodapé Dinamico
        # -------------------------
        elements.append(Spacer(1, 10))
        agencies = (
            df["Agência"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        agencies = sorted(a for a in agencies.unique() if a)

        # Itaú BBA sempre fica presente
        fonte = ", ".join(agencies + ["Itaú BBA"])

        elements.append(
            Paragraph(
                f"Fonte: {fonte}.",
                footer_style
            )
        )

        doc.build(elements)
        return output_path
