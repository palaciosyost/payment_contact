from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.translate import _  # 👈 ESTA LÍNEA AGREGA LA FUNCIÓN _()
import requests
import logging
import json
_logger = logging.getLogger(__name__)
import re
from odoo.addons.payment.controllers import portal as payment_portal
from werkzeug.utils import redirect

from odoo.addons.payment.controllers.portal import PaymentPortal
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
# -*- coding: utf-8 -*-

from odoo import _, http
from odoo.addons.website_sale.controllers import main
from odoo.exceptions import AccessError, MissingError, ValidationError


from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentPortal
from werkzeug.utils import redirect


class PaymentPortalYape(PaymentPortal):

    @http.route(['/shop/payment/transaction/<int:order_id>'], type='http', auth='public', website=True, csrf=False)
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        order = self._document_check_access('sale.order', order_id, access_token)

        payment_tx = request.env['payment.transaction'].sudo().search([
            ('sale_order_ids', 'in', [order_id])
        ], limit=1)

        if payment_tx and payment_tx.provider_id.code == 'yape':
            if order.state == 'draft':
                order.write({'state': 'sent'})

            request.session.pop('sale_last_order_id', None)  # Limpiar sesión previa
            request.session['sale_last_order_id'] = order_id  # Guardar la nueva orden

            _logger.info(f"🔄 Redirigiendo a /shop/confirmation con la orden {order_id}")

            return request.redirect('/shop/confirmation')


        return super().shop_payment_transaction(order_id, access_token, **kwargs)



    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        """ Controlador del proceso de confirmación del pago """
        
        sale_order_id = request.session.get('sale_last_order_id')
        print(f"🔍 Sale Order ID en sesión: {sale_order_id}")  # Debug

        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            print(f"🔍 Order encontrada: {order.name}")  # Debug

            # Verificar si el pago fue con Yape
            is_yape = any(tx.provider_id.code == 'yape' for tx in order.transaction_ids)
            print(f"🔍 Es pago con Yape: {is_yape}")  # Debug
            
            # Preparar los valores para la plantilla
            values = {
                'order': order,
                'is_yape': is_yape,
                'website_sale_order': order,  # Compatible con plantillas estándar
            }

            return request.render("website_sale.confirmation", values)
        
        else:
            print("⚠ No hay Sale Order ID en sesión")
            return request.redirect('/shop')




class SunatApiController(http.Controller):


    # @http.route('/payment/sent/<string:order_id>', type='http', auth='public', csrf=False)
    # def sale_payment (self, order_id):
    #     order = request.env["sale.order"].sudo().search([("id", "=", int(order_id))])
    #     return request.render("payment_contact.yape_payment_confirmation", {'order': order})


    @http.route('/api/consulta_documento/<string:numero>', type='http', auth='public', csrf=False, methods=['GET'])
    def consulta_documento(self, numero):
        if not numero:
            return request.make_response(
                '{"error": "Número de documento no proporcionado"}',
                headers=[('Content-Type', 'application/json')]
            )

        token_api = request.env.company.token_api
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

