# -*- coding: utf-8 -*-
# Copyright 2020 Jg Soluções Inteligentes (http://www.jgma.com.br/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
import logging
from math import sqrt
from scipy import stats
_logger = logging.getLogger(__name__)

class InventarioXlsx(models.AbstractModel):
    _name = 'report.ipe_base.report_inventario_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    celulas_soma_amostras = []
    celula_media = fields.Char(default='',store=False)
    def generate_xlsx_report(self, workbook, data, inventario):
            
            # self.create_header(sheet)
            
            domain=[('inventario_id', '=', inventario.id)]
            especie_lines = self.env['ipe_base.especies_lines']
            
            #calculando soma das amostras
            res_line = especie_lines.read_group(domain,fields=['ft','ft_ha', 'volume_ha'], 
                                        groupby=['amostra_id'], 
                                        lazy=False)
            for esp in res_line: 
                print('***************************************')
                print('***************************************')
                print(esp)
                
        
            self.write_amostra_detail(workbook,inventario.amostras)
            self.write_classe_detail(workbook,inventario)
            self.write_resumo_detail(workbook,inventario)
            workbook.close()
           
            
                

    def create_header(self,sheet):
        sheet.write(0,0, 'TABELA POR CLASSE DIAMÉTRICA')
   
   
    def write_table(self,workbook, table,inventario):
        LINE_HEADER = 2
        LINE_INI = 2
        
        sheet = workbook.add_worksheet('Tabela Classificativa')
        sheet.merge_range('A1:R1',"DISTRIBUIÇÃO DO VOLUME POR ESPÉCIE POR CLASSE DIAMÉTRICA  /ha")
        sheet.write(LINE_HEADER,0,"Nº")
        sheet.write(LINE_HEADER,1,"Espécie")
        #montando especies
        domain=[('inventario_id', '=', inventario.id)]
        res_line = self.env['ipe_base.especies_lines'].read_group(domain,fields=['ft','ft_ha', 'volume_ha','especie_id'], 
                                        groupby=['especie_id'], 
                                        lazy=False)
        
        line_count = 0
        for line in res_line:
           
            sheet.write(LINE_INI+1+line_count,0,line_count+1)
            sheet.write(LINE_INI+1+line_count,1,str(line['especie_id'][1]))
            line_count += 1
         
            
        
        sheet.merge_range('C2:E2',"5-14,9")
        sheet.merge_range('F2:H2',"15-24,9")
        sheet.merge_range('I2:K2',"25-34,9")
        sheet.merge_range('L2:M2',"35-44,9")
        sheet.merge_range('O2:Q2',">=45")
        sheet.write(1,17,"TOTAL")
        sheet.write(LINE_HEADER,2,"ft")
        sheet.write(LINE_HEADER,3,"ft/Ha")
        sheet.write(LINE_HEADER,4,"m³/Ha")
        sheet.write(LINE_HEADER,5,"ft")
        sheet.write(LINE_HEADER,6,"ft/Ha")
        sheet.write(LINE_HEADER,7,"m³/Ha")
        sheet.write(LINE_HEADER,8,"ft")
        sheet.write(LINE_HEADER,9,"ft/Ha")
        sheet.write(LINE_HEADER,10,"m³/Ha")
        sheet.write(LINE_HEADER,11,"ft")
        sheet.write(LINE_HEADER,12,"ft/Ha")
        sheet.write(LINE_HEADER,13,"m³/Ha")
        sheet.write(LINE_HEADER,14,"ft")
        sheet.write(LINE_HEADER,15,"ft/Ha")
        sheet.write(LINE_HEADER,16,"m³/Ha")
        sheet.write(LINE_HEADER,17,"m³/Ha")
        LINE_INI = 2
        ROW_INI = 2
        items = ['ft','ft_ha', 'volume_ha']
        classe_count = 0
        especie_count = 0
        item_count = 0
        for especie in table:
          
            classe_count = 0
            for classe in especie:
               
                item_count = 0
                for item in items:
                  
                    sheet.write(LINE_INI+1+especie_count,ROW_INI + classe_count + item_count, classe[item_count])
                    item_count += 1
                classe_count += len(items)
           
            linha =LINE_INI+2+especie_count
            sheet.write_formula('R'+ str(linha), '=E'+str(linha)+'+H'+str(linha)+'+K'+str(linha)+'+N'+str(linha)+'+Q'+str(linha))
            especie_count +=1
        #calculando os totais
        #total de m³/Ha
        sheet.write_formula('R'+ str(linha+1),'=R'+str(LINE_INI+1)+':R'+str(linha))
        #calculando total de arvores
        col = ['C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R']
        for c in col:
            sheet.write_formula(c + str(linha+1),'=SUM('+ c + str(LINE_INI+2) + ':'+ c +str(linha)+')') 
        #somando o total de arvores
        col = ['C','F','I','L','O']
        col = map(lambda x: x + str(linha+1), col) 
        formula = "="
        formula += "+".join(col)
        sheet.write_formula('R' + str(linha+2),formula) 
        self.celula_media = 'R' + str(linha+1)
        sheet.write(linha+1,16,"Total de árvores") 
        sheet.write(linha,1,"TOTAIS") 
           
    
    def busca_posicao_elemento(self, lista, valor):
        for el in lista:
            if valor == el:
                return (lista.index(el),)

            if isinstance(el, list):
                x = self.busca_posicao_elemento(el, valor)
                if x:
                    return (lista.index(el),) + x

        return False
    
    def write_classe_detail(self,workbook,inventario):
        
        table = []
        classes = ['05','15','25','35','45']
        #classe diametrica total
        domain=[('inventario_id', '=', inventario.id)]
        res_line = self.env['ipe_base.especies_lines'].read_group(domain,fields=['ft','ft_ha', 'volume_ha','especie_id'], 
                                        groupby=['especie_id'], 
                                        lazy=False)
        for esp in res_line: 
            t=[]
            
            for classe in classes:
                domain=[('inventario_id', '=', inventario.id),('classe_diametrica', '=',classe),('especie_id','=',esp['especie_id'][0])]
                res_l = self.env['ipe_base.especies_lines'].read_group(domain,fields=['ft','ft_ha', 'volume_ha'], 
                                            groupby=['especie_id'], 
                                            lazy=False)
                if len(res_l)>0:
                    for l in res_l:
                        print(l)
                        array = [l['ft'],l['ft_ha'],l['volume_ha']]
                        t.append(array)
                else:
                    t.append([0,0,0])
            table.append(t)
            
        print(table)
            
        self.write_table(workbook,table,inventario)
        #print(res_line)
    def calcula_variancia(self,inventario):
        res_line = self.env['ipe_base.especies_lines'].read_group([('inventario_id', '=', inventario.id)],fields=['volume_ha'
                                                        ], 
                                        groupby=['amostra_id'], 
                                        lazy=False)
        data = []
        for item in res_line:
            data.append(item['volume_ha'])
            print(data)
        average = sum(data)
        print(average)
        var = 0
        soma2 = 0
        for item in data:
            soma2 = pow(item - average,2)
        
        var = soma2/(len(data)-1)
        
        return var
    
    def calcula_media(self,inventario):
        res_line = self.env['ipe_base.especies_lines'].read_group([('inventario_id', '=', inventario.id)],fields=['volume_ha'
                                                        ], 
                                        groupby=['amostra_id'], 
                                        lazy=False)
        data= []
        for item in res_line:
            data.append(item['volume_ha'])
        
        average = sum(data)
        return average
    
    def calcula_STD(self, inventario):
        var = self.calcula_variancia(inventario)
        return sqrt(var)
        
    def write_resumo_detail(self,workbook,inventario):
        
        res_line = self.env['ipe_base.especies_lines'].read_group([('inventario_id', '=', inventario.id)],fields=['volume_lenha', 'volume_estaca', 'volume_torete', 
                                                        'volume_tora', 'volume_residuos_lenhoso', 'volume_material_lenhoso','especie_id.name',
                                                        ], 
                                        groupby=['especie_id'], 
                                        lazy=False)
        
        #for l in res_line:
        #    print(l['especie_id'][1])
        line_count=0
        LINE_INI = 1
        sheet = workbook.add_worksheet('Resumo de Material Lenhoso')
        sheet.write(0,0,"Resumo de material Lenhoso")
        
        sheet.write(LINE_INI,0,"Nº")
        sheet.write(LINE_INI,1,"ESPÉCIE")
        sheet.write(LINE_INI,2,"TORAS (m³)")
        sheet.write(LINE_INI,3,"TORETES (m³)")
        sheet.write(LINE_INI,4,"ESTACAS (m³)")
        sheet.write(LINE_INI,5,"LENHA (m³)")
        sheet.write(LINE_INI,6,"RESÍDUOS (m³)(30%)")
        sheet.write(LINE_INI,7,"TOTAL (m³)")
        for line in res_line:
            print(line)
            sheet.write(LINE_INI+1+line_count,0,line_count+1)
            sheet.write(LINE_INI+1+line_count,1,str(line['especie_id'][1]))
            sheet.write(LINE_INI+1+line_count,2,line['volume_tora'])
            sheet.write(LINE_INI+1+line_count,3,line['volume_torete'])
            sheet.write(LINE_INI+1+line_count,4,line['volume_estaca'])
            sheet.write(LINE_INI+1+line_count,5,line['volume_lenha'])
            sheet.write(LINE_INI+1+line_count,6,line['volume_residuos_lenhoso'])
            sheet.write(LINE_INI+1+line_count,7,line['volume_material_lenhoso'])
            line_count += 1
        cols = ['C','D','E','F','G','H']
        i = 2
        for c in cols:
            sheet.write(LINE_INI+1+line_count,i,'=SUM('+c+'3:'+c+str(LINE_INI+1+line_count)+')')
            i+=1
        #wirte resumo
        print(self.celulas_soma_amostras)
        sum_amostra = u",".join(self.celulas_soma_amostras)
        print(sum_amostra)
        form_media = self.calcula_media(inventario)
        form_var = self.calcula_variancia(inventario)
        #form_var = "=0"
        #form_var = form_var.encode('utf-8')
        
        form_DP = self.calcula_STD(inventario)
        form_CV = 100*form_DP/form_media
        tstudent = stats.t.ppf(1-0.025, inventario.qtd_amostras-1)
        print("o T de student deu:%s", tstudent)
        form_erro = form_DP/sqrt(inventario.qtd_amostras)
        form_erro_p = (form_erro/form_media)*100
        form_int_max = form_media + tstudent*form_erro
        form_int_min = form_media - tstudent*form_erro
       # form_int_max = '=D2+T.INV(0.05,'+str(inventario.qtd_amostras-1)+')*D4/SQRT('+str(inventario.qtd_amostras)+')'
       # form_int_min = '=D2-T.INV(0.05,'+str(inventario.qtd_amostras-1)+')*D4/SQRT('+str(inventario.qtd_amostras)+')'
        data = (
            [1, 'Volume médio m³/Ha',self.calcula_media(inventario)],
            [2, 'Variância',form_var],
            [3, 'Desvio Padrao',form_DP],
            [4, 'Coeficiente de variação',form_CV],
            [5, 'Erro Padrão(%)',form_erro_p],
            [6, 'Intervalo de confiança','95%'],
            [7, 'Intervalo de confiança Máximo',form_int_max],
            [8, 'Intervalo de confiança Mínimo',form_int_min],
        )
        row = 1
        col = 0
        sheet2 = workbook.add_worksheet("Análise Estatística")
        sheet2.write(0,0, "RESULTADOS OBTIDOS") 
        for item, desc, form in (data):
            sheet2.write(row,col, item)
            sheet2.write_string(row,col+1, desc)
            sheet2.write(row,col+3, form)
            row += 1
               
    def write_amostra_detail(self,workbook,amostras):
        amostra_count=0
        LINE_INI = 1
        for amostra in amostras:
            sheet = workbook.add_worksheet(amostra.name)
            amostra_count+=1
            line_count = 0
            sheet.write(0,0,amostra.name)
            sheet.write(0,3,"Área(m²): " + str(amostra.area_amostra))
            sheet.write(0,4,amostra.area_amostra)
            sheet.write(LINE_INI,0,"Nº")
            sheet.write(LINE_INI,1,"ESPÉCIE")
            sheet.write(LINE_INI,2,"DAP(cm)")
            sheet.write(LINE_INI,3,"HC(m)")
            sheet.write(LINE_INI,4,"VOLUME(m³)")
            
            for line in amostra.especies_lines:
                sheet.write(LINE_INI+1+line_count,0,line_count+1)
                sheet.write(LINE_INI+1+line_count,1,line.especie_id.name)
                sheet.write(LINE_INI+1+line_count,2,line.dap)
                sheet.write(LINE_INI+1+line_count,3,line.h)
                sheet.write(LINE_INI+1+line_count,4,line.volume)
                line_count += 1
            linha = LINE_INI+1+line_count
            sheet.write_formula('E' + str(linha+2),'=SUM(E'+ str(LINE_INI+2) + ':E'+str(linha+1)+')') 
            sheet.write_formula('E' + str(linha+3),'=E' + str(linha+2) + '*10000/E1') 
            cel = u"$'"+str(amostra.name)+u"'.E" + str(linha+3)
            self.celulas_soma_amostras.append(cel)
        
        
        
        
        
        
         
                
