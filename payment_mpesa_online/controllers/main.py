# -*- coding: utf-8 -*-
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
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
import logging

from odoo import _, http
from odoo.http import request

LOGGER = logging.getLogger(__name__)


class LipaNaMpesa(http.Controller):
    """ Mpesa online routes for callback url and for
    submitting payment form data
    """
    @http.route('/payment/mpesa_online',
                type='http',
                auth='public',
                methods=['POST'],
                website=True,
                csrf=False)
    def lipa_na_mpesa(self, **post):
        """ To handle HTTP Post from the lipa na mpesa form """

        user = post.get('mpesa_phone_number')
        msg = _(
            'MPESA_ONLINE: Receiving payment form data for transaction ref')
        msg += '<%s>' % post.get('reference', '')
        msg += ' for <%s>' % user
        LOGGER.info(msg)
        if not http.request.session.get(
                'sale_order_id') and http.request.session.get(
                    'sale_last_order_id'):
            http.request.session.update(
                sale_order_id=http.request.session.get('sale_last_order_id'))
        tx_id = request.session.get('__website_sale_last_tx_id', False)
        if tx_id: # for portal, this will not be updated. will get tx from data
            post.update(tx_id=tx_id)

        if http.request.env['payment.transaction'].sudo().form_feedback(
                post, 'mpesa_online'):
            msg = _(
                'MPESA_ONLINE: Completed sending payment request to customer')
            msg += ' <%s>' % user
            LOGGER.info(msg)
            msg = _('MPESA_ONLINE: redirecting back to Odoo payment process.')
            LOGGER.info(msg)
            return http.request.redirect(post.pop('return_url'))
        return http.request.redirect('/shop/payment')
