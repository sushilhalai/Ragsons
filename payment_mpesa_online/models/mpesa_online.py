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

from odoo import api, models

LOGGER = logging.getLogger(__name__)


class PaymentMpesaOnline(models.Model):
    """
    model and methods  for handling and storing mpesa
    online data received through the json CallBackURL
    """
    _inherit = 'mpesa.online'
    # _sql_constraints = {('unique_internal_transaction_id',
    #                    'unique(internal_transaction_id)',
    #                    'Another payment with same internal transaction ID exist!')}

    @api.model
    def save_data(self, params):
        """
        Stores the payment data for mpesa online as received from safaricom
        via the json CallBackURL
        """
        res = super(PaymentMpesaOnline, self).save_data(params)
        if res:
            txn = self.env['payment.transaction'].search(
                [('is_processed', '=', False),
                 ('state', 'not in', ['done', 'cancel']),
                 ('acquirer_id.provider', '=', 'mpesa_online'),
                 ('mpesa_online_merchant_request_id', '=',
                  res.merchant_request_id),
                 ('mpesa_online_checkout_request_id', '=',
                  res.checkout_request_id)],
                limit=1)
            if txn:
                vals = txn.mpesa_online_message_validate(pay=res, vals={})
                txn.write(vals)
        return res
