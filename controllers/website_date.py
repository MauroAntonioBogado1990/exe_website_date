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
        Horario de entrega: {post.get('horario_transporte')}
        ¿Trabaja con nuestra mercadería?: {post.get('trabaja_mercaderia')}
        """

        if post.get('trabaja_mercaderia') == 'Sí':
            comment += f"A quién le compra o compraba repuestos: {post.get('origen_producto_si')}\n"
        elif post.get('trabaja_mercaderia') == 'No':
            comment += f"¿Cómo conoció los productos?: {post.get('origen_producto_no')}\n"
        
        #agregado de pais
        countries = request.env['res.country'].sudo().search([], order='name ASC')

        #  Validación del CUIT
        cuit = post.get('vat', '').strip()
        #if not cuit.isdigit() or len(cuit) != 11:
        if len(cuit) != 11:    
            argentina = request.env['res.country'].sudo().search([('code', '=', 'AR')], limit=1)
            states = request.env['res.country.state'].sudo().search([('country_id', '=', argentina.id)])
            afip_responsabilities = request.env['l10n_ar.afip.responsibility.type'].sudo().search([])

            return request.render('exe_website_date.template_nuevo_cliente_form', {
                'error': "El CUIT debe tener exactamente 11 dígitos numéricos sin guiones.",
                'states': states,
                'afip_responsabilities': afip_responsabilities,
                'form_data': post
            })
        pricelist = request.env['product.pricelist'].sudo().search([('name', '=', 'Navidad')], limit=1)
        if not pricelist:
            raise ValueError("No se encontró la lista de precios 'Navidad'")
        


        # ✅ Si el CUIT es válido, se crea el partner
        partner = request.env['res.partner'].sudo().create({
            'name': post.get('name'),
            'city': post.get('city'),
            'state_id': int(post.get('state_id')) if post.get('state_id') else False,
            #'country_id': int(post.get('country_id')) if post.get('country_id') else argentina.id,
            'country_id': 10,
            'street': post.get('street'),
            'zip': post.get('zip'),
            'mobile': post.get('mobile'),
            'phone': post.get('phone'),
            'email': post.get('email'),
            'comment': comment,
            'vat': cuit,
            'l10n_ar_afip_responsibility_type_id': int(post.get('afip_id')) if post.get('afip_id') else False,
            'l10n_latam_identification_type_id': request.env['l10n_latam.identification.type'].sudo().search([('name', '=', 'CUIT')], limit=1).id,
            'property_product_pricelist': pricelist.id,
            'user_id': 8,
            'company_type': 'company',

        })
        partner.sudo().write({'property_product_pricelist': 2})
        # Cambia a contacto individual
        partner.sudo().write({'company_type': 'person'})
        
        
        # Asegurarse de que el partner esté en el contexto correcto
        partner = partner.with_context(force_company=request.env.company.id)

        # Crear o actualizar la propiedad
        existing_prop = request.env['ir.property'].sudo().search([
            ('name', '=', 'property_product_pricelist'),
            ('res_id', '=', f'res.partner,{partner.id}')
        ], limit=1)

        if existing_prop:
            existing_prop.sudo().write({
                'value_reference': 'product.pricelist,2',
                'company_id': request.env.company.id,
            })
        else:
            request.env['ir.property'].sudo().create({
                'name': 'property_product_pricelist',
                'res_id': f'res.partner,{partner.id}',
                'res_model': 'res.partner',
                'value_type': 'many2one',
                'value_reference': 'product.pricelist,2',
                'company_id': request.env.company.id,
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