from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            final_seq = ''
            sequence = ''
            final_sequence = ''
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            seq_code = self.env['ir.config_parameter'].sudo().get_param('custom_seq.seq_code') or False    
            if seq_code != 'default':
                if 'company_id' in vals:
                    sequence = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                        'sale.quotation.sequence', sequence_date=seq_date) or _('New')
                else:
                    sequence = self.env['ir.sequence'].next_by_code('sale.quotation.sequence', sequence_date=seq_date) or _('New')
                print("z"*88,seq_code,vals['partner_id'],vals['order_line'][0][2]['product_id'],vals)    
                if seq_code == 'customer' and 'partner_id' in vals:
                    partner_id = self.env['res.partner'].browse(vals['partner_id'])
                    final_seq =  partner_id and partner_id.customer_code or ''
                elif seq_code == 'product_categ' and 'order_line' in vals and 'product_id' in vals['order_line'][0][2]:
                    product_id = self.env['product.product'].browse(vals['order_line'][0][2]['product_id'])
                    final_seq =  product_id and product_id.categ_id.c_code or ''
                year = datetime.datetime.now().year
                final_sequence = final_seq + sequence + "/"+ str(year)    
                vals['name'] = final_sequence
        result = super(SaleOrder, self).create(vals)
        return result