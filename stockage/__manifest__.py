# -*- coding: utf-8 -*-
{
    'name': "Stock personnalisé",
    'summary': """
    Gestion des casses
    """,
    'description': """
    Gestion des casses
    """,
    'author': "Tano Martin",
    'sequence': -100,
    'category': 'Project Management',
    'version': '1.0.0',
    'depends': [
        'base',
        'stock',
    ],
    'auto_install': False,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'data/reference_cas.xml',
        'data/reference_exp.xml',
        'views/menu.xml',
        'views/casser_view.xml',
        'views/expirer_view.xml',

    ],
    'demo': [],
    'license': 'LGPL-3',
}
