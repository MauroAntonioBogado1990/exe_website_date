from odoo import models, fields

class PartnerInherit(models.Model):
    _inherit = 'res.partner'

    property_product_pricelist = fields.Many2one(
        'product.pricelist',
        string='Tarifa',
        domain="[('active', '=', True)]",  # o el dominio que vos quieras
    )