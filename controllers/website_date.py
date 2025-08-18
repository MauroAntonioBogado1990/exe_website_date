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

        # 🔒 Validación del CUIT
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
            #'l10n_ar_afip_responsibility_type_id': int(post.get('afip_id')) if post.get('afip_id') else False,
            'l10n_latam_identification_type_id': request.env['l10n_latam.identification.type'].sudo().search([('name', '=', 'CUIT')], limit=1).id,

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

        #esto se tendría que agregar para notificar al cliente y usuarios
        #esto se tendría que agregar para la notificaion 
        #Enviar alerta interna
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        partner_url = f"{base_url}/web#id={partner.id}&model=res.partner&view_type=form"

        internal_body = f"""
        Se ha registrado un nuevo cliente desde el formulario web.

        Nombre: {partner.name}
        CUIT: {partner.vat}
        Email: {partner.email}
        Teléfono: {partner.phone or partner.mobile}
        Ciudad: {partner.city}
        Provincia: {partner.state_id.name if partner.state_id else ''}
        Dirección: {partner.street}
        Comentario: {comment}

        Ver cliente en Odoo: {partner_url}
        """

        request.env['mail.mail'].sudo().create({
            'subject': f"Nuevo cliente registrado: {partner.name}",
            'body_html': f"<pre>{internal_body}</pre>",
            #'email_to': 'leandro@wstandard.com.ar,deposito@wstandard.com.ar',
            'email_from': request.env.user.company_id.email or 'no-reply@wstandard.com.ar',
        }).send()

        #Enviar bienvenida al cliente
        cliente_body = f"""
        Hola {partner.name},

        Gracias por registrarte en nuestro sistema. Pronto nos pondremos en contacto para completar tu alta.

        Saludos cordiales,  
        El equipo de WStandard
        """

        request.env['mail.mail'].sudo().create({
            'subject': "¡Bienvenido a WStandard!",
            'body_html': f"<p>{cliente_body}</p>",
            'email_to': partner.email,
            'email_from': request.env.user.company_id.email or 'no-reply@wstandard.com.ar',
        }).send()

        return request.render('exe_website_date.template_nuevo_cliente_gracias')
