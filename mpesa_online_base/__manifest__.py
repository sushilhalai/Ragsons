# -*- coding: utf-8 -*-
{
    'name': "Base module for MPESA EXPRESS",
    'support': 'support@optima.co.ke',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 109,
    'summary': """
        Base module for M-PESA Express in Odoo POS (Point Of Sale) or E-commerce""",
    'description': """
Base Module for M-PESA EXPRESS/Lipa Na Mpesa Online
====================================================
* This module forms the basis for all our MPESA Express/Online payment Apps.

* Once you purchase it, you are no longer required to purchase it again for any subsequent MPESA Express Apps that you purchase from us.

* It is the basis for any MPESA Express payment App for Point of sale (POS) or E-commerce
""",
    'author': "Optima ICT Services LTD",
    'website': "http://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing & Payments',
    'version': '14.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/mpesa_online_base_views.xml',
    ],
    'images': ['static/description/mpesa_base.png'],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
