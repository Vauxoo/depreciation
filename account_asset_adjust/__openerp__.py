# -*- coding: utf-8 -*-
{
    'name': "Asset Adjustment Module",

    'summary': """Tool for Inflation Adjustments in Assets""",

    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",

    # Categories can be used to filter modules
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_asset'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'view/account_asset_adjust.xml',
        # 'templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/openacademy_course_demo.xml',
    # ],
    'installable': True,
    'auto-install': False,
}
