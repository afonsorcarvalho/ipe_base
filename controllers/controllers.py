# -*- coding: utf-8 -*-
from odoo import http

# class IpeBase(http.Controller):
#     @http.route('/ipe_base/ipe_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ipe_base/ipe_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ipe_base.listing', {
#             'root': '/ipe_base/ipe_base',
#             'objects': http.request.env['ipe_base.ipe_base'].search([]),
#         })

#     @http.route('/ipe_base/ipe_base/objects/<model("ipe_base.ipe_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ipe_base.object', {
#             'object': obj
#         })