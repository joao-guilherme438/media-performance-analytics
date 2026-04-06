import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Definição da classe principal para encapsular a lógica de análise
class AnalisadorMidia:
    """
    Classe responsável por gerenciar a conexão com o banco de dados,
    processar métricas de marketing e gerar visualizações de dados.
    """
    
    def __init__(self):
        # Nome do banco de dados SQLite (arquivo local)
        self.db_name = 'wpp_media_data.db'
        # Estabelece conexão com o banco de dados
        self.conn = sqlite3.connect(self.db_name)
        # Inicializa a estrutura do banco e insere dados iniciais
        self.configurar_banco()

    def configurar_banco(self):
        """Cria a tabela de campanhas e popula com dados fictícios de performance."""
        cursor = self.conn.cursor()
        
        # Garante que a tabela seja reiniciada a cada execução para evitar duplicatas
        cursor.execute("DROP TABLE IF EXISTS campanhas")
        
        # Schema da tabela: focado em métricas brutas de mídia
        cursor.execute("""
            CREATE TABLE campanhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_campanha TEXT,
                canal TEXT,
                impressoes INTEGER,
                cliques INTEGER,
                investimento REAL
            )
        """)
        
        # Dataset de exemplo simulando diferentes canais e volumes de tráfego
        dados = [
            ('Performance Search', 'Google Search', 120000, 4800, 3500.0),
            ('Brand Awareness', 'Instagram Ads', 180000, 2900, 2200.0),
            ('Remarketing App', 'Facebook Ads', 45000, 1500, 800.0),
            ('Vídeo Pre-Roll', 'YouTube Music', 250000, 950, 4000.0),
            ('Trend Engagement', 'TikTok Ads', 60000, 5800, 1500.0)
        ]
        
        # Inserção em lote (bulk insert) para melhor performance
        cursor.executemany("""
            INSERT INTO campanhas (nome_campanha, canal, impressoes, cliques, investimento) 
            VALUES (?, ?, ?, ?, ?)
        """, dados)
        
        self.conn.commit()

    def carregar_dados(self):
        """
        Extrai dados do SQL via Pandas e realiza o feature engineering 
        (criação de métricas calculadas).
        """
        # Lê a query SQL diretamente para um DataFrame do Pandas
        df = pd.read_sql_query("SELECT * FROM campanhas", self.conn)
        
        # Cálculo de CTR (Click-Through Rate): Eficácia do anúncio
        df['CTR (%)'] = (df['cliques'] / df['impressoes']) * 100
        
        # Cálculo de CPC (Custo por Clique): Eficiência financeira
        df['CPC (R$)'] = df['investimento'] / df['cliques']
        
        return df

    def gerar_grafico_pizza(self, df):
        """Gera gráfico de distribuição de investimento (Budget Allocation)."""
        plt.figure(figsize=(8, 6))
        
        # Criação do gráfico de pizza focado no investimento por canal
        plt.pie(df['investimento'], labels=df['canal'], autopct='%1.1f%%', 
                startangle=140, colors=['#4F81BD', '#C0504D', '#9BBB59', '#8064A2', '#4BACC6'])
        
        plt.title('Distribuição de Investimento por Canal')
        
        # Exporta o gráfico para imagem antes de exibir (bom para documentação)
        plt.savefig('grafico_investimento.png')
        print("\n✅ Gráfico 'grafico_investimento.png' gerado com sucesso!")
        plt.show()

    def gerar_grafico_barras(self, df):
        """Gera gráfico comparativo de CTR por canal."""
        # Ordenação dos dados para facilitar a leitura visual do ranking
        df_sorted = df.sort_values('CTR (%)')
        
        plt.figure(figsize=(10, 6))
        plt.barh(df_sorted['canal'], df_sorted['CTR (%)'], color='skyblue')
        
        plt.xlabel('Taxa de Clique (CTR %)')
        plt.title('Performance de Canais - Ranking de CTR')
        
        # Exporta a visualização para arquivo
        plt.savefig('grafico_performance.png')
        print("\n✅ Gráfico 'grafico_performance.png' gerado com sucesso!")
        plt.show()

def menu():
    """Interface de Linha de Comando (CLI) para interação com o usuário."""
    analisador = AnalisadorMidia()
    
    while True:
        print("\n" + "="*30)
        print("    WPP MEDIA ANALYTICS TOOL")
        print("="*30)
        print("1. Visualizar Tabela de Performance")
        print("2. Gerar Gráfico de Investimento (Pizza)")
        print("3. Gerar Gráfico de Performance (Barras)")
        print("4. Exportar para CSV")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")

        # Recarrega os dados a cada opção para garantir sincronia com o banco
        df = analisador.carregar_dados()

        if opcao == '1':
            # Exibe colunas específicas para não poluir o terminal
            print("\n", df[['canal', 'impressoes', 'cliques', 'CTR (%)', 'CPC (R$)']])
        elif opcao == '2':
            analisador.gerar_grafico_pizza(df)
        elif opcao == '3':
            analisador.gerar_grafico_barras(df)
        elif opcao == '4':
            # Exportação de dados para relatórios em Excel/BI
            df.to_csv('relatorio_wpp.csv', index=False)
            print("\n✅ Arquivo 'relatorio_wpp.csv' exportado com sucesso!")
        elif opcao == '0':
            print("Encerrando sistema... Boa sorte no processo seletivo!")
            break
        else:
            print("❌ Opção inválida! Tente novamente.")

# Ponto de entrada do script
if __name__ == "__main__":
    menu()