
{
 'name': 'Alquiler de productos',
 'version': '1.0',
 'author': 'Cloe Romero',
 'category': 'Custom',
 'summary': 'Gestión de alquileres de producto',
 'depends': ['base', 'sale_management'],
 'data': [
 'security/ir.model.access.csv',
 'views/alquiler_producto_views.xml',
 ],
 'icon': '/alquiler_producto/static/description/rent.png',
 'installable': True,
 'application': True,
}