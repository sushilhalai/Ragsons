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
# © 2021 Bernard K Too<bernard.too@optima.co.ke>
"""
import base64
import logging
from datetime import timedelta

import requests
from requests.auth import HTTPBasicAuth

from odoo import _, fields, models

LOGGER = logging.getLogger(__name__)


class MpesaOnlineAcquirer(models.Model):
    """ inherited to add mpesa features """

    _inherit = "payment.acquirer"

    provider = fields.Selection(
        selection_add=[("mpesa_online", "Lipa Na Mpesa Online")],
        ondelete={"mpesa_online": "set default"},
    )
    mpesa_online_transaction_type = fields.Selection(
        [
            ("CustomerPayBillOnline", "PayBill"),
            ("CustomerBuyGoodsOnline", "Buy Goods and Services"),
        ],
        string="Lipa na M-PESA",
        required_if_provider="mpesa_online",
        default="CustomerPayBillOnline",
    )
    mpesa_online_currency_id = fields.Many2one(
        "res.currency",
        "M-PESA Currency",
        required_if_provider="mpesa_online",
        default=lambda self: self.env.ref("base.KES").id,
        help="The M-PESA currency. Default is KES. \n If the sales order is in a different currency other than the M-PESA currency, \nit has to be converted to the M-PESA currency",
    )
    mpesa_online_store_number = fields.Char(string="Store Number", default="174379")
    mpesa_online_service_number = fields.Char(
        "Service Number",
        required_if_provider="mpesa_online",
        help="Enter the mobile money service number or shortcode e.g the Till number\
                or Pay bill number if MPESA, this will appear in E-commerce \
                website for your customers to use",
    )
    mpesa_online_service_name = fields.Char(
        "Service Name",
        required_if_provider="mpesa_online",
        help="Enter the mobile money service name,e.g  MPESA if safaricom.\
                This will appear in E-commerce website ",
    )
    mpesa_online_dp = fields.Integer(
        "Decimal Precision",
        default=0,
        help="This is the decimal precision to be used when \
                checking if customer paid exact,higher or less than the order amount. \
                Default is zero meaning the paid amount and order amount are rounded up to\
                the nearest 'ones' by default..i.e no checking of decimals (cents) in comparing the paid \
                amount vs the sales order amount",
    )

    mpesa_online_passkey = fields.Char(
        "Lipa Na MPESA Online Passkey",
        required_if_provider="mpesa_online",
        default="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
    )
    mpesa_online_resource_url = fields.Char(
        "Resource URL",
        required_if_provider="mpesa_online",
        default="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
    )
    mpesa_online_access_token_url = fields.Char(
        "Access Token URL",
        required_if_provider="mpesa_online",
        default="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
    )
    mpesa_online_callback_url = fields.Char(
        "Callback URL",
        required_if_provider="mpesa_online",
        default=lambda self: self.env["ir.config_parameter"].get_param(
            "web.base.url", ""
        )
        + "/mpesa_express",
    )
    mpesa_online_consumer_key = fields.Char(
        "Consumer Key", required_if_provider="mpesa_online"
    )
    mpesa_online_consumer_secret = fields.Char(
        "Consumer Secret", required_if_provider="mpesa_online"
    )
    mpesa_online_access_token = fields.Char("M-PESA Access Token", readonly=True)
    mpesa_online_token_expiry_date = fields.Datetime(
        "Token Expiry Date",
        default=lambda self: fields.Datetime.now(),
        readonly=True,
        help="This date and time will automatically be updated \n\
                every time the system gets a new token from mpesa API",
    )

    def _mpesa_online_get_access_token(self):
        self.ensure_one()
        payload = None
        if (
            not self.mpesa_online_access_token
            or fields.Datetime.now() >= self.mpesa_online_token_expiry_date
        ):
            try:
                res = requests.get(
                    self.mpesa_online_access_token_url,
                    auth=HTTPBasicAuth(
                        self.mpesa_online_consumer_key,
                        self.mpesa_online_consumer_secret,
                    ),
                )
            except requests.exceptions.RequestException as exc:
                LOGGER.warning("MPESA_ONLINE: %s", exc)
            else:
                if res.status_code == 200:
                    payload = res.json()
                    LOGGER.info(
                        "MPESA_ONLINE: Response Code: %s, Access Token received.",
                        res.status_code,
                    )
                else:
                    msg = _("Cannot fetch access token. Received HTTP Error code ")
                    LOGGER.warning(
                        "MPESA_ONLINE: "
                        + msg
                        + str(res.status_code)
                        + ", "
                        + res.reason
                        + ". URL: "
                        + res.url
                    )
            if payload:
                self.write(
                    dict(
                        mpesa_online_access_token=payload.get("access_token"),
                        mpesa_online_token_expiry_date=fields.Datetime.to_string(
                            fields.Datetime.now()
                            + timedelta(seconds=int(payload.get("expires_in")))
                        ),
                    )
                )
        return self.mpesa_online_access_token

    def mpesa_stk_push(self, data):
        """
        method to be called from  payment transaction model when form data is received.
        """
        self.ensure_one()
        return self._mpesa_online_stk_push(data)

    def _mpesa_online_stk_push(self, data):
        self.ensure_one()
        if self.mpesa_online_resource_url:
            amount = data.get("amount")
            if (
                int(data.get("currency")) != self.mpesa_online_currency_id.id
            ):  # multi-currency support
                amount = (
                    self.env["res.currency"]
                    .browse([int(data.get("currency"))])
                    ._convert(
                        from_amount=float(amount),
                        company=self.company_id,
                        to_currency=self.mpesa_online_currency_id,
                        date=fields.Date.today(),
                    )
                )
            timestamp = fields.Datetime.context_timestamp(
                self, timestamp=fields.Datetime.now()
            ).strftime("%Y%m%d%H%M%S")
            string = (
                (self.mpesa_online_store_number or self.mpesa_online_service_number)
                + self.mpesa_online_passkey
                + timestamp
            )
            body = {
                "BusinessShortCode": self.mpesa_online_store_number
                or self.mpesa_online_service_number,
                "Password": base64.b64encode(bytes(string, "latin-1")).decode("utf-8"),
                "Timestamp": timestamp,
                "TransactionType": self.mpesa_online_transaction_type,
                # convert to integer to avoid 'invalid amount error'
                "Amount": int(float(amount)),
                "PartyA": data.get("mpesa_phone_number"),
                "PartyB": self.mpesa_online_service_number,
                "PhoneNumber": data.get("mpesa_phone_number"),
                "CallBackURL": data.get("callback_url"),
                "AccountReference": data.get("reference"),
                "TransactionDesc": data.get("reference"),
            }
            LOGGER.info("MPESA_ONLINE: Payload = %s", body)
            try:
                res = requests.post(
                    self.mpesa_online_resource_url,
                    json=body,
                    headers={
                        "Authorization": "Bearer %s"
                        % self._mpesa_online_get_access_token()
                    },
                )
            except requests.exceptions.RequestException as exc:
                LOGGER.warning("MPESA_ONLINE: %s", exc)
                return False
            else:
                if res.status_code == 200:
                    jsn = res.json()
                    LOGGER.info(
                        "MPESA_ONLINE: Response Code: %s, %s. <Mpesa phone: %s> \
                                <amount requested: %s %s> <Order ref: %s>",
                        jsn.get("ResponseCode", ""),
                        jsn.get("ResponseDescription", ""),
                        data.get("mpesa_phone_number"),
                        amount,
                        self.mpesa_online_currency_id.name,
                        data.get("reference"),
                    )
                    tx_id = data.get("tx_id", False)
                    if not tx_id:
                        return False
                    txn = self.env["payment.transaction"].browse([int(tx_id)])
                    if not txn:
                        return False
                    vals = dict(
                        mpesa_online_merchant_request_id=jsn.get(
                            "MerchantRequestID", False
                        ),
                        mpesa_online_checkout_request_id=jsn.get(
                            "CheckoutRequestID", False
                        ),
                        date=fields.Datetime.now(),
                    )
                    return txn.write(vals)
                else:
                    msg = _(
                        "Cannot push request for payment. Received HTTP Error code "
                    )
                    LOGGER.warning(
                        "MPESA_ONLINE: "
                        + msg
                        + str(res.status_code)
                        + ", "
                        + res.reason
                        + ". URL: "
                        + res.url
                    )
                    try:
                        message = res.json()
                    except BaseException:
                        pass
                    else:
                        code = message.get("errorCode") or message.get(
                            "responseCode", None
                        )
                        desc = message.get("errorMessage") or message.get(
                            "responseDesc", None
                        )
                        if code and desc:
                            LOGGER.warning(
                                "MPESA_ONLINE: Error code " + code + ": " + desc
                            )

        return False

    def mpesa_online_get_form_action_url(self):
        return "/payment/mpesa_online"

    def mpesa_online_form_generate_values(self, values):
        """  additional values for the  mpesa express """
        if not values:
            values = {}
        if self.mpesa_online_callback_url:
            values.update(callback_url=self.mpesa_online_callback_url)
        # MPESA does not support decimal places in amount.
        # if values.get('amount'):
        #    values.update(amount=round(values.get('amount')))
        return values

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical name in the corresponding
        key for the following features:
        * fees: support payment fees computations
        * authorize: support authorizing payment (separates
        authorization and capture)
        * tokenize: support saving payment data in a payment.tokenize
        object
        """
        res = super(MpesaOnlineAcquirer, self)._get_feature_support()
        res["fees"].append("mpesa_online")
        return res
