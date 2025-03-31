from odoo import models, fields

class PaymentProviderYape(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('yape', "Yape")], ondelete={'yape': 'set default'})
    yape_qr = fields.Binary(string="Código QR")
    yape_holder_name = fields.Char(string="Nombre del Titular")
    yape_phone = fields.Char(string="Teléfono del Titular")


    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['yape'] = {
            'mode': 'form',  # No 'manual'
            'form_template_id': 'website_sale.confirmation',
            'support_tokenization': False,
            'auth_required': False,
        }
        return res

# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """Valores para la pasarela (si necesitas QR o datos extra)"""
        if self.provider_code != 'yape':
            return super()._get_specific_rendering_values(processing_values)

        return {
            'reference': self.reference,
            'amount': self.amount,
            'currency': self.currency_id.name,
        }

    def _process_feedback_data(self, data):
        """Lógica cuando se recibe respuesta del pago (si fuera automático)"""
        if self.provider_code != 'yape':
            return super()._process_feedback_data(data)

        self._set_transaction_done()
        self.sale_order_id.write({'state': 'sent'})  # Estado enviado
        return True

    def _get_specific_rendering_context(self):
        """Renderiza la URL de redirección al hacer pago"""
        self.ensure_one()
        if self.provider_code != 'yape':
            return super()._get_specific_rendering_context()
        return {
            'return_url': '/shop/confirmation',
        }
