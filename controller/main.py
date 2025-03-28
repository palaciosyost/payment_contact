from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.translate import _  # 👈 ESTA LÍNEA AGREGA LA FUNCIÓN _()
import requests
import logging
import json
_logger = logging.getLogger(__name__)
import re



class SunatApiController(http.Controller):

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

