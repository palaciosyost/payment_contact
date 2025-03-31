# -*- coding: utf-8 -*-
from odoo import models, fields

# _logger = logging.getLogger(__name__)

class PaymentProviderYape(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('yape', "Yape")],
        ondelete={'yape': 'set default'}
    )
    yape_qr = fields.Binary(string="Código QR")
    yape_holder_name = fields.Char(string="Nombre del Titular")
    yape_phone = fields.Char(string="Teléfono")


    def _get_default_payment_method_code(self):
        if self.code == 'yape':
            return 'manual'
        return super()._get_default_payment_method_code()

    def _get_redirect_form_html(self, tx_values):
        if self.code == 'yape':
            return """
                <form id="o_payment_redirect_form" action="/payment/yape/redirect" method="get">
                </form>
                <script>
                    document.getElementById("o_payment_redirect_form").submit();
                </script>
            """
        return super()._get_redirect_form_html(tx_values)
class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    def _get_processing_values(self):
        if self.provider_code == 'yape':
            """Return the values used to process the transaction."""
            import pprint
            import logging

            _logger = logging.getLogger(__name__)
            self.ensure_one()

            processing_values = {
                'provider_id': self.provider_id.id,
                'provider_code': self.provider_code,
                'reference': self.reference,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
            }

            # 🔁 Agrega datos específicos del proveedor
            processing_values.update(self._get_specific_processing_values(processing_values))

            # ✅ Agrega redirect_form_html directamente si es Yape
            if self.provider_code == 'yape' and self.operation in ('online_redirect', 'validation'):
                redirect_form_html = self.provider_id._get_redirect_form_html(processing_values)
                processing_values.update(redirect_form_html=redirect_form_html)

            _logger.info(
                "🟡 Valores de procesamiento para transacción %s:\n%s",
                self.reference,
                pprint.pformat(processing_values),
            )

            return processing_values
        return super()._get_processing_values()