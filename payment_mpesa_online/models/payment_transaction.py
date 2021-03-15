# -*- coding: utf-8 -*-
"""
# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).
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
# © 2019 Bernard K Too<bernard.too@optima.co.ke>
"""
import logging

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare

LOGGER = logging.getLogger(__name__)


class MpesaOnlineTransaction(models.Model):
    """ inherited to add MPESA ONLINE fields"""

    _inherit = "payment.transaction"

    mpesa_online_receipt_number = fields.Char(
        "MPESA Receipt Number",
        related="mpesa_online_id.mpesa_receipt_number",
        readonly=True,
        help="MPESA transaction reference/receipt number",
    )
    mpesa_online_merchant_request_id = fields.Char(
        "MPESA Merchant Request ID",
        readonly=True,
        help="MPESA transaction reference/receipt number",
    )
    mpesa_online_checkout_request_id = fields.Char(
        "MPESA Checkout Request ID", readonly=True, help="MPESA Checkout Request ID"
    )
    mpesa_online_id = fields.Many2one(
        "mpesa.online",
        "Mpesa transaction",
        readonly=True,
        help="Related payment details for the transaction",
    )
    mpesa_online_amount = fields.Monetary(
        related="mpesa_online_id.amount",
        currency_field="mpesa_online_currency_id",
        string="Amount Paid",
        help="Amount paid by customer. \n\
                The currency may differ from that of the sales order itself",
    )
    mpesa_online_currency_id = fields.Many2one(
        related="acquirer_id.mpesa_online_currency_id", string="Currency(Mpesa)"
    )
    provider = fields.Selection(
        string="Provider", related="acquirer_id.provider", readonly=True
    )

    @api.model
    def _mpesa_online_form_get_tx_from_data(self, data):
        reference, currency, acquirer = (
            data.get("reference"),
            data.get("currency"),
            data.get("acquirer"),
        )
        txn = self.search(
            [
                ("reference", "=", reference),
                ("acquirer_id", "=", int(acquirer)),
                ("currency_id", "=", int(currency)),
            ]
        )
        if not txn or len(txn) > 1:
            error_msg = "MPESA_ONLINE: Received data for Order reference %s" % reference
            if not txn:
                error_msg += "; but no transaction found"
            else:
                error_msg += "; but multiple transactions found"
            LOGGER.error(error_msg)
        return txn

    def _mpesa_online_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # compare amount paid vs amount of the order
        if float_compare(float(data.get("amount")), (self.amount + self.fees), 2) != 0:
            invalid_parameters.append(
                ("amount", data.get("amount"), "%.2f" % self.amount)
            )

            # compare currency
        if int(data.get("currency")) != self.currency_id.id:
            invalid_parameters.append(
                ("currency", data.get("currency"), self.currency_id.id)
            )

            # compare acquirer
        if int(data.get("acquirer")) != self.acquirer_id.id:
            invalid_parameters.append(
                ("acquirer", data.get("acquirer"), self.acquirer_id.id)
            )

            # compare order reference
        if str(data.get("reference")) != self.reference:
            invalid_parameters.append(
                ("reference", data.get("reference"), self.reference)
            )

        return invalid_parameters

    def mpesa_online_message_validate(self, pay=None, vals=None):
        """
        Called when the mpesa online callback url receives data from safaricom mpesa API.
        Validates payment and return dict of values to be used to update the payment transaction.
        """
        if pay:
            pay.write(
                {
                    "reconciled": True,
                    "acquirer_id": self.acquirer_id.id,
                    "currency_id": self.acquirer_id.mpesa_online_currency_id.id,
                }
            )
            vals["date"] = fields.Datetime.now()
            vals["mpesa_online_id"] = pay.id
            vals["acquirer_reference"] = pay.display_name
            msg = _("MPESA_ONLINE: Customer paid")
            msg += " %s %s" % (pay.amount, self.mpesa_online_currency_id.name)
            msg += _(" against an order amounting to")
            msg += " %s %s" % (self.amount, self.currency_id.name)
            LOGGER.info(msg)
            amount_to_pay = self.amount
            # multi-currency support
            if self.acquirer_id.mpesa_online_currency_id.id != self.currency_id.id:
                amount_to_pay = self.currency_id._convert(
                    from_amount=self.amount,
                    company=self.partner_id.company_id,
                    to_currency=self.acquirer_id.mpesa_online_currency_id,
                    date=fields.Date.today(),
                )
            res = float_compare(
                pay.amount, amount_to_pay, self.acquirer_id.mpesa_online_dp
            )
            if res == 0:
                msg = _(
                    "MPESA_ONLINE: Payment successfully confirmed.Customer paid precise amount"
                )
                vals["state"] = "done"
                vals["state_message"] = msg
                LOGGER.info(msg)
            elif res == 1:
                delta = pay.amount - amount_to_pay
                msg = _(
                    "MPESA_ONLINE: Payment successfully confirmed.Customer paid more than the order amount by"
                )
                msg += " %s %s" % (
                    pay.currency_id.symbol or "",
                    "{:,.2f}".format(delta),
                )
                vals["state_message"] = msg
                vals["state"] = "done"
                LOGGER.info(msg)
            else:
                delta = amount_to_pay - pay.amount
                msg = _(
                    "MPESA_ONLINE: Payment validated but order not confirmed.Customer paid less than the order amount by"
                )
                msg += " %s %s" % (
                    pay.currency_id.symbol or "",
                    "{:,.2f}".format(delta),
                )
                vals["state"] = "pending"
                vals["state_message"] = msg
                LOGGER.info(msg)
        return vals

    def _mpesa_online_form_validate(self, data):
        # there will be not tx_id in data for portal case. Hence we need to
        # check and update before proceeding
        if not (data.get("tx_id", False)):
            data.update(tx_id=self.id)
        acq = self.env["payment.acquirer"].browse([int(data.get("acquirer"))])
        if not acq:
            return False
        return acq.mpesa_stk_push(data)
