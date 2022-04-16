# -*- coding: utf-8 -*-
{
    'name': "pos_hide_refund",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_order_form.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_hide_refund/static/src/js/hide_refund.js',
        ],
        'web.assets_qweb': [
            ('remove', 'point_of_sale/static/src/xml/Screens/ProductScreen/ControlButtons/RefundButton.xml'),
            'pos_hide_refund/static/src/xml/RefundButton.xml',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
