# Automação de Download de Relatórios de Acompanhamento Financeiro da ANS

## Problema

No processo de **ressarcimento ao SUS**, as operadoras de saúde devem devolver ao Sistema Único de Saúde (SUS) valores correspondentes aos atendimentos prestados a seus beneficiários que foram realizados em unidades públicas. A Agência Nacional de Saúde Suplementar (ANS) disponibiliza relatórios financeiros, chamados **ABI (Aviso de Beneficiário Identificado)**, que detalham os atendimentos prestados a cada beneficiário. O processo de baixar esses relatórios, disponível no [site da ANS](https://www.ans.gov.br/index.php/component/centralderelatorio/?view=login), é manual e repetitivo.

Com o aumento no número de relatórios ABI (atualmente no 98º), o processo se torna mais moroso e sujeito a erros, demandando uma solução automatizada para otimizar o tempo e o esforço necessários para obtenção desses dados.

## Solução

Este repositório oferece uma automação para o download dos relatórios de ressarcimento ao SUS disponibilizados pela ANS. O código realiza o login no site da ANS, e baixa os relatórios ABI de maneira automática, solicitando apenas as credenciais da operadora. 

Essa solução visa aumentar a eficiência e reduzir o tempo despendido no processo de download de relatórios financeiros.

## Funcionalidades

- **Login Automatizado**: O script faz login na plataforma da ANS utilizando as credenciais fornecidas.
- **Download Automático**: Após o login, os relatórios ABI são baixados de forma automática e eficiente.
- **Escolha de Diretório**: Utiliza uma interface gráfica para escolher o local onde os relatórios serão salvos.

## Tecnologias e Bibliotecas Utilizadas

Aqui estão as principais bibliotecas e ferramentas utilizadas no projeto:

- **`os`**: Biblioteca padrão para interações com o sistema de arquivos.
- **`time`**: Biblioteca para controlar pausas e temporizações no fluxo do programa.
- **`threading`**: Utilizada para gerenciamento de threads, garantindo que a interface gráfica permaneça responsiva durante a execução de tarefas demoradas.
- **`requests`**: Biblioteca utilizada para fazer requisições HTTP (não utilizada diretamente no Selenium, mas pode ser útil em certas condições).
- **`selenium`**: Para automação de navegadores web. Utilizada para controlar o Chrome e realizar login e download de relatórios.
- **`webdriver_manager.chrome`**: Facilita o gerenciamento do ChromeDriver, instalando automaticamente a versão correta do driver para o navegador.
- **`tkinter`**: Utilizada para criar a interface gráfica (GUI) que permite ao usuário inserir suas credenciais e escolher onde os arquivos serão salvos.
- **`webdriver.common.by`, `webdriver.support.ui.WebDriverWait`, `webdriver.support.expected_conditions`**: Utilizados para aguardar elementos da página web durante a automação com Selenium.
- **`tkinter.filedialog`**: Permite ao usuário escolher o diretório onde os arquivos serão salvos por meio de uma interface gráfica.
- **`messagebox`**: Utilizado para exibir mensagens de erro ou confirmação ao usuário.

## Requisitos

Certifique-se de ter o Python instalado em sua máquina. Este projeto também requer o Google Chrome instalado.

## Instalação do ChromeDriver
Este projeto utiliza o ChromeDriver para controlar o navegador Chrome. Para configurá-lo:

- 1. O webdriver_manager cuida automaticamente da instalação do ChromeDriver correto, portanto, não é necessário baixá-lo manualmente. O ChromeDriver é gerenciado com:

from webdriver_manager.chrome import ChromeDriverManager

- 2. Durante a execução do script, ele instalará a versão correta do driver automaticamente.

## Uso

Execute o script Python que contém o código de automação.
Uma interface gráfica aparecerá solicitando as credenciais da operadora de saúde e permitindo que você escolha o diretório onde deseja salvar os relatórios.
Após inserir as credenciais e selecionar o local, o processo de download será iniciado automaticamente.

## Processo de Ressarcimento ao SUS

O ressarcimento ao SUS ocorre quando beneficiários de planos de saúde utilizam o sistema público de saúde para atendimentos que poderiam ter sido realizados na rede privada. A operadora deve restituir o valor do atendimento ao SUS, e para isso, a ANS disponibiliza relatórios de beneficiários identificados (ABI), detalhando cada utilização.

Esses relatórios precisam ser analisados e baixados regularmente pelas operadoras, o que torna o processo altamente repetitivo, principalmente com o aumento constante do número de relatórios.

## Imagens do Processo

- Tela de Login da ANS
![Tela de Login](/imgs\login.png)

- Interface da Ferramenta
![Interface da Ferramenta](/imgs\interface.png)

- Relatórios Disponíveis para Download
![Relatórios ABI](/imgs\relatorios.png)

## Contribuições

Contribuições são bem-vindas! Se você tiver sugestões de melhorias ou encontrar problemas, sinta-se à vontade para abrir uma issue ou enviar um pull request.
