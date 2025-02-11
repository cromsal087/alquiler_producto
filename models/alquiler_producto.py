from odoo import models, fields, api 
from datetime import timedelta

class AlquilerProducto(models.Model):

    _name = 'alquiler.producto'
    _description = 'Gestion de alquiler de productos'

    customer_id = fields.Many2one('res.partner', string='Cliente', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    initial_date = fields.Date(string='Fecha de inicio', required=True)
    final_date = fields.Date(string='Fecha de vencimiento',compute='_compute_final_date', store=True, required=True) #store=True: Indica si el valor calculado se guarda en la base de datos (True) o se calcula cada vez que se necesita (False).
    status = fields.Selection(
    [('Alquilado', 'En alquiler'),    # 'alquilado' es el valor técnico, 'En alquiler' es lo que ve el usuario
    ('Entregado', 'Entregado'),
    ('No entregado','No entregado')], string='Estado', default = 'alquilado',tracking = True) 
    comments = fields.Text(string= 'Observaciones')

    @api.onchange("product_id")
    def _productcheck(self):
        if self.product_id:
            # Busca si el producto está en otros alquileres activos
            alquileres = self.env['alquiler.producto'].search([
                ('product_id', '=', self.product_id.id),
                ('status', '=', 'alquilado')
            ])
            # Si encuentra alquileres activos, limpia el campo y muestra advertencia
            if alquileres:
                self.product_id = False
                return {'warning': {'title': 'Error', 'message': 'Producto no disponible'}}

    @api.depends('initial_date') # Se ejecuta cuando cambia la fecha inicial
    def _compute_final_date(self):
        for record in self:
            if record.initial_date:
                record.final_date = record.initial_date + timedelta(days=30)

    @api.model
    def _check_overdue(self):
        today = fields.Date.today() # Obtiene la fecha actual
        # Busca alquileres vencidos
        alquileres = self.search([
            ('status', '=', 'alquilado'),
            ('final_date', '<', today)
        ])
        # Cambia su estado a 'no entregado'
        alquileres.write({'status': 'No entregado'})
