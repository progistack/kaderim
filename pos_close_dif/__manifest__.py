# -*- coding: utf-8 -*-
{
    'name': "pos_close_dif",

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
    ],
    'assets': {
        'web.assets_qweb': [
            ('remove', 'point_of_sale/static/src/xml/Popups/ClosePosPopup.xml'),
            'pos_close_dif/static/src/xml/Popups/ClosePosPopup.xml',
        ],
    },
}
