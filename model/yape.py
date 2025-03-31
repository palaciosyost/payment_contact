from odoo import models, fields


class PaymentProviderYape(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('yape', "Yape")], ondelete={'yape': 'set default'})
    yape_qr = fields.Binary(string="Código QR")
    yape_holder_name = fields.Char(string="Nombre del Titular")
    yape_phone = fields.Char(string="Teléfono del Titular")

    def _get_default_payment_method_type(self):
        if self.code == 'yape':
            return 'form'
        return super()._get_default_payment_method_type()

    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['yape'] = {
            'mode': 'form',
            'support_tokenization': False,
            'auth_required': False,
        }
        return res
class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        self.ensure_one()
        return {
            'reference': self.reference,
            'amount': self.amount,
            'currency': self.currency_id.name,
        }

    def _get_specific_rendering_context(self):
        self.ensure_one()
        if self.provider_code == 'yape':
            return {
                'return_url': '/shop/confirmation',
            }
        return super()._get_specific_rendering_context()

    def _process_feedback_data(self, data):
        if self.provider_code != 'yape':
            return super()._process_feedback_data(data)
        self._set_transaction_done()
        if self.sale_order_id:
            self.sale_order_id.write({'state': 'sent'})
        return True
