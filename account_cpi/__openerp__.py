# -*- coding: utf-8 -*-
{
    'name': "Consumer Price Index",

    'summary': """Fiscal Period Dependant Value Factor""",

    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",

    # Categories can be used to filter modules
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'view/account_price_index_view.xml',
        # 'templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/openacademy_course_demo.xml',
    # ],
    'installable': True,
    'auto-install': False,
}
