import pandas as pd
import yagmail as ya
from sqlalchemy import create_engine
from fpdf import FPDF
from datetime import datetime

print("Conectando ao banco via SQLAlchemy...")

#Envio de email
#usuario = 'luucassmartiins@gmail.com'
#senha = 'jpbp cyzn nrxo xyhf'

#Criando o objeto do yagmail
#ya = ya.SMTP(user=usuario, password=senha)

def gerar_relatorio_pedidos(data_inicio, data_final):
    try:
        # Cria a engine de conexão
        engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/classicmodels')   

        query = f"""
        SELECT        
          ROW_NUMBER() OVER (ORDER BY o.orderDate DESC) AS "Nº", 
          REPLACE(o.orderNumber, '.', '') AS "Numero do pedido", 
          c.customerName AS "Nome do cliente", 
          o.orderDate AS "Data do pedido", 
          SUM(od.quantityOrdered * od.priceEach) AS "Total do pedido", 
          CASE
              WHEN o.status = 'In Process' THEN "Em processamento"
              WHEN o.status = 'Disputed' THEN "Disputado"
              WHEN o.status = 'On Hold' THEN "Em espera"
              WHEN o.status = 'Resolved' THEN "Resolvido"
              WHEN o.status = 'Shipped' THEN "Enviado"
            ELSE "Nenhum valor vinculado" END AS "Status do Pedido" 
        FROM 
          customers c 
              INNER JOIN orders o ON c.customerNumber = o.customerNumber 
              INNER JOIN orderdetails od ON o.orderNumber = od.orderNumber 
        WHERE 
          o.orderDate >= '{data_inicio}' 
          AND o.orderDate <= '{data_final}' 
        GROUP BY 
          c.customerName, 
          o.orderNumber, 
          o.orderDate 
        ORDER BY 
          o.orderDate ASC 
        LIMIT 
          120;

        """

        # Usa a engine para ler o SQL
        df = pd.read_sql(query, engine)
        #df.insert(0, "Nº", range(1, len(df) + 1))

        print("\n📊 Resultado da consulta:\n")
        print(df)

        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"data_inicio": data_inicio, "data_final": data_final})

        # Geração do PDF
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 12)
                self.cell(0, 10, "Relatório de Pedidos", border=False, ln=True, align="C")
                self.cell(0, 10, periodo_texto, border=False, ln=True, align="C")
                self.image("logo_globex.png", x=10, y=8, w=30)  # x, y, largura em mm
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        pdf = PDF(orientation="L")
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        total_geral = df["Total do pedido"].sum()

        col_widths = [30, 35, 70, 30, 30, 40]
        col_names = list(df.columns)

        # Função para imprimir o cabeçalho da tabela
        def imprimir_cabecalho_tabela():
            pdf.set_font("Arial", "B", 10)
            for i, col in enumerate(col_names):
                pdf.cell(col_widths[i], 10, col, border=1)
            pdf.ln()
            pdf.set_font("Arial", size=10)

        if df.empty:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 20, "Nenhum resultado encontrado para o filtro informado.", 0, 1, "C")
        else:

            # Imprime o cabeçalho pela primeira vez
            imprimir_cabecalho_tabela()

        # Loop para imprimir as linhas da tabela
        for index, row in df.iterrows():
            # Verifica se está perto do final da página, imprime nova página e cabeçalho
            if pdf.get_y() > pdf.page_break_trigger - 15:
                pdf.add_page()
                imprimir_cabecalho_tabela()

            pdf.cell(col_widths[0], 8, str(row.iloc[0]), border=1)
            pdf.cell(col_widths[1], 8, str(row.iloc[1]), border=1)
            pdf.cell(col_widths[2], 8, str(row.iloc[2])[:35], border=1)  # Truncar nomes longos
            # Garante que o valor seja datetime, mesmo se vier como string
            data_pedido = pd.to_datetime(row.iloc[3])
            pdf.cell(col_widths[3], 8, data_pedido.strftime('%d/%m/%Y'), border=1)
            #pdf.cell(col_widths[3], 8, str(row.iloc[3]).strftime('%d/%m/%Y'), border=1)        

            valor_formatado = f"{row.iloc[4]:,.2f}".replace(",", "").replace(".", ",")
            pdf.cell(col_widths[4], 8, f"R$ {valor_formatado}", border=1, align="R")
            pdf.cell(col_widths[5], 8, str(row.iloc[5]), border=1)
            pdf.ln()

        # Espaço antes do total geral
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)

        # Linha de total geral (células unidas até a última coluna)
        pdf.cell(sum(col_widths[:-1]), 8, "TOTAL GERAL:", border=1, align="R")
        valor_formatado_total = f"{total_geral:,.2f}".replace(",", "").replace(".", ",")
        pdf.cell(col_widths[-1], 8, f"R$ {valor_formatado_total}", border=1, align="R")

        # Salva o PDF
        pdf.output(r"C:\Users\Lucas\Desktop\estudo de python\relatorio_pedidos.pdf")
        print("\n✅ PDF gerado com sucesso: relatorio_pedidos.pdf, verifique o arquivo na pasta 'estudo de python'")
        #print("\n✅ Aguarde, estamos enviando por e-mail o relatorio!")

        #Destinatário
        destinatario = 'lucas.lsmcd@gmail.com'
        assunto = 'Relatório de Pedidos Diário'
        corpo = 'Olá, segue em anexo o relatório de pedidos gerados diariamente dentro do BD via python!'

        #Caminho do arquivo
        arquivo_pdf = r"C:\Users\Lucas\Desktop\estudo de python\relatorio_pedidos.pdf"

        #Envio do e-mail
      # ya.send(
      #      to=destinatario,
      #      subject=assunto,
      #      contents=corpo,
      #     attachments=arquivo_pdf

      #  )

      # print("\n✅Email enviado com sucesso!")

    except Exception as e:
        print("❌ Erro:", e)

def gerar_relatorio_produtos(status):
    try:
        # Cria a engine de conexão
        engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/classicmodels')   

        query = f"""
        SELECT
            ROW_NUMBER() OVER (ORDER BY t0.productCode DESC) AS "Nº",
            t0.productCode AS "Código do Produto", 
            t0.productName AS "Nome do Produto", 
            t0.productLine AS "Linha do produto", 
            t0.quantityInStock AS "Quantidade em Estoque" 
        FROM 
            products t0 
        WHERE 
            t0.`Status` = '{status}';
        """

        # Usa a engine para ler o SQL
        df = pd.read_sql(query, engine)
        #df.insert(0, "Nº", range(1, len(df) + 1))

        print("\n📊 Resultado da consulta:\n")
        print(df)

        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"status": status})

        # Geração do PDF
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 12)
                self.cell(0, 10, "Relatório de Produtos", border=False, ln=True, align="C")
                self.cell(0, 10, status_texto, border=False, ln=True, align="C")
                self.image("logo_globex.png", x=10, y=8, w=30)  # x, y, largura em mm
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        pdf = PDF(orientation="L")
        pdf.add_page()
        pdf.set_font("Arial", size=10)        

        col_widths = [30, 35, 70, 35, 45]
        col_names = list(df.columns)

        # Função para imprimir o cabeçalho da tabela
        def imprimir_cabecalho_tabela():
            pdf.set_font("Arial", "B", 10)
            for i, col in enumerate(col_names):
                pdf.cell(col_widths[i], 10, col, border=1)
            pdf.ln()
            pdf.set_font("Arial", size=10)

        if df.empty:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 20, "Nenhum resultado encontrado para o filtro informado.", 0, 1, "C")
        else:

            # Imprime o cabeçalho pela primeira vez
            imprimir_cabecalho_tabela()

        # Loop para imprimir as linhas da tabela
        for index, row in df.iterrows():
            # Verifica se está perto do final da página, imprime nova página e cabeçalho
            if pdf.get_y() > pdf.page_break_trigger - 15:
                pdf.add_page()
                imprimir_cabecalho_tabela()

            pdf.cell(col_widths[0], 8, str(row.iloc[0]), border=1)
            pdf.cell(col_widths[1], 8, str(row.iloc[1]), border=1)
            pdf.cell(col_widths[2], 8, str(row.iloc[2])[:35], border=1)  # Truncar nomes longos         
            pdf.cell(col_widths[3], 8, str(row.iloc[3]), border=1)
            pdf.cell(col_widths[4], 8, str(row.iloc[4]), border=1)
            pdf.ln()

        # Espaço antes do total geral
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        

        # Salva o PDF
        pdf.output(r"C:\Users\Lucas\Desktop\estudo de python\relatorio_produtos.pdf")
        print("\n✅ PDF gerado com sucesso: relatorio_produtos.pdf, verifique o arquivo na pasta 'estudo de python'")
        #print("\n✅ Aguarde, estamos enviando por e-mail o relatorio!")

        #Destinatário
        destinatario = 'lucas.lsmcd@gmail.com'
        assunto = 'Relatório de Pedidos Diário'
        corpo = 'Olá, segue em anexo o relatório de pedidos gerados diariamente dentro do BD via python!'

        #Caminho do arquivo
        arquivo_pdf = r"C:\Users\Lucas\Desktop\estudo de python\relatorio_pedidos.pdf"

        #Envio do e-mail
      # ya.send(
      #      to=destinatario,
      #      subject=assunto,
      #      contents=corpo,
      #     attachments=arquivo_pdf

      #  )

      # print("\n✅Email enviado com sucesso!")

    except Exception as e:
        print("❌ Erro:", e)

print("=== Gerador de Relatórios ===")
print("1 - Relatório de Pedidos")
print("2 - Relatório de Produtos")
opcao = input("Escolha o relatório a ser gerado: ")

if opcao == "1":

    data_inicio = input("Digite a data inicial (AAAA-MM-DD): ")
    data_final = input("Digite a data final (AAAA-MM-DD): ")
    periodo_texto = f"Período: {data_inicio} até {data_final}"

    # Supondo que data_inicio e data_final são strings no formato 'YYYY-MM-DD'
    data_inicio_formatada = datetime.strptime(data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y")
    data_final_formatada = datetime.strptime(data_final, "%Y-%m-%d").strftime("%d/%m/%Y")    


    # Chama função ou bloco do relatório 1
    gerar_relatorio_pedidos(data_inicio, data_final)

elif opcao == "2":
    
    status = input("Digite o status do produto (1 - Ativo/0 - Inativo): ")
    if status == "0":
        status_texto = f"Status: {status} - Inativo"
    else:
        status_texto = f"Status: {status} - Ativo"

    gerar_relatorio_produtos(status)

else:
    print("❌ Opção inválida. Encerrando...")    


input("\nPressione Enter para sair...")
