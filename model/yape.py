# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('pago_yape', 'Yape')],
        ondelete={'pago_yape': 'set default'}
    )
    qr_yape = fields.Binary(string="QR de Yape")
    titular_yape = fields.Char(string="Nombre del titular")
    numero_yape = fields.Char(string="Número de titular")

    def _get_default_auth_method(self):
        return 'manual'

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist Culqi providers for unsupported currencies. """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)
        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in ('PEN', 'USD'):
            providers = providers.filtered(lambda p: p.code != 'pago_yape')

        return providers

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _handle_notification_data(self, data):
        if self.provider_code != 'pago_yape':
            return super()._handle_notification_data(data)
        # 👉 Lógica de respuesta/validación del pago aquí
        self._set_transaction_done()
