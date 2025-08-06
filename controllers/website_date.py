from odoo import http
from odoo.http import request

class WebsiteNewClientForm(http.Controller):
    @http.route(['/nuevo_cliente'], type='http', auth="public", website=True)
    def nuevo_cliente_form(self, **kw):
        return request.render('exe_website_date.template_nuevo_cliente_form')

    @http.route(['/nuevo_cliente/enviar'], type='http', auth="public", website=True, csrf=False)
    def nuevo_cliente_enviar(self, **post):
        # Armamos notas con campos combinados
        # comment = f"""
        # Nombre del local: {post.get('local_name')}
        # Transporte preferido: {post.get('transporte')}
        # ¿Trabaja con mercadería?: {post.get('trabaja_mercaderia')}
        # Origen o proveedor: {post.get('origen_producto')}
        # """
        comment = (
            f"Nombre del local: {post.get('local_name')}\n"
            f"Transporte preferido: {post.get('transporte')}\n"
            f"¿Trabaja con mercadería?: {post.get('trabaja_mercaderia')}\n"
            f"Origen o proveedor: {post.get('origen_producto')}"
        )


        # Creamos el contacto principal
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

        # Dirección de entrega como contacto secundario
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