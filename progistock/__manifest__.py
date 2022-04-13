# -*- coding: utf-8 -*-
{
    'name': "alerte stock",

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
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mail'],

    # always loaded
    'data': [
         #'security/ir.model.access.csv',
        #'views/product_lot_views.xml',
        'views/auto_action_views.xml',
        'views/email_log_views.xml',
        'data/product_lot_exp_action.xml',
        'data/product_lot_qty_action.xml',
        'views/product_cat_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
