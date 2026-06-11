import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Comparativo de Tempos DOJO", layout="wide")

st.title("📈 Dashboard Comparativo - Tempos DOJO")
st.markdown("Faça o upload do arquivo de dados para gerar os gráficos de linha comparativos.")

# Componente para upload de arquivo
uploaded_file = st.file_uploader("Envie a planilha (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Lendo o arquivo (suporta tanto CSV quanto Excel)
    try:
        if uploaded_file.name.endswith('.csv'):
            # Ignorando linhas vazias no início se houver
            df = pd.read_csv(uploaded_file, skip_blank_lines=True) 
        else:
            df = pd.read_excel(uploaded_file)
            
        # Limpar espaços em branco nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        st.success("Arquivo carregado com sucesso!")
        
        # Verifica se existe a coluna 'Nome'
        if 'Nome' in df.columns:
            # Lista de pessoas
            lista_pessoas = df['Nome'].dropna().unique()
            
            # Filtro interativo para o usuário escolher quem quer comparar
            pessoas_selecionadas = st.multiselect(
                "Selecione as pessoas para comparar as amostras:",
                options=lista_pessoas,
                default=lista_pessoas[:3] # Seleciona os 3 primeiros por padrão
            )
            
            if pessoas_selecionadas:
                # Filtrar o DataFrame
                df_filtrado = df[df['Nome'].isin(pessoas_selecionadas)]
                
                # Pegar apenas as colunas de amostras (ignorando 'MÉDIA', etc)
                colunas_amostras = [col for col in df.columns if 'AMOSTRA' in str(col).upper()]
                
                # Reorganizar os dados para o gráfico de linha do Streamlit
                # O índice vira as amostras, e as colunas viram os nomes das pessoas
                df_grafico = df_filtrado[['Nome'] + colunas_amostras].set_index('Nome').T
                
                st.subheader("Gráfico Comparativo de Desempenho")
                # Gráfico de linha nativo do Streamlit (X = Amostras, Y = Tempos, Linhas = Pessoas)
                st.line_chart(df_grafico)
                
                st.subheader("Tabela de Dados Filtrada")
                st.dataframe(df_filtrado[['Nome'] + colunas_amostras + (['MÉDIA'] if 'MÉDIA' in df.columns else [])])
            else:
                st.warning("Por favor, selecione pelo menos uma pessoa para gerar o gráfico.")
                
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
