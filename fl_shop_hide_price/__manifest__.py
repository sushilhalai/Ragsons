# -*- coding: utf-8 -*-
{
    'name': 'Hide Price in Shop',
    'version': '14.0.1.0.0',
    'category': 'Website',
    'summary': 'Hide Product Price from Public Users or Not Logged In User, Website Sale Hide Price, Hide Price in Shop, Shop Hide Price, Product Hide Price, Hide Price Multiwebsite',
    'description': """
        This module allows to hide prices and add to cart button in shop page for not logged in users,
        It also replaces Add to Cart button with Log in to Check Price,
        Hide Product Price and Add to Cart button in the shop page,
        Hide Product Price, Select Quantity and Replace Add to Cart button in product details page,
        Without login user can't see product price,
        Price details are shown only to the logged in users,
        Product price will be visible after the user is logged in,
        Support for the multi-website platform.
    """,
    'sequence': 1,
    'author': 'Futurelens',
    'website': 'http://thefuturelens.com',
    'depends': ['website_sale'],
    'data': [
        'views/templates.xml'
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/banner_shop_price_hide.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'price': 5,
    'currency': 'EUR',
}
