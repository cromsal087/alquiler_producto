
{
 'name': 'Alquiler de productos',
 'version': '1.0',
 'author': 'Cloe Romero',
 'category': 'Custom',
 'summary': 'Gestión de alquileres de producto',
 'depends': ['base', 'sale_management'], #aqui siempre ponemos base y luego lo que tenga que ver con los permisos
 'data': [
 'security/ir.model.access.csv',
 'views/alquiler_producto_views.xml',
 ],
 'icon': '/alquiler_producto/static/description/rent.png', #siempre va con barra delante o peta
 'installable': True,
 'application': True,
}