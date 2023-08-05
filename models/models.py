# -*- coding: utf-8 -*-

from odoo import models, fields, api
from math import pi,sqrt
import logging
_logger = logging.getLogger(__name__)


class ipe_inventario(models.Model):
    _name = 'ipe_base.inventario'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Inventário'
    name = fields.Char()
    description = fields.Text("Descrição do Inventário")
    area_total = fields.Float(string="Área total(Ha)" ,digits=(10,4))
    amostras = fields.One2many('ipe_base.amostras','inventario_id', string='Amostras')
    qtd_amostras = fields.Integer('Qtd Amostras', compute = '_compute_qt_amostras', store=True)
    area_total_amostras = fields.Integer('Área total das Amostras', compute = '_compute_area_amostras', store=True,digits=(10,4))
    

    def write(self, vals):
        
        return super().write(vals)
    

    @api.depends("amostras" )
    def _compute_qt_amostras(self):
        for s in self:
            s.qtd_amostras = len(s.amostras)
    
   
    @api.depends("amostras")
    def _compute_area_amostras(self):
        for s in self:
            area_amostra_list = s.amostras.mapped('area_amostra')
            s.area_total_amostras = sum(area_amostra_list)

    
        

class ipe_amostra(models.Model):
    _name = 'ipe_base.amostras'
    _description = 'Amostras'
    _order = 'sequence'
   
    
    sequence = fields.Integer()
    name = fields.Char("Nome", help="Nome da amostra, pode ser amostra01 ou amostra02 etc...")
    area_amostra = fields.Float(string="Área amostra(m²)")
    inventario_id = fields.Many2one('ipe_base.inventario', string='Inventário')
    especies_lines = fields.One2many(comodel_name='ipe_base.especies_lines', inverse_name='amostra_id', string='Espécies')
    
    
    def _compute_mean_volume(self):
        for s in self:
            volmes = s.especies_lines.mapped('volume')

    def action_calcula_volume(self):
        self._compute_mean_volume()
        return True

class ipe_especies_line(models.Model):
    _name = 'ipe_base.especies_lines'
    _description = 'linhas de espécies'
    _order = 'id, sequence'
    CLASSE_DIAMETRICA = [
        ('05','5 - 14,9'),
        ('15','15 - 24,9'),
        ('25','25 - 34,9'),
        ('35','35 - 44,9'),
        ('45','>=45')
        ]
    name = fields.Char("Nome") 
    sequence = fields.Integer()
    amostra_id = fields.Many2one('ipe_base.amostras', string='Amostra')
    inventario_id = fields.Many2one('ipe_base.inventario', related='amostra_id.inventario_id',
    store=True
    )
    especie_id = fields.Many2one('ipe_base.especies', string='Espécie',required=True)
    scientific_name = fields.Char("Nome científico",related='especie_id.scientific_name')
    
    dap =fields.Float("DAP(cm)",help="Diâmetro na altura do peito em Centímetros",required=True)
    h = fields.Float("Altura Comercial (m)",help="Altura comercial",required=True)
    fator_de_forma = fields.Float("Fator de forma",related='especie_id.fator_de_forma',
                                   store=True,required=True,
                                   help="Entre com o valor do fator de forma, usualmente coníferas 0,5 e flolhosas 0,7", default=0.7)
    volume = fields.Float("Volume (m³)",compute='_compute_volume',store=True,digits=(8,4))
    ft_ha = fields.Float("Frequencia/Ha", compute="_compute_ft_ha",store=True, digits=(8,4))
  
    ft = fields.Integer("Frequencia",default=1)
   
    volume_ha = fields.Float("Volume/Ha (m³/Ha)", compute="_compute_volume_ha", store=True, digits=(8,4))
    classe_diametrica = fields.Selection(CLASSE_DIAMETRICA, compute="_compute_classe_diametrica",store=True)
    tipo_material_lenhoso = fields.Many2one('ipe_base.tipo_material_lenhoso',string="Tipo de material lenhoso", 
                                            compute="_compute_tipo_material_lenhoso", store=True)
    volume_material_lenhoso = fields.Float(string='Volume Total(m³)', digits=(8, 3),
                                           compute='_compute_volume_material_lenhoso',store=True)
    volume_residuos_lenhoso = fields.Float(string='Resíduos(m³) 30%', digits=(8, 3),
                                           compute='_compute_volume_residuos_lenhoso',store=True)
    volume_lenha = fields.Float(string='Lenha(m³)', digits=(8, 3),
                                           compute='_compute_tipo_material_lenhoso',store=True)
    volume_estaca = fields.Float(string='Estacas(m³)', digits=(8, 3),
                                           compute='_compute_tipo_material_lenhoso',store=True)
    volume_torete = fields.Float(string='Toretes(m³)', digits=(8, 3),
                                           compute='_compute_tipo_material_lenhoso',store=True)
    volume_tora = fields.Float(string='Toras(m³)', digits=(8, 3),
                                           compute='_compute_tipo_material_lenhoso',store=True)
    
    
    @api.depends("dap", "h","fator_de_forma","especie_id.fator_de_forma" )
    def _compute_volume(self):
        for s in self:
            s.volume = ((pi*s.dap**2)/40000)*s.h*s.especie_id.fator_de_forma
    
   
    @api.depends("amostra_id",'amostra_id.inventario_id.area_total_amostras','dap','classe_diametrica')
    def _compute_ft_ha(self):
        for s in self:
            ha = s.amostra_id.inventario_id.area_total_amostras/10000
            s.ft_ha = 1/ha
            # cd =[('05','15','25','35','45')]
            # for c in cd:
            #     if s.classe_diametrica == c:
            #         s.ft_5 = s.ft
            #         s.ft_ha_5 = s.ft_ha
            #         s.ft_ha_15 = 0
            #         s.ft_ha_25 = 0
            #         s.ft_ha_35 = 0
            #         s.ft_ha_45 = 0
            # if s.classe_diametrica == '15':
            #     s.ft_15 = s.ft
            #     s.ft_ha_15 = s.ft_ha
            # if s.classe_diametrica == '25':
            #     s.ft_25 = s.ft
            #     s.ft_ha_25 = s.ft_ha
            # if s.classe_diametrica == '35':
            #     s.ft_35 = s.ft
            #     s.ft_ha_35 = s.ft_ha
            # if s.classe_diametrica == '45':
            #     s.ft_45 = s.ft
            #     s.ft_ha_5 = s.ft_ha
            
            
            
    
    @api.depends("volume" , "amostra_id","amostra_id.area_amostra")
    def _compute_volume_ha(self):
        for s in self:
            ha = s.amostra_id.area_amostra/10000
            s.volume_ha = s.volume/ha
            
    @api.depends("dap","inventario_id","amostra_id")
    def _compute_classe_diametrica(self):
        for s in self:
            dap = s.dap
            if dap >= 5 and dap < 15:
                s.classe_diametrica = '05'
            if dap >= 15 and dap < 25:
                s.classe_diametrica = '15'
            if dap >= 25 and dap < 35:
                s.classe_diametrica = '25'
            if dap >= 35 and dap < 45:
                s.classe_diametrica = '35'
            if dap >= 45:
                s.classe_diametrica = '45'
    # funcão que configura o para o tipo de material lenhoso, e também coloca
    # o volume no campo certo de acordo com o tipo lenha, estaca, tora e toretes            
    def configura_material(self,tipo,volume):
        _logger.debug("Configurando material")
      
        if self.dap >= tipo.min_dap and self.dap < tipo.max_dap:
            self.tipo_material_lenhoso = tipo
            if self.tipo_material_lenhoso.name == 'Estaca':
                self.volume_estaca = volume
            if self.tipo_material_lenhoso.name == 'Lenha':
                self.volume_lenha = volume
            if self.tipo_material_lenhoso.name == 'Toretes':
                self.volume_torete = volume
            if self.tipo_material_lenhoso.name == 'Toras':
                self.volume_tora = volume
                
        _logger.debug("Tipo configurado %s",self.tipo_material_lenhoso.name)
            
    
    @api.depends("amostra_id",'amostra_id.inventario_id.area_total_amostras','dap')
    def _compute_tipo_material_lenhoso(self):
        for s in self:
            tipo_lst = self.env['ipe_base.tipo_material_lenhoso'].search([])
            volume = s.calcula_volume_material_lenhoso(s)
            _logger.debug("Volume de material lenhoso: %s", volume)
            tipo_material = 0
            for t in tipo_lst:
                if t.name == "Estaca":
                    if s.especie_id.serve_para_estaca:
                        s.configura_material(t,volume)
                else:  
                    s.configura_material(t,volume)
            _logger.debug("Finalizado Configaração do record")
            _logger.debug("Resumo:")
            _logger.debug(" tipo %s", s.tipo_material_lenhoso)
            _logger.debug("Volume lenha: %s,Volume estaca: %s,Volume toretes: %s,Volume tora: %s", 
                          s.volume_lenha,s.volume_estaca,s.volume_torete,s.volume_tora)
            
                            
                            
    #calcula volume total do material lenhoso
    # volume de material lenhoso + 30% de resíduos
    def calcula_volume_total(self,rec):
        volume_total = rec.volume_ha*rec.amostra_id.inventario_id.area_total 
        return volume_total + volume_total*0.3
    
    #calcula volume material lenhoso 
    def calcula_volume_material_lenhoso(self,rec):     
        return rec.volume_ha*rec.amostra_id.inventario_id.area_total 
              
          
   
    @api.depends("amostra_id",'amostra_id.inventario_id.area_total_amostras','dap',)
    def _compute_volume_material_lenhoso(self):
        for s in self:
            s.volume_material_lenhoso = s.calcula_volume_total(s)
    
   
    @api.depends("amostra_id",'amostra_id.inventario_id.area_total_amostras','dap','volume_material_lenhoso')
    def _compute_volume_residuos_lenhoso(self):
        for s in self:
            s.volume_residuos_lenhoso = s.calcula_volume_material_lenhoso(s)*0.3
                    
            
class tipoMaterialLenhoso(models.Model):
    _name = 'ipe_base.tipo_material_lenhoso'
    _description = "Tipo de material Lenhoso"
    
    name = fields.Char("Nome")   
    max_dap = fields.Float("Max")
    min_dap = fields.Float("Min")
    
    
class ipe_especies(models.Model):
    _name = 'ipe_base.especies'
    _description = 'Espécies'
    _order = 'name'

    name = fields.Char("Nome")
    scientific_name = fields.Char("Nome científico")
    tipo = fields.Selection(
        string="Tipo",
        selection=[
                ('conifera', 'Conífera'),
                ('folhosa', 'Folhosa'),
        ],
        default='conifera',
        help="Conifera ou Folhosa, ajusta o fator de forma"
    )
    fator_de_forma = fields.Float("Fator de Forma",default=0.55)
    serve_para_estaca = fields.Boolean(string="Serve para estaca?")

    
     