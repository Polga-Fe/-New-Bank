#Importações
from colorama import Fore, Style, Back
from datetime import datetime, timedelta
from os import path
from json import dumps, loads

def arquivo_base():
    caminho_base = path.expanduser('~') + '\\documents\\dados.csv'
    if not path.exists(caminho_base):
        with open (caminho_base, 'w') as arquivo_base:
            arquivo_base.close()
    return caminho_base

def ler_arquivo():
    with open(arquivo_base(), 'r') as arquivo:
        dados = arquivo.readlines()
    return dados

def investimento():
    print(    '''OBRIGADO POR DECIDIR INVESTIR CONOSCO.\nOPÇÕES COM ATÉ 120% DE CDI!
    1. 105% DE CDI")
    2. 110% DE CDI")
    3. 115% DE CDI")
    4. 120% DE CDI''')

    while True:
        try:
            op = int(input("Escolha uma opção (1-4): "))
            if op in [1, 2, 3, 4]:
                break
        except ValueError:
            print("Por favor, insira um número inteiro válido.")

    taxas = {1: 0.05, 2: 0.10, 3: 0.15, 4: 0.20}
    return taxas[op]

def atualizar_investimento():
    from datetime import datetime

    dados = ler_arquivo()

    for index, registro in enumerate(dados):
        registro = loads(registro)

        if registro['tipo'].upper() == 'INVESTIMENTO':
            data_investida = datetime.strptime(registro['data'], '%d/%m/%Y %H:%M:%S')
            data_atual = datetime.now()
            temp = (data_atual - data_investida).days
            i_diario = (0.1183 / 252) * registro['taxa']
            registro['montante_investimento'] = f"{float(registro['valor']) * (1 + i_diario)**temp:.2f}"
        dados[index] = dumps(registro)

    with open(arquivo_base(), 'w') as arquivo:
        arquivo.write('\n'.join(dados))

def criar_registro(tipo):
    data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    while True:
        try:
            valor = float(input(f'Informe o valor para o registro de {tipo}: '))
        except ValueError:
            print('Digite um número válido!')
        else:
            break

    dados = ler_arquivo()

    if not dados:
        next_id = 1
    else:
        next_id = int(loads(dados[-1])['id'])+1
    registro = {'id': next_id,
                'data': data,
                'tipo': tipo,
                'valor': valor if tipo.upper() != 'DESPESA' else -valor}

    if tipo.upper() == 'INVESTIMENTO':
        registro['taxa'] = investimento()

    registro = dumps(registro)
    caminho_base = arquivo_base()

    with open (caminho_base, 'a') as arquivo:
        arquivo.writelines(registro)
        arquivo.write('\n')

def corrige_registro():
    dados = ler_arquivo()
    if not dados:
        print("Não existem registros para atualizar.")
        return

    try:
        id_atualizar = int(input("Informe o ID do registro que deseja atualizar: "))
    except ValueError:
        print("ID inválido. Deve ser um número.")
        return

    registro_encontrado = False
    novos_dados = []

    for value in dados:
        registro = loads(value)
        if registro['id'] == id_atualizar:
            registro_encontrado = True
            print(f"Registro atual: Tipo: {registro['tipo']} - Valor: R${registro['valor']} - Data: {registro['data']}")

            novo_tipo = input(f"Informe o novo tipo (atual: {registro['tipo']}) ou deixe em branco para manter: ").strip()
            novo_valor = input(f"Informe o novo valor (atual: R${registro['valor']}) ou deixe em branco para manter: ").strip()

            alteracoes = []

            if novo_tipo:
                alteracoes.append(f"Tipo: {registro['tipo']} -> {novo_tipo}")
                registro['tipo'] = novo_tipo
            if novo_valor:
                alteracoes.append(f"Valor: R${registro['valor']} -> R${novo_valor}")
                registro['valor'] = novo_valor

            if alteracoes:
                data_atualizacao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                registro['data'] = data_atualizacao
                print("Registro atualizado com sucesso! Alterações feitas:")
                for alteracao in alteracoes:
                    print(alteracao)
                    print(f"Data da atualização: {data_atualizacao}")
            else:
                print("Nenhuma alteração foi feita!")

        novos_dados.append(dumps(registro))

    if not registro_encontrado:
        print(f"Registro com ID {id_atualizar} não encontrado.")
        return

    caminho_base = arquivo_base()
    with open(caminho_base, 'w') as arquivo:
        arquivo.write('\n'.join(novos_dados) + '\n')

def excluir_registro():
    dados = ler_arquivo()
    if not bool(dados):
        print('Não existem registros na base de dados')
        return
    while True:
        id_a_remover = input('Qual registro deseja excluir? ID: ')
        if id_a_remover.isdigit():
            id_existe = False
            for index, value in enumerate(dados):
                id = int(loads(value)['id'])
                if id == int(id_a_remover):
                    dados.pop(index)
                    id_existe = True
                    print('Registro removido com sucesso.')
                    with open(arquivo_base(), 'w') as arquivo:
                        arquivo.writelines(dados)
            if not id_existe:
                print('ID não existente na base.')
            else:
                break
        else:
            continuar = input('Input inválido!\nDeseja tentar novamente? S/N').upper().strip()
            match continuar:
                case 'S':
                    continue
                case 'N':
                    break
                case _:
                    print('Opção inválida. Voltando para o Menu Principal...\n')
                    break

def exibir_registros():
    arquivo_base()
    dados = ler_arquivo()
    if not bool(dados):
        print('Não existem registros na base de dados')
        return
    validador = False
    tipo = input('Qual tipo de registros deseja visualizar? Data, Tipo ou Valor? ').upper().strip()
    match tipo:
        case 'DATA':
            # Corrigindo busca por intervalo de datas
            data_inicial = input('Informe a data inicial (dd/mm/aaaa): ').strip()
            data_final = input('Informe a data final (dd/mm/aaaa): ').strip()

            # Convertendo as datas de string para objetos datetime e ajustando para incluir toda a data final
            data_inicial = datetime.strptime(data_inicial, '%d/%m/%Y')
            data_final = datetime.strptime(data_final, '%d/%m/%Y') + timedelta(days=1) - timedelta(seconds=1)

            # Lambda para verificar se a data está dentro do intervalo
            busca_por_data = lambda registro, data_inicial, data_final: \
                data_inicial <= datetime.strptime(registro['data'], '%d/%m/%Y %H:%M:%S') <= data_final

            for value in dados:
                value = loads(value)
                if busca_por_data(value, data_inicial, data_final):
                    output = f'ID: {value["id"]} - Data: {value["data"]} - Tipo: {value["tipo"]} - Valor: R${value["valor"]}'
                    if 'taxa' in value:
                        output = output + f' - Taxa: {value["taxa"]}%'
                    if 'montante_investimento' in value:
                        output = output + f' - Investimento Atualizado: R${value["montante_investimento"]}'
                    print(output)
                    validador = True
            if not validador:
                print('Nenhum registro encontrado para a data informada.')
        case 'TIPO':
            pesquisa_tipo = input('Qual o tipo de registro que deseja buscar? Receita, Despesa ou Investimento?').upper().strip()
            for value in dados:
                value = loads(value)
                if value['tipo'].upper() == pesquisa_tipo:
                    output = f'ID: {value["id"]} - Data: {value["data"]} - Tipo: {value["tipo"]} - Valor: R${value["valor"]}'
                    if 'taxa' in value:
                        output = output + f' - Taxa: {value["taxa"]}%'
                    if 'montante_investimento' in value:
                        output = output + f' - Investimento Atualizado: R${value["montante_investimento"]}'
                    print(output)
        case 'VALOR':
            pesquisa_valor = int(input('Qual o valor que deseja buscar? '))
            while True:
                tipo_pesquisa_valor = input(f'MaiorIgual (>=), MenorIgual (<=) ou Igual (==) à R${pesquisa_valor}? ')
                if tipo_pesquisa_valor not in ('>=', '<=', '=='):
                    print('Por favor, use as opções fornecidas dentro dos parentêses.')
                    continue
                break
            for value in dados:
                value = loads(value)
                if eval(f'{value["valor"]} {tipo_pesquisa_valor} {pesquisa_valor}'):
                    output = f'ID: {value["id"]} - Data: {value["data"]} - Tipo: {value["tipo"]} - Valor: R${value["valor"]}'
                    if 'taxa' in value:
                        output = output + f' - Taxa: {value["taxa"]}%'
                    if 'montante_investimento' in value:
                        output = output + f' - Investimento Atualizado: R${value["montante_investimento"]}'
                    print(output)

def agrupamento_mes():
    dados = ler_arquivo()
    if not bool(dados):
        print('Não existem registros na base de dados')
        return

    while True:
        try:
            mes_desejado = int(input('Qual mês de 2024 deseja visualizar? '))
            if not 0 < mes_desejado <= 12:
                raise ValueError
        except:
            print('Por favor, informe um mês válido no formato MM.')
        else:
            break

    def saida_valores(tipo, valores, mes_desejado):
        media = calcular_media(valores)
        if media is not None:
            print(f'A média de {tipo} para o mês {mes_desejado} é: R${media:.2f}')
        else:
            print(f'Não existem registros de {tipo} para o mês {mes_desejado}.')

    Group_By_Receitas = list()
    Group_By_Investimento = list()
    Group_By_Despesa = list()
    calcular_media = lambda lista: sum(lista) / len(lista) if len(lista) > 0 else None

    for registro in dados:
        registro = loads(registro)
        if int((registro['data'])[3:5]) == int(mes_desejado):
            match registro['tipo'].upper():
                case 'RECEITA':
                    Group_By_Receitas.append(registro['valor'])
                case 'INVESTIMENTO':
                    Group_By_Investimento.append(registro['valor'])
                case 'DESPESA':
                    Group_By_Despesa.append(registro['valor'])


    saida_valores('receitas', Group_By_Receitas, mes_desejado)
    saida_valores('investimentos', Group_By_Investimento, mes_desejado)
    saida_valores('despesas', Group_By_Despesa, mes_desejado)

# Função principal do sistema
def inicia_sistema():
    opcoes = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    estilo = (Fore.WHITE + Back.MAGENTA + Style.BRIGHT)
    nome_banco = '"NEW"BANK'

    print(estilo + '-' * 30)
    print(f'|{nome_banco:^28}|')
    print(f'-' * 30 + Style.RESET_ALL)
    print(
        """OPÇÕES:
1- Registrar Receita
2- Registrar Despesa
3- Realizar Investimento
4- Consultar Registros (Data, Tipo ou Valor)
5- Corrigir Registro
6- Deletar Registro
7- Atualizar Investimentos
8- Agrupamento por Mês

0- Sair do Programa
"""
    )

    while True:
        opcao = input('Informe qual opção deseja utilizar: ')
        if opcao.isdigit():
            opcao = int(opcao)
            if opcao not in opcoes:
                print('Opção INVÁLIDA. Digite novamente: ')
                continue
            else:
                print(estilo + '-' * 30)
                print('-' * 30 + Style.RESET_ALL)
                match opcao:
                    case 1:
                        print('NOVA RECEITA')
                        criar_registro('Receita')
                        print('Receita registrada com sucesso!')
                    case 2:
                        print('NOVA DESPESA')
                        criar_registro('Despesa')
                        print('Despesa registrada com sucesso!')
                    case 3:
                        print('NOVO INVESTIMENTO')
                        criar_registro('Investimento')
                        print('Investimento registrado com sucesso!')
                    case 4:
                        print('REGISTROS CADASTRADOS')
                        exibir_registros()
                    case 5:
                        print('CORRIGIR REGISTRO')
                        corrige_registro()
                        print('Atualização registrada com sucesso!')
                    case 6:
                        print('EXCLUIR REGISTRO')
                        excluir_registro()
                        print('Exclusão efetuada com sucesso!')
                    case 7:
                        print('ATUALIZAÇÃO DE INVESTIMENTOS')
                        atualizar_investimento()
                        print('Investimentos atualizados!')
                    case 8:
                        print('MÉDIA (R$) DE TIPO DE REGISTRO POR MÊS')
                        agrupamento_mes()
                    case 0:
                        print('Finalizando Programa. . .')
                        break
        else:
            print('Opção INVÁLIDA. Digite novamente: ')
    print('Programa finalizado!')

# Executar o sistema
inicia_sistema()