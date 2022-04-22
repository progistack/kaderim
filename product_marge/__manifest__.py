# -*- coding: utf-8 -*-
{
    'name': "Product Marge",
    'summary': """Gestion des informations de marge.""",
    'description': """Gestion des informations de marge sur les ventes.""",
    'author': "Progistack",
    'website': "http://www.yourcompany.com",
    'sequence': -90,
    'category': 'Project Management',
    'version': '1.0.0',
    'depends': [
        'base',
        'point_of_sale',
    ],
    'auto_install': False,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'wizard/marge_detail_view.xml',
        'views/views.xml',
        'views/report.xml',
        'views/detail_marge_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
