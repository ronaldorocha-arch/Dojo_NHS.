import streamlit as st
import pandas as pd
import io

# Configuração da página
st.set_page_config(page_title="Comparativo de Tempos DOJO", layout="wide")

st.title("📈 Dashboard Comparativo - Tempos DOJO")
st.markdown("Faça o upload do arquivo de dados para gerar gráficos e adicionar novos registros.")

# Upload de arquivo
uploaded_file = st.file_uploader("Envie a planilha (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Lendo o arquivo e guardando na memória
    if 'dados' not in st.session_state:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, skip_blank_lines=True) 
            else:
                df = pd.read_excel(uploaded_file)
            
            # --- CAÇADOR DE CABEÇALHO ---
            # Se as colunas estiverem sem nome (Unnamed), procuramos onde está o cabeçalho real
            if any("Unnamed" in str(col) for col in df.columns):
                for i, row in df.head(15).iterrows(): # Olha as primeiras 15 linhas
                    valores_linha = [str(val).strip().upper() for val in row.values]
                    if 'NOME' in valores_linha:
                        # Achou a linha com o nome! Define ela como as colunas do arquivo
                        df.columns = row.values
                        # Corta o arquivo para começar só a partir dessa linha
                        df = df.iloc[i+1:].reset_index(drop=True)
                        break
            
            # Limpa o nome das colunas e remove linhas 100% vazias
            df.columns = df.columns.astype(str).str.strip()
            df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
            
            st.session_state['dados'] = df
            
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

    if 'dados' in st.session_state:
        df_atual = st.session_state['dados']
        
        st.success("Arquivo carregado e cabeçalhos localizados com sucesso!")
        
        # Procura a coluna 'Nome' ignorando se está maiúsculo ou minúsculo
        colunas_upper = [str(c).upper() for c in df_atual.columns]
        
        if 'NOME' in colunas_upper:
            # Encontra qual é o nome exato da coluna na planilha original
            nome_coluna_real = df_atual.columns[colunas_upper.index('NOME')]
            
            # --- SEÇÃO DE GRÁFICOS ---
            st.markdown("---")
            st.subheader("📊 Análise de Desempenho")
            
            lista_pessoas = df_atual[nome_coluna_real].dropna().unique()
            pessoas_selecionadas = st.multiselect(
                "Selecione as pessoas para comparar:",
                options=lista_pessoas,
                default=lista_pessoas[:3] if len(lista_pessoas) >= 3 else lista_pessoas
            )
            
            colunas_amostras = [col for col in df_atual.columns if 'AMOSTRA' in str(col).upper()]
            
            if pessoas_selecionadas:
                df_filtrado = df_atual[df_atual[nome_coluna_real].isin(pessoas_selecionadas)]
                # Converte os tempos para número caso o Excel tenha mandado como texto
                for col in colunas_amostras:
                    df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')
                
                df_grafico = df_filtrado[[nome_coluna_real] + colunas_amostras].set_index(nome_coluna_real).T
                st.line_chart(df_grafico)
            else:
                st.warning("Selecione pelo menos uma pessoa para gerar o gráfico.")

            # --- SEÇÃO PARA INSERIR NOVOS DADOS ---
            st.markdown("---")
            st.subheader("➕ Adicionar Novo Avaliado")
            
            with st.form("form_novos_dados", clear_on_submit=True):
                novo_nome = st.text_input("Nome completo do avaliado:")
                
                st.write("Insira os tempos (use ponto para decimais, ex: 12.5):")
                cols = st.columns(5) 
                
                novos_valores = {}
                for i, col_name in enumerate(colunas_amostras):
                    with cols[i % 5]:
                        novos_valores[col_name] = st.number_input(col_name, min_value=0.0, step=0.1)
                
                enviou = st.form_submit_button("Salvar Novos Dados")
                
                if enviou:
                    if novo_nome == "":
                        st.error("Por favor, preencha o Nome!")
                    else:
                        nova_linha = {nome_coluna_real: novo_nome}
                        nova_linha.update(novos_valores)
                        df_nova_linha = pd.DataFrame([nova_linha])
                        
                        st.session_state['dados'] = pd.concat([df_atual, df_nova_linha], ignore_index=True)
                        st.success(f"Dados de {novo_nome} adicionados com sucesso! Atualize a página para ver no gráfico.")
                        st.rerun()

            # --- VISUALIZAÇÃO E DOWNLOAD ---
            st.markdown("---")
            st.subheader("📁 Tabela Completa Atualizada")
            st.dataframe(st.session_state['dados'])
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                st.session_state['dados'].to_excel(writer, index=False, sheet_name='Tempos Atualizados')
            
            st.download_button(
                label="📥 Baixar Planilha Atualizada (Excel)",
                data=buffer.getvalue(),
                file_name="Tempos_DOJO_Atualizado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Ainda não encontrei a coluna 'Nome'. Tem certeza que ela existe nessa planilha?")
