# -*- coding: utf-8 -*-
{
    'name': "stock_scheduler",
    'version': "0.0.1",
    'summary': """
            Stock alert scheduler
    """,
    'author' : "Sedrick KOUAGNI",
    'company': 'PROGISTACK',
    'maintainer': 'kanangamansedrickgael@gmail.com',
    'description': """
        Stock alert scheduler
    """,
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Inventory',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_scheduler.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': False,
}
