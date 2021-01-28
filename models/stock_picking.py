from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        if 'picking_type_id' in vals:
            picking_type_id = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            seq_code = self.env['ir.config_parameter'].sudo().get_param('custom_seq.seq_code')
            final_seq = ''
            sequence = ''
            final_sequence = '' 
            sequence=self.env['ir.sequence'].next_by_code('delivery.note.sequence') or _('New')
            if picking_type_id and picking_type_id.code == 'outgoing' and seq_code != 'default':
                if seq_code == 'customer' and 'partner_id' in vals:
                    partner_id = self.env['res.partner'].browse(vals['partner_id'])
                    final_seq =  partner_id and partner_id.customer_code or ''
                elif seq_code == 'product_categ' and 'move_ids_without_package' in vals and 'product_id' in vals['move_ids_without_package'][0][2]:
                    product_id = self.env['product.product'].browse(vals['move_ids_without_package'][0][2]['product_id'])
                    final_seq =  product_id and product_id.categ_id.c_code or '' 
                year = datetime.datetime.now().year
                final_sequence = final_seq + sequence + "/"+ str(year)   
                vals['name'] = final_sequence
            res = super(StockPicking, self).create(vals)
            return res



