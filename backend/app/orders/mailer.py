from ..emails.sender import format_cop, frontend_url, render_shell, send_email

STATUS_LABELS = {
    'Pendiente': 'Pendiente de pago',
    'Pagado': 'Pagado',
    'Entregado': 'Entregado',
    'Cancelado': 'Cancelado',
}


def _order_url(order):
    return frontend_url(f'/mis-pedidos/{order.id}')


def _items_table(order):
    rows = ''.join(
        f"""
          <tr>
            <td style="padding:8px 0; border-bottom:1px solid #e2e8f0; color:#0f172a; font-size:13px;">{item.product.name if item.product else 'Producto eliminado'}</td>
            <td style="padding:8px 0; border-bottom:1px solid #e2e8f0; color:#475569; font-size:13px; text-align:center;">{float(item.quantity):g}</td>
            <td style="padding:8px 0; border-bottom:1px solid #e2e8f0; color:#0f172a; font-size:13px; text-align:right;">{format_cop(item.total or 0)}</td>
          </tr>
        """
        for item in order.items
    )
    return f"""
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:4px;">
        <tr>
          <td style="padding:6px 0; color:#94a3b8; font-size:11px; font-weight:700; text-transform:uppercase;">Producto</td>
          <td style="padding:6px 0; color:#94a3b8; font-size:11px; font-weight:700; text-transform:uppercase; text-align:center;">Cant.</td>
          <td style="padding:6px 0; color:#94a3b8; font-size:11px; font-weight:700; text-transform:uppercase; text-align:right;">Total</td>
        </tr>
        {rows}
        <tr>
          <td colspan="2" style="padding-top:10px; color:#0f172a; font-size:14px; font-weight:700; text-align:right;">Total</td>
          <td style="padding-top:10px; color:#065f46; font-size:14px; font-weight:700; text-align:right;">{format_cop(order.total)}</td>
        </tr>
      </table>
    """


def send_order_confirmed(order):
    content_html = _items_table(order)
    html = render_shell(
        f'Recibimos tu pedido #{order.id}',
        f'Hola {order.user.first_name}, tu pedido quedó registrado y pendiente de pago. Recuerda que la recogida es únicamente en nuestra tienda física en Tesalia, Huila.',
        content_html,
        cta_label='Ver mi pedido',
        cta_url=_order_url(order),
    )
    text = (
        f'Hola {order.user.first_name}, recibimos tu pedido #{order.id} por {format_cop(order.total)}, '
        'pendiente de pago. La recogida es únicamente en nuestra tienda física en Tesalia, Huila.'
    )
    return send_email(order.user.email, f'Pedido #{order.id} confirmado - TesaliaVet', html, text)


def send_payment_registered(order, invoice, pdf_bytes):
    content_html = f"""
      <p style="margin:0 0 12px; color:#0f172a; font-size:14px;"><strong>Recibo:</strong> {invoice.invoice_number}</p>
      {_items_table(order)}
    """
    html = render_shell(
        f'Pago recibido - Pedido #{order.id}',
        f'Hola {order.user.first_name}, confirmamos el pago de tu pedido. Adjuntamos tu recibo en PDF.',
        content_html,
        cta_label='Ver mi pedido',
        cta_url=_order_url(order),
    )
    text = (
        f'Hola {order.user.first_name}, confirmamos el pago de tu pedido #{order.id} por {format_cop(order.total)}. '
        f'Tu recibo ({invoice.invoice_number}) va adjunto en PDF.'
    )
    return send_email(
        order.user.email, f'Pago recibido - Pedido #{order.id} - TesaliaVet', html, text,
        attachments=[(f'{invoice.invoice_number}.pdf', pdf_bytes, 'application/pdf')],
    )


def send_order_delivered(order):
    html = render_shell(
        f'Pedido #{order.id} entregado',
        f'Hola {order.user.first_name}, tu pedido ya fue entregado en tienda. ¡Gracias por comprar en TesaliaVet!',
        '',
        cta_label='Ver mi pedido',
        cta_url=_order_url(order),
    )
    text = f'Hola {order.user.first_name}, tu pedido #{order.id} ya fue entregado en tienda. ¡Gracias por comprar en TesaliaVet!'
    return send_email(order.user.email, f'Pedido #{order.id} entregado - TesaliaVet', html, text)


def send_order_cancelled(order):
    content_html = f"""
      <p style="margin:0; padding:14px; background:#fef2f2; border:1px solid #fecaca; border-radius:10px; color:#991b1b; font-size:13px;">
        <strong>Motivo:</strong> {order.cancel_reason or 'No especificado'}
      </p>
    """
    html = render_shell(
        f'Pedido #{order.id} anulado',
        f'Hola {order.user.first_name}, tu pedido fue anulado.',
        content_html,
        cta_label='Ver mi pedido',
        cta_url=_order_url(order),
    )
    text = (
        f'Hola {order.user.first_name}, tu pedido #{order.id} fue anulado. '
        f'Motivo: {order.cancel_reason or "No especificado"}.'
    )
    return send_email(order.user.email, f'Pedido #{order.id} anulado - TesaliaVet', html, text)


def send_return_processed(order, ret):
    content_html = f"""
      <p style="margin:0 0 8px; color:#0f172a; font-size:14px;"><strong>Monto reembolsado:</strong> {format_cop(ret.refund_amount)}</p>
      <p style="margin:0; color:#0f172a; font-size:14px;"><strong>Método:</strong> {ret.refund_method}</p>
    """
    html = render_shell(
        f'Devolución procesada - Pedido #{order.id}',
        f'Hola {order.user.first_name}, registramos una devolución sobre tu pedido.',
        content_html,
        cta_label='Ver mi pedido',
        cta_url=_order_url(order),
    )
    text = (
        f'Hola {order.user.first_name}, registramos una devolución de {format_cop(ret.refund_amount)} '
        f'({ret.refund_method}) sobre tu pedido #{order.id}.'
    )
    return send_email(order.user.email, f'Devolución procesada - Pedido #{order.id} - TesaliaVet', html, text)
