# models/alquiler_producto.py
from odoo import models, fields, api
from datetime import timedelta, date

class AlquilerProducto(models.Model):
    _name = 'alquiler.producto'
    _description = 'Gestión de alquiler de productos'

    prestamo_id = fields.Integer(string='Identificador de prestamo', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('alquiler.producto.sequence'))
    customer_id = fields.Many2one('res.partner', string='Cliente', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    initial_date = fields.Date(string='Fecha de inicio', required=True, default=fields.Date.today)
    final_date = fields.Date(string='Fecha de vencimiento', compute='_compute_final_date', store=True)
    status = fields.Selection([
        ('alquilado', 'En alquiler'),
        ('entregado', 'Entregado'),
        ('noentregado', 'No entregado')
    ], string='Estado', default='alquilado', tracking=True)
    comments = fields.Text(string='Observaciones')

    @api.onchange('product_id')
    def _check_product_availability(self):
        for record in self:
            if record.product_id:
                # Verificar si el producto está en otros alquileres activos
                active_rentals = self.env['alquiler.producto'].search([
                    ('product_id', '=', record.product_id.id),
                    ('status', '=', 'alquilado'),
                    ('id', '!=', record._origin.id)
                ])
                if active_rentals:
                    record.product_id = False
                    return {
                        'warning': {
                            'title': 'Producto no disponible',
                            'message': 'Este producto ya está en alquiler.'
                        }
                    }

    @api.depends('initial_date')
    def _compute_final_date(self):
        for record in self:
            if record.initial_date:
                record.final_date = record.initial_date + timedelta(days=30)

    @api.model
    def _cron_check_overdue_rentals(self):
        today = fields.Date.today()
        overdue_rentals = self.search([
            ('status', '=', 'alquilado'),
            ('final_date', '<', today)
        ])
        overdue_rentals.write({'status': 'noentregado'})

# __manifest__.py
{
    'name': 'Alquiler de productos',
    'version': '1.0',
    'author': 'Cloe Romero',
    'category': 'Sales',
    'summary': 'Gestión de alquileres de producto',
    'depends': ['base', 'sale_management', 'product'],
    'data': [
        'security/rental_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'views/alquiler_producto_views.xml',
    ],
    'icon': '/alquiler_producto/static/description/rent.png',
    'installable': True,
    'application': True,
}

# security/rental_security.xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="rental_group_user" model="res.groups">
        <field name="name">Rental / User</field>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <record id="rental_group_manager" model="res.groups">
        <field name="name">Rental / Manager</field>
        <field name="implied_ids" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
    </record>
</odoo>

# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_alquiler_producto_user,alquiler.producto.user,model_alquiler_producto,base.group_user,1,0,0,0
access_alquiler_producto_sale,alquiler.producto.sale,model_alquiler_producto,sales_team.group_sale_salesman,1,1,1,1

# data/ir_cron_data.xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="ir_cron_check_overdue_rentals" model="ir.cron">
        <field name="name">Check Overdue Rentals</field>
        <field name="model_id" ref="model_alquiler_producto"/>
        <field name="state">code</field>
        <field name="code">model._cron_check_overdue_rentals()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="numbercall">-1</field>
        <field name="doall" eval="False"/>
        <field name="active" eval="True"/>
    </record>
</odoo>

# data/ir_sequence_data.xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="seq_alquiler_producto" model="ir.sequence">
        <field name="name">Alquiler Producto Sequence</field>
        <field name="code">alquiler.producto.sequence</field>
        <field name="prefix">ALP/%(year)s/</field>
        <field name="padding">5</field>
        <field name="company_id" eval="False"/>
    </record>
</odoo>

# views/alquiler_producto_views.xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_alquiler_producto_form" model="ir.ui.view">
        <field name="name">alquiler.producto.form</field>
        <field name="model">alquiler.producto</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <field name="status" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <field name="prestamo_id"/>
                        <field name="customer_id"/>
                        <field name="product_id"/>
                        <field name="initial_date"/>
                        <field name="final_date"/>
                        <field name="comments"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="view_alquiler_producto_tree" model="ir.ui.view">
        <field name="name">alquiler.producto.tree</field>
        <field name="model">alquiler.producto</field>
        <field name="arch" type="xml">
            <tree>
                <field name="prestamo_id"/>
                <field name="customer_id"/>
                <field name="product_id"/>
                <field name="initial_date"/>
                <field name="final_date"/>
                <field name="status"/>
            </tree>
        </field>
    </record>

    <record id="action_alquiler_producto" model="ir.actions.act_window">
        <field name="name">Alquileres</field>
        <field name="res_model">alquiler.producto</field>
        <field name="view_mode">tree,form</field>
    </record>

    <menuitem id="menu_alquiler_producto_root" 
              name="Alquileres"
              sequence="10"/>

    <menuitem id="menu_alquiler_producto" 
              parent="menu_alquiler_producto_root"
              action="action_alquiler_producto"
              sequence="1"/>
</odoo>
