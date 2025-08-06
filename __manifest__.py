{
    'name': 'Web Site Date',
    'version': '17.0',
    'category': 'Tools',
    'author':'Mauro Bogado,Exemax',
    'summary': 'Modulo para poder realizar la carga de un contacto desde el entorno de la web y replicarlo en el entorno de Odoo',
    'depends': ['base','sale','web', 'website'],
    'data': [
        #'security/ir.model.access.csv',
        'views/website_date.xml',
        
        
    ],
    'assets': {
    'web.assets_frontend': [
        'exe_website_date/views/website_date.xml',
    ],
    },

    'installable': True,
    'application': False,
}   