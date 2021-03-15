# -*- coding: utf-8 -*-
"""
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT section below).
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2019 Bernard K Too<bernard.too@optima.co.ke>
"""
import logging
from odoo import fields, models, api, _
LOGGER = logging.getLogger(__name__)


class PaymentMpesaOnline(models.Model):
    """
    model and methods  for handling and storing mpesa
    online data received through the json CallBackURL
    """
    _name = 'mpesa.online'
    _description = 'Mpesa Online Data from Safaricom'
    _order = 'id desc'

    amount = fields.Monetary(
        'Amount Paid',
        help="Mpesa online amount",
        currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        'Currrency',
        default=lambda self: self.env.ref('base.KES').id,
        help="Currency in use")
    merchant_request_id = fields.Char('Merchant Request ID')
    checkout_request_id = fields.Char('Checkout Request ID')
    phone_number = fields.Char('Phone Number',
                               help="The customer mpesa phone number")
    mpesa_receipt_number = fields.Char(
        'Mpesa Receipt Number',
        help="The reference number as assigned to the transaction by the mobile money provider")
    transaction_date = fields.Char('Transaction Date')
    result_code = fields.Char('Result Code')
    result_desc = fields.Text('Result Description')
    reconciled = fields.Boolean(
        'Reconciled',
        default=False,
        help="if checked, then this payment has been reconciled")
    order_id = fields.Many2one(
        'sale.order',
        'Related Sales Order',
        help="The sales order that was paid using this transaction,\
                this will appear once the payment has been validated")
    partner_id = fields.Many2one(
        'res.partner',
        'Customer',
        related='order_id.partner_id',
        store=True)
    acquirer_id = fields.Many2one(
        'payment.acquirer',
        'Payment Channel',
        help="The payment acquirer related to this payment as configured in Odoo")

    # _sql_constraints = {('unique_internal_transaction_id',
    #                    'unique(internal_transaction_id)',
    #                    'Another payment with same internal transaction ID exist!')}

    @api.depends('phone_number', 'mpesa_receipt_number')
    def name_get(self):
        res = []
        for rec in self:
            name = (rec.phone_number or '') + ' / ' + \
                (rec.mpesa_receipt_number or '')
            res.append((rec.id, name))
        return res

    @api.model
    def save_data(self, params):
        """
        Stores the payment data for mpesa online as received from safaricom
        via the json CallBackURL
        """
        if params:
            vals = dict(
                reconciled=False,
                result_code=params.get('ResultCode', False),
                result_desc=params.get('ResultDesc', False),
                merchant_request_id=params.get('MerchantRequestID', False),
                checkout_request_id=params.get('CheckoutRequestID', False),
                amount=[x.get('Value') for x in params['CallbackMetadata']
                        ['Item'] if x.get('Name') == 'Amount'].pop(),
                phone_number=[x.get('Value') for x in params['CallbackMetadata']
                              ['Item'] if x.get('Name') == 'PhoneNumber'].pop(),
                transaction_date=[x.get('Value') for x in params['CallbackMetadata']
                                  ['Item'] if x.get('Name') == 'TransactionDate'].pop(),
                mpesa_receipt_number=[x.get('Value') for x in params['CallbackMetadata']
                                      ['Item'] if x.get('Name') == 'MpesaReceiptNumber'].pop(),
            )
            return self.create(vals)
        msg = _(
            'MPESA_ONLINE: Callback metadata received was not saved.')
        LOGGER.warning(msg)
        return False
