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
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
"""
import logging

from odoo import _, http
from odoo.http import request

LOGGER = logging.getLogger(__name__)


class LipaNaMpesa(http.Controller):
    """ Mpesa online routes for callback url and for submitting payment form data """
    @http.route('/mpesa_express',
                type='json',
                auth='public',
                methods=['POST'],
                website=True)
    def index(self, **kw):
        """ Lina na MPESA Online Callback URL"""
        params = request.jsonrequest or {}
        if params:
            data = params['Body']['stkCallback']
            res_code = data.get('ResultCode')
        if res_code == 0:
            pay = request.env['mpesa.online'].sudo().save_data(data)
            if pay:
                LOGGER.info("MPESA_ONLINE: Result Code: %s, %s", res_code,
                            data.get('ResultDesc'))
                LOGGER.info(
                    _('MPESA_ONLINE: Data successfully stored in the system'))
        else:
            LOGGER.warning("MPESA_ONLINE: Result Code: %s, %s", res_code,
                           data.get('ResultDesc'))
