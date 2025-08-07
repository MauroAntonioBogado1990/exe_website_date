from odoo import http
from odoo.http import request

class WebsiteNewClientForm(http.Controller):

    @http.route(['/nuevo_cliente'], type='http', auth="public", website=True)
    def nuevo_cliente_form(self, **kw):
        # Buscar país Argentina
        argentina = request.env['res.country'].sudo().search([('code', '=', 'AR')], limit=1)

        # Provincias de Argentina
        states = request.env['res.country.state'].sudo().search([('country_id', '=', argentina.id)])

        # Responsabilidad ante AFIP
        afip_responsabilities = request.env['l10n_ar.afip.responsibility.type'].sudo().search([])

        return request.render('exe_website_date.template_nuevo_cliente_form', {
            'states': states,
            'afip_responsabilities': afip_responsabilities
        })

    @http.route(['/nuevo_cliente/enviar'], type='http', auth="public", website=True, csrf=False)
    def nuevo_cliente_enviar(self, **post):
        comment = f"""
        Nombre del local: {post.get('local_name')}
        Transporte preferido: {post.get('transporte')}
        ¿Trabaja con nuestra mercadería?: {post.get('trabaja_mercaderia')}
        
        """
        if post.get('trabaja_mercaderia') == 'Sí':
            comment += f"A quién le compra o compraba repuestos: {post.get('origen_producto_si')}\n"
        elif post.get('trabaja_mercaderia') == 'No':
            comment += f"¿Cómo conoció los productos?: {post.get('origen_producto_no')}\n"


        partner = request.env['res.partner'].sudo().create({
            'name': post.get('name'),
            'city': post.get('city'),
            'state_id': int(post.get('state_id')) if post.get('state_id') else False,
            'street': post.get('street'),
            'zip': post.get('zip'),
            'mobile': post.get('mobile'),
            'phone': post.get('phone'),
            'email': post.get('email'),
            'comment': comment,
            'vat': post.get('vat'),
            'l10n_ar_afip_responsibility_type_id': int(post.get('afip_id')) if post.get('afip_id') else False,
        })

        if post.get('entrega_street'):
            request.env['res.partner'].sudo().create({
                'name': post.get('name') + ' (Entrega)',
                'parent_id': partner.id,
                'type': 'delivery',
                'street': post.get('entrega_street'),
                'zip': post.get('entrega_zip'),
                'city': post.get('entrega_city'),
                'state_id': int(post.get('entrega_state_id')) if post.get('entrega_state_id') else False,
            })

        return request.render('exe_website_date.template_nuevo_cliente_gracias')