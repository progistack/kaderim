# -*- coding: utf-8 -*-

{
    'name': "POS Dashboard",
    'version': '15.0.1.0.0',
    'summary': """POS Dashboard""",
    'description': """POS Dashboard""",
    'category': 'Point of Sale',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['hr', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/history_dashboard_view.xml',
        'report/report.xml'
    ],
     'assets': {
        'web.assets_backend': [
            'dashboard_pos/static/src/js/pos_dashboard.js',
            'dashboard_pos/static/src/css/pos_dashboard.css',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.js',
        ],
        'web.assets_qweb': [
            'dashboard_pos/static/src/xml/pos_dashboard.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'application': False,
}