from odoo import models, api, fields, _

class ResCompany(models.Model):
    _inherit = "res.company"

    api_mode = fields.Selection(
        selection=[
            ("api_net", "API NET")
        ],
        string="API a usar"
    )
    token_api = fields.Char(string="Token")
    token_api_yape = fields.Char(string="Token")
