from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.translate import _  # 👈 ESTA LÍNEA AGREGA LA FUNCIÓN _()
import requests
import logging
import json
_logger = logging.getLogger(__name__)
import re
import urllib.parse
import json

class SHOPcONFIRM (WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)

            # Obtener el proveedor de pago
            payment_provider = order.transaction_ids and order.transaction_ids[0].provider_id
            payment_code = payment_provider.code if payment_provider else None

            # Preparar valores para la plantilla
            values = self._prepare_shop_payment_confirmation_values(order)
            values['payment_provider'] = payment_provider
            values['payment_code'] = payment_code

            return request.render("website_sale.confirmation", values)
        else:
            return request.redirect('/shop')


class SunatApiController(http.Controller):
    
    @http.route('/shop/cart/whatsapp', type='http', auth="public", website=True)
    def whatsapp_cart(self, **kw):
        # Obtener la cotización activa (en estado 'draft') del usuario actual
        order = request.website.sale_get_order()
        
        if not order:
            return request.redirect('/shop/cart')  # Redirigir al carrito si no hay orden

        # Obtener el nforce_createúmero de cotización y los productos en el carrito
        cotizacion_numero = order.name
        productos = order.order_line

        # Construir el mensaje de WhatsApp con el número de cotización y productos
        mensaje = f"Hola, estoy interesado en la cotización {cotizacion_numero}. Aquí está el detalle:\n\n"
        
        for linea in productos:
            nombre_producto = linea.product_id.name
            cantidad = linea.product_uom_qty
            precio_unitario = linea.price_unit - (linea.discount * linea.price_unit / 100)
            subtotal = linea.price_total

            mensaje += f"*{nombre_producto}* \n"
            mensaje += f"  Cantidad: {cantidad}\n"
            mensaje += f"  Precio unitario: S/{precio_unitario:.2f}\n"
            mensaje += f"  Subtotal: S/{subtotal:.2f}\n\n"

        mensaje += f"Total: *S/{order.amount_total:.2f}*\n"
        mensaje += "Por favor, ¿podrían confirmar la disponibilidad?"

        # Codificar el mensaje para incluirlo en un enlace de WhatsApp
        mensaje_codificado = urllib.parse.quote(mensaje)
        numero_telefono = "51941476469"  # Reemplaza con el número de teléfono o permite ingresarlo dinámicamente
        enlace_whatsapp = f"https://wa.me/{numero_telefono}?text={mensaje_codificado}"
        print('---------------------------------------- ')
        print(enlace_whatsapp)
        order.write({'state': 'sent'})
        request.session['sale_order_id'] = None
        # Redirigir al usuario a WhatsApp
        return f"""
            <html>
                <head>
                    <script type="text/javascript">
                        window.location.href = "{enlace_whatsapp}";
                    </script>
                </head>
                <body>
                    Si no eres redirigido automáticamente, haz clic <a href="{enlace_whatsapp}">aquí</a>.
                </body>
            </html>
        """
 
    @http.route('/payment/yape/redirect', type='http', auth='public', website=True)
    def yape_payment_redirect(self, **kwargs):
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop')

        # Obtener proveedor y método de pago
        provider = request.env['payment.provider'].sudo().search([('code', '=', 'yape')], limit=1)
        payment_method = request.env['payment.method'].sudo().search([
            ('code', '=', 'yape'),
        ], limit=1) 
        tx = request.env['payment.transaction'].sudo().search([
            ('reference', '=', order.name),
            ('provider_id', '=', provider.id),
        ], limit=1)

        if not tx:
            tx = request.env['payment.transaction'].sudo().create({
                'provider_id': provider.id,
                'payment_method_id': payment_method.id,
                'amount': order.amount_total,
                'currency_id': order.currency_id.id,
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'state': 'pending',
                'sale_order_ids': [(6, 0, [order.id])],
            })
        request.session['sale_transaction_id'] = tx.id

        # Dejar el pedido como "Cotización enviada"
        order.state = 'sent'

        return request.redirect('/shop/confirmation')



    @http.route('/api/consulta_documento/<string:numero>', type='http', auth='public', csrf=False, methods=['GET'])
    def consulta_documento(self, numero):
        if not numero:
            return request.make_response(
                '{"error": "Número de documento no proporcionado"}',
                headers=[('Content-Type', 'application/json')]
            )

        token_api = request.env.company.token_api_yape
        if not token_api:
            return request.make_response(
                '{"error": "Token API no configurado en la compañía"}',
                headers=[('Content-Type', 'application/json')]
            )

        # Construir la URL
        if len(numero) == 8:
            url = f"https://api.apis.net.pe/v2/reniec/dni?numero={numero}&token={token_api}"
        elif len(numero) == 11:
            url = f"https://api.apis.net.pe/v2/sunat/ruc?numero={numero}&token={token_api}"
        else:
            return request.make_response(
                '{"error": "Número de documento inválido"}',
                headers=[('Content-Type', 'application/json')]
            )

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return request.make_response(
                response.text,
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error consultando documento {numero}: {e}")
            return request.make_response(
                '{"error": "No se pudo consultar el documento"}',
                headers=[('Content-Type', 'application/json')]
            )

