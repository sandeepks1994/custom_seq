# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'


    # def _get_sequence(self):
    #     res= super(AccountMove, self)._get_sequence()
    #     print("a"*88,res,self)
    #     if self.type=='out_invoice':
    #         seq_code = self.env['ir.config_parameter'].sudo().get_param('custom_seq.seq_code') or False
    #         print("b"*88,seq_code)
    #         if seq_code == 'customer':
    #             final_seq=self.env['ir.sequence'].next_by_code('account.invoice.sequence') or _('New')
    #             print("c"*88,final_seq)
    #     return res

    def post(self):
        # `user_has_group` won't be bypassed by `sudo()` since it doesn't change the user anymore.
        if not self.env.su and not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_("You don't have the access rights to post an invoice."))
        for move in self:
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.today():
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(_("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(_("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0, precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date and move.is_invoice(include_receipts=True):
                move.invoice_date = fields.Date.context_today(self)
                move.with_context(check_move_validity=False)._onchange_invoice_date()

            # When the accounting date is prior to the tax lock date, move it automatically to the next available date.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (move.line_ids.tax_ids or move.line_ids.tag_ids):
                move.date = move.company_id.tax_lock_date + timedelta(days=1)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in self:
            if move.auto_post and move.date > fields.Date.today():
                raise UserError(_("This move is configured to be auto-posted on {}".format(move.date.strftime(get_lang(self.env).date_format))))

            move.message_subscribe([p.id for p in [move.partner_id] if p not in move.sudo().message_partner_ids])

            to_write = {'state': 'posted'}
            if move.name == '/':
                # Get the journal's sequence.
                sequence = move._get_sequence()
                if not sequence:
                    raise UserError(_('Please define a sequence on your journal.'))

                # Consume a new number.
                seq_code = self.env['ir.config_parameter'].sudo().get_param('custom_seq.seq_code') or False
                if self.type=='out_invoice' and seq_code != 'default':
                    final_seq = ''
                    sequence = ''
                    # if seq_code == 'customer':
                    sequence=self.env['ir.sequence'].next_by_code('account.invoice.sequence') or _('New')
                    # elif seq_code == 'product_categ':
                    #     sequence=self.env['ir.sequence'].next_by_code('account.invoice.sequence') or _('New')
                    if seq_code == 'customer' and self.partner_id:
                        final_seq =  self.partner_id.customer_code
                    elif seq_code == 'product_categ' and self.invoice_line_ids:
                        final_seq =  self.invoice_line_ids[0].product_id and self.invoice_line_ids[0].product_id.categ_id.c_code  
                    year = datetime.datetime.now().year
                    final_seq = final_seq + sequence + "/"+ str(year)    
                    to_write['name'] = final_seq
                else:
                    to_write['name'] = sequence.with_context(ir_sequence_date=move.date).next_by_id()
            move.write(to_write)
            # Compute 'ref' for 'out_invoice'.
            if move.type == 'out_invoice' and not move.invoice_payment_ref:
                to_write = {
                    'invoice_payment_ref': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['invoice_payment_ref']}))
                move.write(to_write)

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date

        for move in self:
            if not move.partner_id: continue
            partners = (move.partner_id | move.partner_id.commercial_partner_id)
            if move.type.startswith('out_'):
                partners._increase_rank('customer_rank')
            elif move.type.startswith('in_'):
                partners._increase_rank('supplier_rank')
            else:
                continue

        # Trigger action for paid invoices in amount is zero
        self.filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        ).action_invoice_paid()

        # Force balance check since nothing prevents another module to create an incorrect entry.
        # This is performed at the very end to avoid flushing fields before the whole processing.
        self._check_balanced()
        return True
