#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
#                                                                           #
# File   : gladepy.py                                                       #
# Version: 0.5                                                              #
# Project: GladePy                                                          #
# Date   : May, 29 of 2011                                                  #
# Author  : Claudio Polegato Junior                                         #
#                                                                           #
#  Copyright© 2011 - Claudio Polegato Junior <linux@juniorpolegato.com.br>  #
#  All rights reserveds                                                     #
#                                                                           #
#############################################################################

import xml.dom.minidom
import sys
import os
import zlib
import base64

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Classe que conterá o código para criação e alteração do código Python
#     de forma automática e conforme descrito na proposta do projeto
#     GladePy
class GladePy(object):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Iniciar a classe GladePy com o nome do projeto passado como parâmetro
    def __init__(self, projeto_glade=None, codigo_python=None,
                 coluna_combo=0, imagem_botao=True, funcao=None,
                 juntar=False, classes_base=''):
        # Dicionário que conterá informações de funções chamads pelos sinais/eventos na forma:
        #   "nome_da_função": [("sinal_0/evento_0", "nome_do_widget_0", "classe_do_widget_0"), ..., ("sinal_n/evento_n", "nome_do_widget_n", "classe_do_widget_n")]
        self.funcoes = {}
        # Se já iniciar a classe com um dado nome de projeto XML do Glade,
        #     segue criando o código em Python, senão pára por aqui mesmo
        if not projeto_glade:
            return
        # Atualizar as informações para o dicionário acima, parando se for mal sucedido
        if not self.atualizar_dicionario_funcoes(projeto_glade):
            return
        # Variável que conterá o nome do arquivo com código Python, o qual, se não fornecido,
        #     será criado a partir do nome do projeto em XML do Glade
        if not codigo_python:
            codigo_python = self.gerar_nome_codigo_python(projeto_glade)
        # Atualizar o código Python conforme dados do dicionário e proposta do projeto GladePy
        linha_funcao = self.atualizar_codigo_python(
                            projeto_glade, codigo_python, coluna_combo,
                                imagem_botao, funcao, juntar, classes_base)
        # Se passada, localizar a linha da função a ser posicionado o cursor
        if editor:
            linha_de_comando = editor
            if funcao and line_option and linha_funcao:
                linha_de_comando += " %s %i" % (line_option, linha_funcao)
                if column_option:
                    linha_de_comando += " " + column_option + " 8"
            os.system(linha_de_comando + ' "' + codigo_python + '"')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Gerar um nome de arquivo para o código Python a partir do nome do
    #     projeto XML do Glade, trocando a extensão por "py", sendo que
    #     se não tiver extensão, adicona ao nome ".py"
    def gerar_nome_codigo_python(self, projeto_glade):
        if projeto_glade:
            ponto = projeto_glade.rfind('.')
            if ponto > 0:
                return projeto_glade[:ponto]+".py"
            else:
                return projeto_glade+".py"
        return None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Código para extrair as funções do XML do Glade, que serão as chaves
    #   de um dicionário (funcoes), onde este representa uma lista que
    #   contem elementos na forma de tuplas, as quais contem 3 elementos
    #   texto: sinal/evento, widget e classe GTK
    def atualizar_dicionario_funcoes(self, projeto_glade):
        # Carregar o XML do Glade para tramamento, retornando False se obtiver erro
        try:
            glade_dom = xml.dom.minidom.parse(projeto_glade)
        except:
            print "Erro ao abrir ou carregados dados XML do projeto `%s´" % (projeto_glade)
            return False
        # Tratar cada nó XML cujo nome seja widget
        for widget in glade_dom.getElementsByTagName("object"):
          # Tratar cada nó XML filho do nó "widget" em questão
          for filho in widget.childNodes:
              # Tratar esse nó filho em questão caso tenha nome "signal"
              if filho.nodeName == "signal":
                  # Se já tiver a função indicada pelo atributo "handler" desse nó "signal" na lista de funções já encontradas, adiciona mais informações à esta
                  if filho.getAttribute("handler") in self.funcoes:
                      # À função encontrada no dicionário é adicionado mais informações de nome do sinal, nome do widget e classe do widget em questão
                      self.funcoes[filho.getAttribute("handler")].append((filho.getAttribute("name"),widget.getAttribute("id"),widget.getAttribute("class")))
                  # Se não tiver a função indicada pelo atributo "handler" desse nó "signal" na lista de funções já encontradas, adiciona essa função na lista e suas primeiras informações
                  else:
                      # Nome de função encontrada é adicionada ao dicionário e inicializada com as primeiras informações de nome do sinal, nome do widget e classe do widget
                      self.funcoes[filho.getAttribute("handler")] = [(filho.getAttribute("name"), widget.getAttribute("id"),widget.getAttribute("class"))]
        # Retornar verdadeiro indicando que tudo ocorreu dentro da conformidade
        return True

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Caso o arquivo com código Python não existir,
    #     criar um com o conteúdo inicial em conformidade
    #     à proposta do projeto GladePy
    def criar_codigo_python(self, projeto_glade, codigo_python,
                              coluna_combo, imagem_botao, classes_base):
        if classes_base:
            classes_base = classes_base.strip()
            if classes_base[0] != ',':
                classes_base = ', ' + ', '.join(classes_base.split(','))
        arquivo = open(codigo_python, "w")
        arquivo.write("#!/usr/bin/env python\n")
        arquivo.write("# -*- coding: utf-8 -*-\n\n")
        arquivo.write("import pygtk\n")
        arquivo.write("pygtk.require(\"2.0\")\n")
        arquivo.write("import gtk\n")
        arquivo.write("import zlib\n")
        arquivo.write("import base64\n\n")
        arquivo.write("import pole\n\n")
        arquivo.write("class Project(pole.gtk.Project%s):\n" % classes_base)
        arquivo.write("    @pole.gtk.try_function\n")
        arquivo.write("    def __init__(self, parent, loop, data):\n")
        arquivo.write("        ui = '/caminho/projeto.ui'\n")
        arquivo.write("        super(Project, self).__init__(ui, parent, loop, data)\n")
        arquivo.write("        # Your code below, don't touch on lines above\n\n")
        arquivo.write("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##\n")
        arquivo.write("# Open stand-alone project, use pole.gtk.load_module to open as a module\n")
        arquivo.write("if  __name__ == \"__main__\":\n")
        arquivo.write("    class Parent(object):\n")
        arquivo.write("        def __init__(self):\n")
        arquivo.write("            # Variáveis para criação independente\n")
        arquivo.write("            pass\n")
        arquivo.write("    project = Project(Parent(), None, None)\n")
        arquivo.write("    gtk.main()\n")
        arquivo.close()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Atualizar o código Python conforme dados do dicionário e proposta
    #     do projeto GladePy
    def atualizar_codigo_python(self, projeto_glade, codigo_python,
                                coluna_combo, imagem_botao,
                                funcao_posicionada=None, juntar=False,
                                classes_base=''):
        # Se não existir o código python, criar um código inicial e então atualizar
        if not os.path.exists(codigo_python):
            self.criar_codigo_python(projeto_glade, codigo_python,
                               coluna_combo, imagem_botao, classes_base)
        # Abrir o arquivo de código Python
        arquivo = open(codigo_python, "r+")
        # Encontrar a classe Projeto e guardar a posição subseqüente
        inicio_codigo_classe_projeto = 0
        linha_codigo_classe_projeto = 0
        linha = ' '
        linha_classe = "class Project(pole.gtk.Project"
        while linha and linha_classe not in linha:
            linha = arquivo.readline()
            inicio_codigo_classe_projeto += len(linha)
            linha_codigo_classe_projeto += 1
        # Encontrar onde termina a classe Projeto, guardando numa lista essas linha
        linha = arquivo.readline().decode("utf-8")
        codigo_classe_projeto = []
        while linha and (linha[:4] == "    " or linha == '\n'):
            codigo_classe_projeto.append(linha)
            linha = arquivo.readline().decode("utf-8")
        # Guardar o código subseqüente ao conteúdo da classe Projeto, pois será adicionado ao fim da atualização
        arquivo.seek(-len(linha), 1)
        parte_final_codigo_python = arquivo.read().decode("utf-8")

        declaracao = u"        ui = "
        linha_declaracao = self.localizar_codigo(declaracao, codigo_classe_projeto)
        if juntar:
            codigo_classe_projeto[linha_declaracao] = "        ui = zlib.decompress(base64.b64decode('" + base64.b64encode(zlib.compress(open(projeto_glade).read(), 9)) + "'))\n"
        else:
            codigo_classe_projeto[linha_declaracao] = "        ui = '" + projeto_glade + "'\n"


        # Verificar dentro desse conteúdo a declaração da função X
        # Se encontrar uma declaração da função X, verifica se entre os comentários acima dessa tem o comentário a padrão de cada informação da função. Se não tiver, adiciona este antes da função.
        # Se não encontrar a declaração da função X, cria uma com os comentários padrões depois do bloco já existente da classe Projeto

        # Tratar cada função no dicionário, atualizando o código conforme necessário
        novas_funcoes = []
        for funcao in self.funcoes.keys():
            # Criar as linhas de comentário da declaração da função encontrada no XML do Glade
            comentarios_novos = [u"    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##\n",
                                 u"    # Signal/event on widget(GTK class) connected to %s\n" % (funcao)
                                ]
            for informacoes_funcao in self.funcoes[funcao]:
                comentarios_novos.append("    # %s em %s(%s)\n" % (informacoes_funcao))
            declaracao = u"    def %s(self, *args):" % (funcao)
            # Verificar em qual linha está essa declaração, se houver
            linha_declaracao = self.localizar_codigo(declaracao, codigo_classe_projeto)
            # Caso não exista a declaração, coloca esta declaracao e comentários na lista de novas declarações
            if linha_declaracao == None:
                for novo_comentario in comentarios_novos:
                    novas_funcoes.append(novo_comentario)
                # Aqui seria interessante colocar uma opção para caso queira a função comentada
                # if declaracao_comentada:
                #     novas_funcoes.append("    # " + declaracao[4:])
                # else:
                novas_funcoes.append("    @pole.gtk.try_function\n")
                novas_funcoes.append(declaracao + '\n')
                novas_funcoes.append("        pass\n")
                novas_funcoes.append('\n')
            # Caso exista a declaração, mas esta não tiver comentário nenhum imediatamente acima, coloca todos os comentários novos sobre essa declaração
            else:
                if codigo_classe_projeto[linha_declaracao - 1] != "    @pole.gtk.try_function\n":
                    codigo_classe_projeto.insert(linha_declaracao, "    @pole.gtk.try_function\n")
                    linha_declaracao += 1
                if  codigo_classe_projeto[linha_declaracao - 2][:5] != "    #":
                    for comentario_novo in comentarios_novos:
                        codigo_classe_projeto.insert(linha_declaracao - 1, comentario_novo)
                        linha_declaracao += 1
                # Caso exista a declaração, atualizar se necessário, marcando comentários antigos se necessário
                else:
                    # Tratando os comentários existentes no da declaração encontrada no código da classe Projeto
                    i = linha_declaracao - 2
                    comentario_existente = codigo_classe_projeto[i]
                    while comentario_existente[:5] == "    #":
                        # Se não tiver espaço após o #, coloca para manter um padrão só
                        if comentario_existente[5] != ' ':
                          comentario_existente = comentario_existente[:5] + ' ' + comentario_existente[5:]
                          codigo_classe_projeto[i] = codigo_classe_projeto[i][:5] + ' ' + codigo_classe_projeto[i][5:]
                        # Identificar se já existe o comentário dentre os comentários detectados e sua posição
                        posicao = self.localizar_comentario(comentario_existente, comentarios_novos)
                        # Se o comentário não constar dentre os novos detectados, marcar como comentário antigo se já não estiver marcado
                        if posicao == None:
                            if codigo_classe_projeto[i][6:8] != u"» ":
                                codigo_classe_projeto[i] = codigo_classe_projeto[i][:6] + u"» " + codigo_classe_projeto[i][6:]
                        # Se o comentário constar dentre os novos detectados, desmarcar se estiver marcado como comentário antigo e tirar da lista de comentários novos
                        else:
                            if  codigo_classe_projeto[i][6:8] == u"» ":
                                codigo_classe_projeto[i] = codigo_classe_projeto[i][:6] + codigo_classe_projeto[i][8:]
                            del comentarios_novos[posicao]
                        # Se está na primeira linha do código da classe Projeto, sai da análise
                        if i == 0:
                          break
                        # Obter uma linha do código da classe Projeto antes da analisada atualmente para nova análise
                        i -= 1
                        comentario_existente = codigo_classe_projeto[i]
                    # Resta agora em comentarios_novos, os comentários novos :)
                    # Adicionar os comentários novos dentre os comentários já existentes no código da classe Projeto para a declaração de função em questão
                    for comentario_novo in comentarios_novos:
                        codigo_classe_projeto.insert(linha_declaracao - 1, comentario_novo)
                        linha_declaracao += 1

        # Marcar comentários como antigos de funções presentes no código Python e não declaradas no XML do Glade
        i = 0
        while i < len(codigo_classe_projeto):
            linha = codigo_classe_projeto[i]
            # Percorre o código da classe Projeto e pára ao encontrar uma declaração de função, comentada ou não com #
            while linha[:10] == "    def __" or linha[:8] != "    def " and linha[:9] != "    #def " and linha[:10] != "    # def ":
                i += 1
                if i == len(codigo_classe_projeto):
                    break
                linha = codigo_classe_projeto[i]
            # Se terminou o código, sai dessa rotina
            if i == len(codigo_classe_projeto):
                break
            # Verifica se essa declaração está dentre as do XML do Glade, tratando comentários
            adicional = ""
            if linha[5] == '#':
                adicional = '#'
            if linha[6] == ' ':
                adicional += ' '
            encontrado = False
            for funcao in self.funcoes.keys():
                declaracao = "    %sdef %s(self, *args):\n" % (adicional, funcao)
                if declaracao == linha[:len(declaracao)]:
                    encontrado = True
                    break
            # Se esta declaração não estiver, então marca os comentários dela como comentários antigos
            if not encontrado:
                j = i - 1
                while j >= 0 and codigo_classe_projeto[j][:5] == "    #":
                    if codigo_classe_projeto[j][:7] != u"    # »" and codigo_classe_projeto[j][:7] != "    # #":
                         codigo_classe_projeto[j] = u"    # »" + codigo_classe_projeto[j][5:]
                    j -= 1
            i += 1

        # Pegando o código antigo ignorando o existente acima da classe Projeto
        arquivo.seek(inicio_codigo_classe_projeto)
        codigo_antigo = arquivo.read().decode("utf-8")
        # Compor o código a atualizado
        codigo_atualizado = ''.join(codigo_classe_projeto)
        codigo_atualizado += ''.join(novas_funcoes)
        codigo_atualizado += parte_final_codigo_python
        # Salvar as alterações
        if codigo_antigo != codigo_atualizado:
            # Ignorar no arquivo o código anterior existente acima da classe Projeto e não pertencente à esta
            arquivo.seek(inicio_codigo_classe_projeto)
            # Escrever no arquivo as atualizações da classe Projeto
            arquivo.write(codigo_atualizado.encode("utf-8"))
            # Desconsiderar o restante do arquivo que agora se torna lixo
            arquivo.truncate()
            # Terminado! Fechar o arquivo
            arquivo.close()
        print "\nCódigo Python para o projeto `%s´ criado com sucesso em `%s´!\n" % (projeto_glade, codigo_python)
        if funcao_posicionada:
            declaracao = u"    def %s(self, *args):" % (funcao_posicionada)
            linha_declaracao = self.localizar_codigo(declaracao, codigo_classe_projeto + novas_funcoes)
            return linha_declaracao + linha_codigo_classe_projeto + 2
        return None

    # Localizar em que linha/posição está determinada declaração de função em um código considerando o tamanho desta, isto é, se tiver mais alguma coisa depois (código ou comentário), ela será considerada encontrada
    def localizar_codigo(self, codigo_a_localizar, codigo_total):
        for i in range(len(codigo_total)):
            if codigo_total[i][:len(codigo_a_localizar)] == codigo_a_localizar:
              return i
        return None

    # Localizar em que linha/posição está determinado comentário, o qual é extraído de um código Python editável pelo programador, dentre novos comentários detectados no XML do Glade, considerando o tamanho do novo comentário e tratando a marca de comentário antigo '»'
    def localizar_comentario(self, comentario_a_localizar, comentario_total):
        if comentario_a_localizar[:8] == u"    # » ":
            comentario_a_localizar = comentario_a_localizar[:6] + comentario_a_localizar[8:]
        for i in range(len(comentario_total)):
            if comentario_total[i] == comentario_a_localizar[:len(comentario_total[i])]:
                return i
        return None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Caso este módulo seja chamado diretamente pelo usuário, realiza a
#      operação de criar ou atualizar o código em Python de acordo
#      com o projeto em XML do Glade e seguindo a proposta do
#      gladepy por Claudio Polegato Junior
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "\nUso: [python] %s [opções] nome_projeto_glade [nome_código_python]\n" % (sys.argv[0])
        print "    Onde:"
        print "        Opções. . . . . .: opções que mudam a forma padrão de  tratamento  e"
        print "                           geração do código:"
        print "                           -f <função>:  nome da função sob a qual  o cursor"
        print "                                         será posicionado ao abrir o editor."
        print "                                         O editor  se  encontra  no  arquivo"
        print "                                         .gladepy.conf no  diretório HOME do"
        print "                                         usuário.  Este  arquivo  terá  três"
        print "                                         variáveis:  editor,  line_option  e"
        print "                                         column_option no  formato do Python"
        print "                                         variável = \"valor\" por linha."
        print "                           -c <coluna>:  coluna a ser mostrada nas caixas de"
        print "                                         combinação  (combos). None para não"
        print "                                         mostrar  nenhuma,  deverá ser feito"
        print "                                         manualmente.  Se   não  especificar"
        print "                                         esta opção,  a coluna 0 será usada."
        print "                           -img_btn   :  Se esta opção for especificada, não"
        print "                                         gera     código     para     mostar"
        print "                                         impreterivelmente  as  imagens  nos"
        print "                                         botões.   Neste    caso   segue   o"
        print "                                         comportamento do tema ou Gnome, que"
        print "                                         por padrão  não  mostra  as imagens"
        print "                                         nos botões."
        print "                           -join      :  Se  esta  opção  for  especificada,"
        print "                                         junta  a  inteface  gráfica XML  no"
        print "                                         código Pyhton. Este XML estará numa"
        print "                                         numa    variável    comprimida    e"
        print "                                         codificada  em base64 para previnir"
        print "                                         incompatibilidades    entre    esta"
        print "                                         variável e o  arquivo XML do Glade."
        print "                                         Vantagem de ter  tudo em um arquivo"
        print "                                         só,  desvantagem  que  ao alterar a"
        print "                                         inteface no Glade, deve-se executar"
        print "                                         executar  novamente  o GladePy para"
        print "                                         atualizar esta variável."
        print "                           -baseclasses: Se  esta  opção  for  especificada,"
        print "                                         adiciona o  parâmetro seguinte como"
        print "                                         classe(s)-base junto ao Project, as"
        print "                                         quais  devem  estar  separadas  por"
        print "                                         vírgula se for mais de uma."
        print "        nome_projeto_glade: nome obrigatório  do  arquivo  que  contém o XML"
        print "                            gerado  pelo  Glade,   geralmente  com  extensão"
        print "                            `.glade´ tratado  na  versão  0.2 por libGlade e"
        print "                            agora com extensão  `.ui´  tratado na versão 0.3"
        print "                            por GtkBuilder."
        print "        nome_código_python: nome opcional do arquivo que conterá o código em"
        print "                            Python,  novo   ou  atualizado,  geralmente  com"
        print "                            extensão `.py´."
        print
        print "    Observação: se o nome do arquivo que conterá o código  em Python não for"
        print "                fornecido, será criado ou usado um nome  de arquivo trocando"
        print "                a extensão do nome do arquivo com o XML  gerado pelo  Glade,"
        print "                fornecido obrigatoriamente, pela extensão `.py´, adicionando"
        print "                esta  caso  o  arquivo  não  tenha  extensão.  O arquivo  de"
        print "                configuração  em  ~/.gladepy.conf  configura as variáveis de"
        print "                editor  e   opções   acima,   sendo   para   -c  a  variável"
        print "                combo_column, para -join a  variável  join e para -img_btn a"
        print "                variável image_button.\n"
    else:
        nome_projeto_glade = None
        nome_codigo_python = None
        # Configurações padrão e importando as configurações de ~/.gladepy.conf
        editor = None
        line_option = None
        column_option = None
        combo_column = 0
        image_button = True
        join = False
        baseclasses = ''
        try:
            exec(open(os.environ["HOME"] + "/.gladepy.conf").read())
        except:
            pass
        funcao = None
        parametro = 1
        while parametro < len(sys.argv):
            if sys.argv[parametro] == "-baseclasses":
                parametro += 1
                baseclasses = ', ' + ', '.join(c.strip() for c
                                      in sys.argv[parametro].split(','))
            if sys.argv[parametro] == "-join":
                join = True
            elif sys.argv[parametro] == "-f":
                parametro += 1
                funcao = sys.argv[parametro]
            elif sys.argv[parametro] == "-c":
                parametro += 1
                if sys.argv[parametro].upper() == "NONE":
                    combo_column = None
                else:
                    combo_column = int(sys.argv[parametro])
            elif sys.argv[parametro] == "-img_btn":
                image_button = False
            elif nome_projeto_glade:
                nome_codigo_python = sys.argv[parametro]
            else:
                nome_projeto_glade = sys.argv[parametro]
            parametro += 1
        GladePy(nome_projeto_glade, nome_codigo_python, combo_column,
                                image_button, funcao, join, baseclasses)
