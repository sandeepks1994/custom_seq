# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ProductCategory(models.Model):
    _inherit = "product.category"

    c_code = fields.Char("Code")