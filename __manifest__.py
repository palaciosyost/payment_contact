{
    'name': 'Proceso de Pago - Contact',
    'version': '1.0',
    'description': 'proceso de rellenado de datos del cliente en la pasarela de pago',
    'summary': '',
    'author': 'FPC Technology',
    'website': 'https://fpc-technology.com',
    'license': 'LGPL-3',
    'category': 'eCommerce',
    'depends': [
        'base', "web", "website", 'payment'
    ],
    'data': [
        'view/form_company_view.xml',
        'view/payment_redirect_form.xml',
        'view/web/address_form_view.xml',
        'view/web/l10n_pe_website_sale_inherit.xml',
        "view/pagos_yape.xml",
        "data/payment_yape.xml",
        "data/payment_metodo.xml",
        "view/web/template_pago.xml",
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_frontend' : [
            'payment/static/src/js/payment_form.js',
            '/payment_contact/static/src/js/index.js',
            '/payment_contact/static/src/js/payment.js',
        ]
    }
}