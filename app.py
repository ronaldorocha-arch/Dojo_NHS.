import streamlit as st
import pandas as pd
import io

# Configuração da página
st.set_page_config(page_title="DOJO - Inserção Manual", layout="wide")
st.title("📝 Dashboard DOJO - Preenchimento Manual")

st.markdown("""
**⚠️ ATENÇÃO:** O aplicativo não salva seus dados sozinho quando você fecha o site! 
**Sempre faça o download da planilha no final do preenchimento.** Na semana seguinte, basta enviar a planilha baixada para continuar de onde parou.
""")

# --- 1. UPLOAD PARA CONTINUAR DE ONDE PAROU ---
st.markdown("---")
uploaded_file = st.file_uploader("Para continuar, envie a planilha da última semana (ou ignore para começar uma tabela do zero):", type=['xlsx'])

# --- 2. ESTRUTURA INICIAL DA TABELA ---
if 'dados_iniciais' not in st.session_state or uploaded_file is not None:
    if uploaded_file is not None:
        try:
            st.session_state['dados_iniciais'] = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
    else:
        # Tabela em branco inicial (você pode alterar os nomes de amostra aqui no código se quiser)
        st.session_state['dados_iniciais'] = pd.DataFrame({
            "Nome": ["João", "Maria", ""],
            "1° AMOSTRA": [0.0, 0.0, 0.0],
            "2° AMOSTRA": [0.0, 0.0, 0.0],
            "3° AMOSTRA": [0.0, 0.0, 0.0],
            "4° AMOSTRA": [0.0, 0.0, 0.0],
            "5° AMOSTRA": [0.0, 0.0, 0.0]
        })

st.markdown("---")
st.subheader("⌨️ Tabela de Dados (Digite aqui)")
st.info("Dica: Clique dentro de qualquer célula para digitar. Para adicionar uma nova pessoa, clique na linha vazia no final da tabela.")

# Esta é a função que cria um "Excel" dentro do próprio site
dados_editados = st.data_editor(
    st.session_state['dados_iniciais'],
    num_rows="dynamic", # Permite adicionar e apagar linhas
    use_container_width=True
)

# --- 3. GRÁFICO AUTOMÁTICO ---
st.markdown("---")
st.subheader("📊 Gráfico Automático")

if "Nome" in dados_editados.columns:
    pessoas = dados_editados["Nome"].replace("", pd.NA).dropna().unique()
    pessoas_selecionadas = st.multiselect(
        "Selecione quem deseja comparar no gráfico:", 
        options=pessoas, 
        default=pessoas[:3] if len(pessoas) >= 3 else pessoas
    )
    
    if len(pessoas_selecionadas) > 0:
        df_filtrado = dados_editados[dados_editados["Nome"].isin(pessoas_selecionadas)].copy()
        colunas_amostras = [col for col in df_filtrado.columns if "AMOSTRA" in str(col).upper()]
        
        for col in colunas_amostras:
            df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')
            
        df_grafico = df_filtrado[["Nome"] + colunas_amostras].set_index("Nome").T
        st.line_chart(df_grafico)
    else:
        st.warning("Selecione alguém para ver o gráfico.")

# --- 4. DOWNLOAD PARA NÃO PERDER ---
st.markdown("---")
st.subheader("💾 Salvar Trabalho")
st.warning("Não esqueça de clicar no botão abaixo antes de sair!")

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    dados_editados.to_excel(writer, index=False, sheet_name='Tempos DOJO')

st.download_button(
    label="📥 BAIXAR PLANILHA ATUALIZADA",
    data=buffer.getvalue(),
    file_name="TEMPOS_DOJO_ATUALIZADO.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
