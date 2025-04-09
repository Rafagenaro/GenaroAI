import streamlit as st
import openai

openai_key = ''

def return_resposta_modelo(mensagens, openai_key,modelo='gpt-3.5-turbo',temperatura = 0, stream=False):
    openai.api_key = openai_key
    response = openai.ChatCompletion.create(model=modelo, messages=mensagens, temperature=temperatura, stream=stream)
    return response

def main_page():

    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []

    mensagens = st.session_state['mensagens']


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

main_page()