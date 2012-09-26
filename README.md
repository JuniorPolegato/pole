Módulos:

PoleUtil.py: várias funções úteis para o dia a dia, onde a mais importante é a convert_and_format, que usa a localização para converter string, números, datas e booleano.

PoleLog.py: apenas funções para log e depuração em terminal, projetos para fazer log em arquivo em andamento

PoleGTK.py: algumas classes e funções que tornam o uso do GTK no Python bastante legível e fácil, atualmente tem-se as funções:
- message: mensagem na tela vinculada (ou não) à uma janela
- load_images_as_icon: transforma uma imagem em um ícone de stock com o mesmo nome do arquivo, onde este pode ser usado no Glade tal como "gtk-close" e escolher o tamanho padronizado pelo GTK
- build_interface: juntamento com NEW_CLASSES, traduz classes do Glade para classes do PoleGTK, assim um GtkTreeView no Glade com nome iniciando com 'gr_' é transformado em Grid do PoleGTK, GtkEntry iniciando com 'ed_' vira Editor do PoleGTK, GtkWindow iniciado por 'popup_' vira PopupWindow do PoleGTK, GtkButton do Glade iniciado por 'dt_' vira DateButton do PoleGTK. As propriedade extras dessas classes devem ser colocadas em "Dicas de Ferramentas" no Glade, por exemplo, no GtkEntry, iniciado com nome "ed_..." e na "Dicas de ferramentas" tiver "[dica]|upper" (dica é opcional e pipe é separador entre dica e configurações), todo texto digitado será transformado em maiúsculas. Veja o micro-tutorial no github.
- try_function: decorador para callbacks que mostra uma janela para o usuário quando houver algum erro com informações sucintas e imprime no terminal mais detalhes usando PoleLog.
- load_module: carrega um outro projeto herdado de PoleGTK.Project e segura a execução neste ponto
- VirtualWidget: classe que encapsula um widget do GTK para facilitar acesso às propriedade
- Project: classe base para projetos usando PoleGTK que possibilita "self.nome_widget" acessar o widget feito com o Glade
- Grid: classe que possibilita o tratamento de uma grade e um modelo complexo, que segura em si os valores originais e os valores formatados para apresentar na grade, uma forma muito mais amigável para o desenvolvedor e o usuário, utiliza o PoleUtil.convert_and_format. Se a coluna for do tipo float, será apresentado '9.999.999,99' por exemplo, se for int será '9.999.999', ser for bool será uma caixa de verificação, se for date será 'dd/mm/yyyy', , se for time será 'hh:mm:ss' e assim por diante
- GridRow: uma linha da grade retornada como iterador, por exemplo quando se faz "for linha in grade", aí pode-se acessar a coluna pelo nome com linha["coluna"] ou pelo número linha[n], e retorna um tupla com o valor original e o formatado.
- PopupWindow: cria um popup e o posiciona a partir de um widget, ficando abaixo deste, como calendário, ou centralizado e dá um retorno que quiser ao ser chamado com run() e fica parado neste ponto.
- DateButton: um botão que exibe em seu label uma data, mês e/ou hora e ao clicar abre um calendário especial de acordo com o tipo.
- Calendar: calendário especial baseado em PopupWindow e usado por DateButton

PolePDF.py: usado para gerar pdf usando células e tabelas de forma bem intuitiva, baseado em reportlabs, onde estes objetos já se encaixando da esquerda para a direita e de cima para baixo (teoria de cortes de planos), ou podem ser posicionados de forma flutuante e absoluta

PoleRelatorio.py: módulo para criar relatórios em PDF a partir de alguns parâmetros e dados, usando células e tabelas via PolePDF

PoleXML.py: uma pytonização do libxml2, assim pode-se criar/alterar/obter um atribo xml com `xml.no['atrubuto'] = 'valor'´ e o conteúdo de um nó com `xml.no = 'conteúdo'´ e a estrutura se auto gera ao fazer `xml.no1.no2.no3 = 'teste'´

PoleXmlSec.c: em CPython, assina XML e verifica (ainda com problemas a verificação)

PoleNFe.py: utiliza o suds para wsdl e uma estrutura de diretórios que deve ser especialmente prepara para utilizar os webservices da Nota Fiscal Eletrônica

PoleDANFe.py: gera DANFe em PDF a partir de uma tabela de banco de dados ou XML (ainda terminando)


Além disso, ainda vinculado tem o Projeto GladePy, que lê um arquivo .ui gerado pelo Glade e cria ou atualizar um .py pronto para desenvolver, com todas as funções de callback criadas no Glade e com os devidos imports, além de possibilitar que se inclua no código a .ui de forma "criptografada" onde não é preciso ter a interface num arquivo separado, bom para distribuir versões estáveis. Para terminar, fiz uma alteração no Glade que possibilita chamar um programa externo com informação do arquivo .ui e da função callback que foi clicada, no caso chamando o GladePy, ele já atualiza o .py e te posiciona nessa função usando o Geany, mas pode ser configurado outro editor, desde que ele tenha parâmetro para posicionamento em linha e coluna através do arquivo $HOME/.gladepy.conf
