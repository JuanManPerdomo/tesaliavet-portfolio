import csv
import io
import math
from datetime import datetime
from xml.sax.saxutils import escape as _xml_escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend

# Paleta - mismos tokens que ya usa el resto del panel (Tailwind emerald/slate,
# decision 2/9: nunca colores sueltos, siempre la paleta ya establecida).
BRAND_GREEN = colors.HexColor('#047857')       # emerald-700
BRAND_GREEN_DARK = colors.HexColor('#065f46')  # emerald-800
SLATE_900 = colors.HexColor('#0f172a')
SLATE_500 = colors.HexColor('#64748b')
SLATE_400 = colors.HexColor('#94a3b8')
SLATE_100 = colors.HexColor('#f1f5f9')
SLATE_200 = colors.HexColor('#e2e8f0')
CHART_PALETTE = [
    BRAND_GREEN, colors.HexColor('#0ea5e9'), colors.HexColor('#f59e0b'),
    colors.HexColor('#8b5cf6'), colors.HexColor('#ef4444'), colors.HexColor('#64748b'),
]

PAGE_SIZE = letter
MARGIN = 1.6 * cm
HEADER_HEIGHT = 1.8 * cm
CONTENT_WIDTH = PAGE_SIZE[0] - 2 * MARGIN


def _esc(value):
    """Escapa valores reales (nombres de clientes, referencias, etc.) antes de
    interpolarlos en un Paragraph - Paragraph parsea su contenido como XML
    liviano, asi que un '&' o '<' suelto en un dato real (ej. razon social,
    nota de un cliente) rompia el render sin avisar. Las celdas de Table NO
    pasan por este parser (van directo a texto plano), asi que no lo
    necesitan."""
    return _xml_escape(str(value))


def _compact_amount(value):
    """1234567 -> '1.2M', 45000 -> '45K', 320 -> '320' - evita ejes con
    numeros largos que se amontonan entre si."""
    value = float(value)
    sign = '-' if value < 0 else ''
    value = abs(value)
    if value >= 1_000_000:
        text = f'{value / 1_000_000:.1f}'.rstrip('0').rstrip('.')
        return f'{sign}{text}M'
    if value >= 1_000:
        return f'{sign}{value / 1_000:.0f}K'
    return f'{sign}{value:,.0f}'


def _axis_currency_formatter(value):
    return f'$ {_compact_amount(value)}'


def _axis_number_formatter(value):
    return _compact_amount(value)


def _truncate_label(text, max_len=14):
    """Nombres reales (productos, clientes) pueden ser mucho mas largos que
    el espacio de un eje de categorias - sin truncar, 2-3 nombres largos se
    superponen entre si y quedan ilegibles."""
    text = str(text)
    return text if len(text) <= max_len else text[:max_len - 1].rstrip() + '…'


def build_csv(title, kpis, headers, rows):
    """CSV con un pequeno encabezado (titulo, fecha, KPIs) antes de la tabla -
    mismo contenido que ya trae el PDF, para que abrir el CSV en Excel diga de
    un vistazo de que reporte se trata, sin depender del nombre del archivo.
    BOM UTF-8 al inicio: sin el, Excel no siempre detecta la codificacion y
    muestra las tildes/enies mal, aunque el archivo en si este bien
    codificado."""
    buffer = io.StringIO()
    buffer.write('﻿')
    writer = csv.writer(buffer)
    writer.writerow([title])
    writer.writerow([f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}'])
    writer.writerow([])
    if kpis:
        for label, value in kpis:
            writer.writerow([label, value])
        writer.writerow([])
    writer.writerow(headers)
    writer.writerows(rows)
    return buffer.getvalue()


def _draw_letterhead(canvas, doc):
    """Membrete de marca + pie de pagina, dibujado en cada pagina via el
    callback onFirstPage/onLaterPages de SimpleDocTemplate - mismo mecanismo
    estandar de reportlab para encabezados/pies repetidos."""
    canvas.saveState()
    page_w, page_h = PAGE_SIZE

    canvas.setFillColor(BRAND_GREEN)
    canvas.rect(0, page_h - HEADER_HEIGHT, page_w, HEADER_HEIGHT, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 15)
    canvas.drawString(MARGIN, page_h - HEADER_HEIGHT + 0.6 * cm, 'TesaliaVet')
    canvas.setFont('Helvetica', 8.5)
    canvas.drawRightString(page_w - MARGIN, page_h - HEADER_HEIGHT + 0.65 * cm, 'Agroveterinaria Tesalia · Tesalia, Huila')

    canvas.setStrokeColor(SLATE_200)
    canvas.line(MARGIN, 1.4 * cm, page_w - MARGIN, 1.4 * cm)
    canvas.setFillColor(SLATE_400)
    canvas.setFont('Helvetica', 7.5)
    canvas.drawString(MARGIN, 1.1 * cm, f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    canvas.drawRightString(page_w - MARGIN, 1.1 * cm, f'Página {doc.page}')
    canvas.restoreState()


def _kpi_grid(kpis, styles):
    """KPIs como tarjetas (fondo gris claro, valor grande en negrita) en vez
    de una lista de texto suelta - mismo lenguaje visual que las tarjetas KPI
    del panel (KpiTile.vue, decision 27/47), en 3 columnas."""
    if not kpis:
        return None
    label_style = ParagraphStyle('kpiLabel', fontName='Helvetica', fontSize=7.5, textColor=SLATE_500, leading=10)
    value_style = ParagraphStyle('kpiValue', fontName='Helvetica-Bold', fontSize=13, textColor=SLATE_900, leading=16, spaceBefore=2)

    cards = [[Paragraph(_esc(label).upper(), label_style), Paragraph(_esc(value), value_style)] for label, value in kpis]

    cols = 3 if len(cards) >= 3 else len(cards)
    rows_data = [cards[i:i + cols] for i in range(0, len(cards), cols)]
    for row in rows_data:
        while len(row) < cols:
            row.append('')

    col_width = CONTENT_WIDTH / cols
    table = Table(rows_data, colWidths=[col_width] * cols)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SLATE_100),
        ('BOX', (0, 0), (-1, -1), 0.5, SLATE_200),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return table


def _bar_chart_drawing(chart, width):
    labels = [_truncate_label(v) for v in chart.get('labels', [])]
    values = [float(v) for v in chart.get('values', [])]
    if not values:
        return None

    height = 6.5 * cm
    drawing = Drawing(width, height)

    bc = VerticalBarChart()
    bc.x = 45
    bc.y = 40
    bc.width = width - 65
    bc.height = height - 55
    bc.data = [values]
    bc.strokeColor = None
    bc.bars[0].fillColor = chart.get('color', BRAND_GREEN)
    bc.bars[0].strokeColor = None
    bc.barWidth = 8

    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontSize = 6.5
    bc.categoryAxis.labels.fillColor = SLATE_500
    if len(labels) > 4:
        bc.categoryAxis.labels.angle = 35
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.boxAnchor = 'e'
    else:
        bc.categoryAxis.labels.dy = -4
    bc.categoryAxis.strokeColor = SLATE_200
    bc.categoryAxis.visibleGrid = False

    is_currency = chart.get('format') == 'currency'
    if min(values) >= 0:
        bc.valueAxis.valueMin = 0
    if not is_currency:
        # Rangos chicos (conteos: 0-10 unidades) - sin esto, reportlab elige
        # ticks fraccionarios (0.16, 0.33...) que redondeados dan "0" y "1"
        # repetidos en el eje.
        max_val = max((abs(v) for v in values), default=1) or 1
        bc.valueAxis.valueStep = max(1, math.ceil(max_val / 5))
    bc.valueAxis.labels.fontSize = 7
    bc.valueAxis.labels.fillColor = SLATE_500
    bc.valueAxis.strokeColor = SLATE_200
    bc.valueAxis.gridStrokeColor = SLATE_100
    bc.valueAxis.visibleGrid = True
    bc.valueAxis.labelTextFormat = _axis_currency_formatter if is_currency else _axis_number_formatter

    drawing.add(bc)
    return drawing


def _pie_chart_drawing(chart, width):
    labels = [_truncate_label(v, max_len=20) for v in chart.get('labels', [])]
    values = [float(v) for v in chart.get('values', [])]
    pairs = [(label, value) for label, value in zip(labels, values) if value > 0]
    if not pairs:
        return None

    # Top 5 + "Otros" para no saturar la leyenda con muchas categorias chicas
    # (ej. Clientes por ciudad, con decenas de ciudades distintas).
    pairs.sort(key=lambda p: p[1], reverse=True)
    if len(pairs) > 6:
        rest_total = sum(v for _, v in pairs[5:])
        pairs = pairs[:5] + [('Otros', rest_total)]
    labels, values = zip(*pairs)
    total = sum(values)

    height = 6.5 * cm
    drawing = Drawing(width, height)

    pie = Pie()
    pie.x = 15
    pie.y = height / 2 - 55
    pie.width = 110
    pie.height = 110
    pie.data = list(values)
    pie.labels = None
    pie.slices.strokeColor = colors.white
    pie.slices.strokeWidth = 1.5
    for i in range(len(values)):
        pie.slices[i].fillColor = CHART_PALETTE[i % len(CHART_PALETTE)]
    drawing.add(pie)

    legend = Legend()
    legend.x = 150
    legend.y = height - 15
    legend.dx = 7
    legend.dy = 7
    legend.dxTextSpace = 5
    legend.deltay = 12
    legend.fontSize = 7.5
    legend.alignment = 'left'
    legend.columnMaximum = 6
    legend.colorNamePairs = [
        (CHART_PALETTE[i % len(CHART_PALETTE)], f'{labels[i]} — {values[i] / total * 100:.0f}%')
        for i in range(len(labels))
    ]
    drawing.add(legend)
    return drawing


def _dispatch_chart(chart, width):
    if chart.get('type') == 'pie':
        return _pie_chart_drawing(chart, width)
    return _bar_chart_drawing(chart, width)


def _charts_section(charts, styles):
    """Grafico(s) reales (vectoriales, reportlab.graphics - sin depender de
    matplotlib ni de ningun servicio externo, decision 2) en filas de a 2
    lado a lado; si sobra uno solo, ocupa el ancho completo en vez de dejar
    la mitad de la fila en blanco."""
    if not charts:
        return []
    valid = [c for c in charts if c.get('values') and any(float(v) for v in c['values'])]
    if not valid:
        return []

    title_style = ParagraphStyle(
        'chartTitle', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=9.5, textColor=SLATE_900, spaceAfter=4,
    )
    gutter = 0.6 * cm
    half_width = (CONTENT_WIDTH - gutter) / 2

    elements = []
    i = 0
    n = len(valid)
    while i < n:
        if n - i == 1:
            chart = valid[i]
            drawing = _dispatch_chart(chart, CONTENT_WIDTH)
            if drawing:
                elements.append(Paragraph(_esc(chart.get('title', '')), title_style))
                elements.append(drawing)
                elements.append(Spacer(1, 0.5 * cm))
            i += 1
        else:
            left, right = valid[i], valid[i + 1]
            left_drawing = _dispatch_chart(left, half_width)
            right_drawing = _dispatch_chart(right, half_width)
            cell_left = [Paragraph(_esc(left.get('title', '')), title_style), left_drawing] if left_drawing else ''
            cell_right = [Paragraph(_esc(right.get('title', '')), title_style), right_drawing] if right_drawing else ''
            row_table = Table([[cell_left, cell_right]], colWidths=[half_width + gutter / 2, half_width + gutter / 2])
            row_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), gutter),
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ]))
            elements.append(row_table)
            elements.append(Spacer(1, 0.5 * cm))
            i += 2
    return elements


def build_pdf(title, kpis, headers, rows, charts=None, subtitle=None):
    """PDF con membrete de marca, KPIs como tarjetas, graficos vectoriales
    reales (cuando se pasan) y una tabla de detalle - un solo generador
    compartido por los 5 reportes (decision 52) y el recibo interno de un
    pedido (decision 41/87)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=PAGE_SIZE, title=_esc(title),
        topMargin=HEADER_HEIGHT + 0.8 * cm, bottomMargin=1.8 * cm,
        leftMargin=MARGIN, rightMargin=MARGIN,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'reportTitle', parent=styles['Title'], textColor=BRAND_GREEN_DARK,
        fontSize=18, leading=22, spaceAfter=2, alignment=0,
    )
    subtitle_style = ParagraphStyle('reportSubtitle', parent=styles['Normal'], textColor=SLATE_500, fontSize=9.5)

    elements = [
        Paragraph(_esc(title), title_style),
        Paragraph(_esc(subtitle) if subtitle else f'Generado el {datetime.now().strftime("%d/%m/%Y, %H:%M")}', subtitle_style),
        Spacer(1, 0.35 * cm),
        HRFlowable(width='100%', thickness=1.2, color=SLATE_200),
        Spacer(1, 0.5 * cm),
    ]

    kpi_table = _kpi_grid(kpis, styles)
    if kpi_table:
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.7 * cm))

    elements.extend(_charts_section(charts, styles))

    if headers:
        section_title_style = ParagraphStyle(
            'sectionTitle', parent=styles['Normal'], fontName='Helvetica-Bold',
            fontSize=10.5, textColor=SLATE_900, spaceAfter=6,
        )
        elements.append(Paragraph('Detalle', section_title_style))

        if rows:
            table_data = [headers] + [[str(cell) for cell in row] for row in rows]
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), BRAND_GREEN),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, SLATE_200),
                ('BOX', (0, 0), (-1, -1), 0.75, SLATE_200),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SLATE_100]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph('Sin datos para este período.', styles['Normal']))
    elif not kpi_table and not charts:
        elements.append(Paragraph('Sin datos para este período.', styles['Normal']))

    doc.build(elements, onFirstPage=_draw_letterhead, onLaterPages=_draw_letterhead)
    return buffer.getvalue()
