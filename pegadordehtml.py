import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import os
import logging

# Configuração do logging
logging.basicConfig(filename='site_downloader.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def salvar_codigo_fonte_completo(html, pasta, nome_arquivo='código_fonte_completo.html'):
    caminho_completo = os.path.join(pasta, nome_arquivo)
    with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(html)
    logging.info(f'Código fonte completo salvo em: {caminho_completo}')

def salvar_conteudo(url, pasta, tipo):
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            nome_arquivo = url.split('/')[-1]
            caminho_completo = os.path.join(pasta, tipo, nome_arquivo)
            with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(resposta.text)
            logging.info(f'{tipo.upper()} salvo: {url} -> {caminho_completo}')
    except Exception as e:
        logging.error(f'Erro ao baixar {tipo} de {url}: {e}')

def baixar_site(url_do_site, pasta_raiz):
    if not url_do_site or not pasta_raiz:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
        return
    logging.info(f'Iniciando download do site: {url_do_site}')
    for subpasta in ['html', 'css', 'js']:
        os.makedirs(os.path.join(pasta_raiz, subpasta), exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        resposta = requests.get(url_do_site, headers=headers)
        if resposta.status_code == 200:
            html_principal = resposta.text
            salvar_codigo_fonte_completo(html_principal, pasta_raiz)
            with open(os.path.join(pasta_raiz, 'html', 'index.html'), 'w', encoding='utf-8') as arquivo:
                arquivo.write(html_principal)

            soup = BeautifulSoup(html_principal, 'html.parser')
            for link in soup.find_all('link', {'rel': 'stylesheet'}):
                url_css = link['href']
                salvar_conteudo(url_css, pasta_raiz, 'css')
            for script in soup.find_all('script', {'src': True}):
                url_js = script['src']
                salvar_conteudo(url_js, pasta_raiz, 'js')

            messagebox.showinfo("Sucesso", "Site baixado com sucesso!")
            logging.info(f'Site {url_do_site} baixado com sucesso.')
        else:
            messagebox.showerror("Erro", f"Erro ao acessar o site: {resposta.status_code}")
            logging.error(f'Erro ao acessar o site {url_do_site}: {resposta.status_code}')
    except Exception as e:
        messagebox.showerror("Erro", str(e))
        logging.error(f'Erro ao baixar o site {url_do_site}: {e}')

def iniciar_download():
    url = entry_url.get()
    pasta_raiz = entry_pasta.get()
    threading.Thread(target=baixar_site, args=(url, pasta_raiz)).start()

def selecionar_pasta():
    pasta_selecionada = filedialog.askdirectory()
    entry_pasta.delete(0, tk.END)
    entry_pasta.insert(0, pasta_selecionada)

root = tk.Tk()
root.title("Baixador de Sites Futurista")

style = ttk.Style()
style.theme_use('clam')

style.configure('TButton', foreground='blue', background='black', font=('Helvetica', 10, 'bold'))
style.configure('TLabel', foreground='blue', background='black', font=('Helvetica', 12, 'bold'))
style.configure('TEntry', foreground='blue', background='black', font=('Helvetica', 10, 'normal'))

root.configure(bg='black')

label_url = ttk.Label(root, text="URL do Site:", background='black', foreground='light blue')
label_url.pack(pady=(10,0))

entry_url = ttk.Entry(root, width=50)
entry_url.pack(pady=(0,10))

label_pasta = ttk.Label(root, text="Pasta de Destino:", background='black', foreground='light blue')
label_pasta.pack(pady=(10,0))

entry_pasta = ttk.Entry(root, width=50)
entry_pasta.pack(pady=(0,10))

botao_pasta = ttk.Button(root, text="Selecionar Pasta", command=selecionar_pasta)
botao_pasta.pack(pady=(0,10))

botao_baixar = ttk.Button(root, text="Baixar Site", command=iniciar_download)
botao_baixar.pack(pady=(10,0))

root.mainloop()
