import re
from pathlib import Path
import pickle

import streamlit as st
import openai
from unidecode import unidecode

PASTA_MENSAGENS = Path(__file__).parent / 'mensagens'
PASTA_MENSAGENS.mkdir(exist_ok=True)
CACHE_DESCONVERTE = {}

openai_key = ''

def return_resposta_modelo(mensagens, openai_key,modelo='gpt-3.5-turbo',temperatura = 0, stream=False):
    openai.api_key = openai_key
    response = openai.ChatCompletion.create(model=modelo, messages=mensagens, temperature=temperatura, stream=stream)
    return response

def converte_nome_mensagem(nome_mensagem):
    nome_arquivo = unidecode(nome_mensagem)
    nome_arquivo = re.sub('\W+', '', nome_arquivo).lower()
    return nome_arquivo

def desconverte_nome_mensagem(nome_arquivo):
    if not nome_arquivo in CACHE_DESCONVERTE:
        nome_mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo, key='nome_mensagem')
        CACHE_DESCONVERTE[nome_arquivo] = nome_mensagem
    return CACHE_DESCONVERTE[nome_arquivo]

def retorna_nome_da_mensagem(mensagens):
    nome_mensagem = ''
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            nome_mensagem = mensagem['content'][:30]
            break
    return nome_mensagem

def salvar_mensagens(mensagens):
    if len(mensagens) == 0:
        return False
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    arquivo_salvar = {'nome_mensagem': nome_mensagem, 'nome_arquivo': nome_arquivo, 'mensagem': mensagens}
    with open(PASTA_MENSAGENS / nome_arquivo, 'wb') as f:
        pickle.dump(arquivo_salvar, f)

def ler_mensagem_por_nome_arquivo(nome_arquivo, key='mensagem'):
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]

def ler_mensagens(mensagens, key='mensagem'):
    if len(mensagens) == 0:
        return []
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]

def listar_conversas():
    conversas = list(PASTA_MENSAGENS.glob('*'))
    conversas = sorted(conversas, key=lambda item: item.stat().st_mtime_ns, reverse=True)
    return [c.stem for c in conversas]

def inicializacao():
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''

def main_page():
    mensagens = ler_mensagens(st.session_state['mensagens'])


    st.header('Genaro AI', divider=True)

    for mensagem in mensagens:
        chat = st.chat_message(mensagem['role'])
        chat.markdown(mensagem['content'])


    prompt = st.chat_input('Fale com o Genaro AI!')

    if prompt:
        nova_mensagem = {'role': 'user', 'content': prompt}
        chat = st.chat_message(nova_mensagem['role'])
        chat.markdown(nova_mensagem['content'])
        mensagens.append(nova_mensagem)

        chat = st.chat_message('assistant')
        placeholder = chat.empty()
        placeholder.markdown("▌")
        resposta_completa = ''

        
        respostas = return_resposta_modelo(mensagens,openai_key, stream=True)

        for resposta in respostas:
            resposta_completa += resposta.choices[0].delta.get('content', '')
            placeholder.markdown(resposta_completa + "▌")
        placeholder.markdown(resposta_completa)
        nova_mensagem = {'role': 'assistant', 'content': resposta_completa}
        mensagens.append(nova_mensagem)



        st.session_state['mensagens'] = mensagens
        salvar_mensagens(mensagens)

def tab_conversas(tab):
    tab.button('Comecar Nova conversa', on_click=seleciona_convera, args=('',), use_container_width=True)
    tab.markdown('')
    conversas = listar_conversas()
    for nome_arquivo in conversas:
        nome_mensagem = desconverte_nome_mensagem(nome_arquivo).capitalize()
        if len(nome_mensagem) == 30:
            nome_mensagem += '...'
        tab.button(nome_mensagem, on_click=seleciona_convera, args=(nome_arquivo,), disabled=nome_arquivo==st.session_state['conversa_atual'], use_container_width=True)

def seleciona_convera(nome_arquivo):
    if nome_arquivo == '':
        st.session_state.mensagens = []   
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo)
        st.session_state.mensagens = mensagem
    st.session_state['conversa_atual'] = nome_arquivo

def main():
    inicializacao()
    main_page()
    tab1, tab2 = st.sidebar.tabs(['Conversas', 'Configurações'])
    tab_conversas(tab1)

if __name__ == '__main__':
    main()

