import os
import time
import threading
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import Tk, Label, Entry, Button, filedialog, Text, END, messagebox

# Função para registrar mensagens de log na interface gráfica
def log_message(text_widget, message):
    text_widget.insert(END, f"{message}\n")
    text_widget.see(END)

# Função para realizar o login automatizado no site da ANS
def login(driver, username, password, status_text):
    try:
        driver.get("https://www.ans.gov.br/index.php/component/centralderelatorio/?view=login")
        
        # Aumenta o tempo de espera para garantir que os elementos estejam carregados
        login_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[9]/div/div/div[2]/form/div[1]/div/input'))
        )
        login_input.send_keys(username)

        password_input = driver.find_element(By.XPATH, '/html/body/div[9]/div/div/div[2]/form/div[2]/div[1]/input')
        password_input.send_keys(password)

        # Espera o botão de login estar clicável
        enter_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div/div/div[2]/form/div[2]/button'))
        )
        enter_button.click()

        log_message(status_text, "Login realizado com sucesso.")
        time.sleep(8)  # Pausa para garantir que o login seja processado

        return True
    except Exception as e:
        log_message(status_text, f"Erro durante o login: {e}")
        return False

# Função para navegar até a seção financeira e selecionar relatórios detalhados
def navigate_to_finance_section(driver, status_text):
    try:
        # Aguarda o link do 'Financeiro' estar visível e clicável
        accordion_link = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="accordion"]/div[2]/div[1]/h3/a'))
        )
        
        # Faz scroll até o elemento, caso esteja fora da área visível
        driver.execute_script("arguments[0].scrollIntoView();", accordion_link)
        
        time.sleep(1)  # Pausa curta para garantir o carregamento correto

        # Tenta clicar no link via JavaScript se o clique padrão falhar
        driver.execute_script("arguments[0].click();", accordion_link)
        log_message(status_text, "Clicando no link 'Financeiro'.")
        
        detalhado_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="radio1_1_2"]'))
        )
        detalhado_button.click()
        time.sleep(2)

        log_message(status_text, "Selecionando o botão 'Detalhado'.")

        return True
    except Exception as e:
        log_message(status_text, f"Erro ao acessar a seção financeira: {e}")
        return False

# Função para aguardar o download ser concluído
def wait_for_download(timeout=60):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        seconds += 1
    return seconds

# Função para baixar relatórios ABI com base nas datas fornecidas
def download_abi_reports(driver, dates_and_options, download_folder, status_text):
    for date, option_xpath in dates_and_options:
        try:
            # Primeiro, clique no botão "Próximo"
            next_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="aba1_1_conteudo"]/form/div[2]/div/a'))
            )
            next_button.click()

            time.sleep(2)  # Aguarda a lista suspensa abrir

            # Primeiro, clique no campo de input para abrir o dropdown
            input_field = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/div/input'))
            )
            input_field.click()  # Abre o dropdown
            input_field.clear()  # Limpa o campo antes de digitar
            input_field.send_keys(date)

            log_message(status_text, f"Digitando a data: {date}")

            time.sleep(2)  # Pausa para aguardar a digitação ser reconhecida

            # Aguarda o valor do dropdown estar clicável
            drop_down_value = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )

            # Faz scroll até o elemento caso esteja fora da tela
            driver.execute_script("arguments[0].scrollIntoView();", drop_down_value)
            drop_down_value.click()

            log_message(status_text, f"Selecionando a opção correspondente para: {date}")

            time.sleep(2)  # Pausa para aguardar a seleção

            generate_report_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="aba1_1_conteudo"]/form/div[3]'))
            )
            generate_report_button.click()

            log_message(status_text, f"Gerando relatório para: {date}")

            wait_time = wait_for_download()
            log_message(status_text, f"Download concluído para {date} em {wait_time} segundos.")

            time.sleep(5)
        except Exception as e:
            log_message(status_text, f"Erro durante o processamento da data {date}: {str(e)}")

# Função para selecionar o diretório de download usando tkinter
def select_download_directory():
    folder_selected = filedialog.askdirectory(title="Selecione a pasta para salvar os relatórios")
    return folder_selected

# Função principal que integra tudo
def start_download_process(username, password, download_folder, status_text):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa em modo headless
    chrome_options.add_argument("--disable-gpu")  # Desativa GPU
    chrome_options.add_argument("--no-sandbox")  # Necessário em alguns ambientes   

    # Configurando o diretório de download
    prefs = {
        "download.default_directory": os.path.abspath(download_folder),  # Define a pasta de download absoluta
        "download.prompt_for_download": False,  # Desabilita o prompt de download
        "download.directory_upgrade": True,  # Permite upgrade do diretório de download
        "safebrowsing.enabled": False,  # Desabilita verificações de segurança que podem bloquear downloads
        "profile.default_content_settings.popups": 0,  # Garante que não aparecerão popups de download
    }
    
    # Aplica as preferências de download
    chrome_options.add_experimental_option("prefs", prefs)

    # Inicializa o WebDriver com as opções configuradas
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        log_message(status_text, f"Diretório de download definido para: {download_folder}")

        # Realiza o login
        if not login(driver, username, password, status_text):
            log_message(status_text, "Processo encerrado devido a falha no login.")
            return

        # Navega para a seção financeira e seleciona "Detalhado"
        if not navigate_to_finance_section(driver, status_text):
            log_message(status_text, "Processo encerrado devido a falha na navegação.")
            return

        # Lista de datas e XPaths das opções de ABI
        dates_and_options = [
    ('24/06/24 - 98°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/03/24 - 97°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('11/12/23 - 96°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/09/23 - 95°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/06/23 - 94°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('27/03/23 - 93°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('12/12/22 - 92°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/09/22 - 91º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('27/06/22 - 90°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('28/03/22 - 89°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('13/12/21 - 88°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('27/09/21 - 87°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('28/06/21 - 86°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('29/03/21 - 85°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('14/12/20 - 84°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('03/11/20 - 83°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('31/08/20 - 82°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/05/20 - 81°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('02/03/20 - 80°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('23/12/19 - 79°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('29/10/19 - 78°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/08/19 - 77°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('24/06/19 - 76°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('29/04/19 - 75°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/02/19 - 74°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/11/18 - 73°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('24/09/18 - 72°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('27/08/18 - 71°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/06/18 - 70°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('28/05/18 - 69°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/03/18 - 68°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/02/18 - 67°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/12/17 - 66°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('27/11/17 - 65°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/09/17 - 64°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('28/08/17 - 63°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('03/07/17 - 62°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('05/06/17 - 61°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('02/05/17 - 60°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('06/03/17 - 59°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('21/11/16 - 58°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('08/08/16 - 57º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/04/16 - 56º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('14/12/15 - 55º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('20/05/15 - 54º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('29/12/14 - 53º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('30/10/14 - 52º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('15/09/14 - 51º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('17/07/14 - 50º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('29/05/14 - 49º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('18/03/14 - 48º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('16/12/13 - 47°', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('25/09/13 - 46º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('06/08/13 - 45º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('17/06/13 - 44º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('26/04/13 - 43º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('27/02/13 - 42º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('21/12/12 - 41º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('16/11/12 - 40º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('05/10/12 - 39º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('23/08/12 - 38º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('04/06/12 - 37º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('02/02/12 - 36º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('12/12/11 - 35º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('17/11/11 - 34º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('02/08/11 - 33º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('11/07/11 - 32º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('15/06/11 - 31º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('06/05/11 - 30º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('28/01/11 - 29º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('16/12/10 - 28º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('10/12/10 - 27º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('24/11/10 - 26º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('08/11/10 - 25º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('20/08/10 - 24º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('14/06/10 - 23º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('12/03/08 - 22º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('10/09/07 - 21º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('18/01/07 - 20º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('05/04/06 - 19º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('30/01/06 - 18º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('02/12/05 - 17º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('21/09/05 - 16º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('22/07/05 - 15º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('18/03/05 - 14º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('15/12/04 - 13º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('19/07/04 - 12º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('17/05/04 - 11º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('12/02/04 - 10º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('01/05/03 - 9º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('21/03/03 - 8º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('20/03/03 - Reemissão RE 05', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('06/01/03 - 7º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('01/08/02 - 6º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('03/05/02 - 5º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('01/02/02 - 4º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('30/11/01 - 3º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('10/09/01 - 2º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
    ('31/05/01 - 1º', '//*[@id="aba1_1_conteudo"]/form/div[2]/div/div/ul/li[1]'),
]

        # Realiza o download dos relatórios ABI
        download_abi_reports(driver, dates_and_options, download_folder, status_text)

    finally:
        driver.quit()
        log_message(status_text, "Processo concluído!")

# Função chamada ao clicar no botão de iniciar
def on_start_button_click(username_entry, password_entry, download_folder, status_text):
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Erro", "Por favor, preencha o usuário e a senha.")
        return

    if not download_folder.get():
        messagebox.showerror("Erro", "Por favor, selecione um diretório de download.")
        return

    # Executa o processo de download em uma thread separada para evitar congelamento da interface
    threading.Thread(target=start_download_process, args=(username, password, download_folder.get(), status_text)).start()

# Função chamada ao clicar no botão de escolher diretório
def on_select_folder_button_click(download_folder):
    folder = select_download_directory()
    download_folder.delete(0, END)  # Limpa o campo antes de inserir o novo caminho
    download_folder.insert(0, folder)  # Insere o diretório selecionado no campo de texto

# Função para configurar a interface gráfica
def setup_gui():
    root = Tk()
    root.title("RPA - Relatórios financeiros ANS")
    font = ('Helvetica', 10)  # Define a fonte padrão

    # Labels e Entradas para o login e senha
    Label(root, text="Usuário:", font=font).grid(row=0, column=0, padx=5, pady=5)
    username_entry = Entry(root, font=font)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    Label(root, text="Senha:", font=font).grid(row=1, column=0, padx=5, pady=5)
    password_entry = Entry(root, show="*", font=font)
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Botão para escolher o diretório de download
    download_folder = Entry(root, width=40, font=font)
    download_folder.grid(row=2, column=1, padx=5, pady=5)

    Button(root, text="Selecionar Diretório", font=font, command=lambda: on_select_folder_button_click(download_folder)).grid(row=2, column=0, padx=5, pady=5)

    # Text widget para status
    status_text = Text(root, height=10, width=50, font=('Helvetica', 10))
    status_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    # Botão para iniciar o processo de download
    start_button = Button(root, text="Iniciar Download", font=font, command=lambda: on_start_button_click(username_entry, password_entry, download_folder, status_text))
    start_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Adicionando Créditos
    Label(root, text="Feito por Lucas Viana Ribeiro", fg="blue", font=font).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    Label(root, text="GitHub: https://github.com/Lucasvrib", fg="blue", font=font).grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
