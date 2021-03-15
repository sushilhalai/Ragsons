# -*- coding: utf-8 -*-
{
    'name':
    "Safaricom M-PESA Express (Lipa Na M-PESA Online)",
    'license':
    'OPL-1',
    'support':
    "support@optima.co.ke",
    'summary':
    """
        Accept M-PESA Payments on your e-commerce site using Safaricom Lipa na MPESA Online""",
    'description':
    """
        Accept M-PESA Payments on your e-commerce site using Safaricom Lipa na MPESA Online
    """,
    'author':
    "Optima ICT Services LTD",
    'website':
    "https://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category':
    'Website',
    'version':
    '14.0.0.1.0',
    'price':
    240,
    'currency':
    'EUR',
    'images': ['static/src/img/mpesa_icon.png'],

    # any module necessary for this one to work correctly
    'depends': ['mpesa_online_base', 'sale', 'payment'],

    # always loaded
    'data': [
        'views/mpesa_online_views.xml',
        'views/templates.xml',
        'data/mpesa_acquirer_data.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
