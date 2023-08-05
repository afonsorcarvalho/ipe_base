# Copyright 2020 Jg Soluções Inteligentes (http://www.jgma.com.br/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ReportInventario(models.TransientModel):
    _name = 'ipe_base.report.inventario'
    _description = 'Wizard for report.inventario'
    _inherit = 'xlsx.report'
    partner_id = fields.Many2one('res.partner')

    name = fields.Char("Nome")
    # Search Criteria
    inventario = fields.Many2one(
        'ipe_base.inventario',
        string='Inventario',
    )
    # Report Result, sale.order
    results = fields.Many2many(
        'ipe_base.especies_lines',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing stored in database',
    )

   
    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        Result = self.env['ipe_base.especies_lines']
        domain = []
        if self.inventario:
            domain += [('inventario_id', '=', self.inventario.id)]
        self.results = Result.read_group(domain,fields=['volume_lenha', 'volume_estaca', 'volume_torete', 
                                                        'volume_tora', 'volume_residuos_lenhoso', 'volume_material_lenhoso',
                                                        'ft', 'ft_ha', 'volume_ha'], 
                                        groupby=['especie_id', 'classe_diametrica'], 
                                        lazy=False)
        _logger.debug(self.results)
