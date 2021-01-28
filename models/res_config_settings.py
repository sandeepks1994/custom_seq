# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    seq_code = fields.Selection([('default', 'Default'), ('customer', 'Customer Code'), ('product_categ', 'Product Category Code')], 'Sequence Code', default='default')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(seq_code=self.env['ir.config_parameter'].sudo().get_param('custom_seq.seq_code'))
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('custom_seq.seq_code', self.seq_code)
        return res