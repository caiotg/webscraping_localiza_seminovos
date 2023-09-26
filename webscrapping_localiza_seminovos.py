import pandas as pd
import datetime as dt

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from sqlalchemy import create_engine

class webscrappingLocalizaSeminovos():

    def __init__(self, listaMontadoras, conexao, baseDadosCarros, baseDadosCarrosVendidos):

        self.listaMontadoras = listaMontadoras
        self.conexao = conexao
        self.baseDadosCarros = baseDadosCarros
        self.baseDadosCarrosVendidos = baseDadosCarrosVendidos

    def pegando_carros_site(self):

        options = webdriver.ChromeOptions()

        # CASO QUEIRA RODAR COM O NAVEGADOR EM SEGUNDO PLANO
        # options.add_argument('--headless')

        driver = webdriver.Chrome(service=Service(), options=options)

        dados = {'montadora': [],'modelo': [], 'local_venda': [], 'km': [], 'ano': [], 'preco': []}

        for montadora in self.listaMontadoras:

            try:

                driver.get(url=f'https://seminovos.localiza.com/carros/mitsubishi?marca1={montadora}')
                
                itens = []

                driver.implicitly_wait(3)

                numeroCarrosPagina = driver.find_element('xpath', '/html/body/app-root/nz-layout/nz-content/app-vehicles-list/section/div/div[2]/div')
                numeroCarrosPagina = numeroCarrosPagina.text
                numeroCarrosPagina = int(numeroCarrosPagina.split(' ')[0])

                while (numeroCarrosPagina - 1) > len(itens):

                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

                    driver.implicitly_wait(2)

                    elementos = driver.find_elements(By.CSS_SELECTOR, 'body > app-root > nz-layout > nz-content > app-vehicles-list > section > div > div:nth-child(3) > div > span')

                    for elemento in elementos:
                        
                        if elemento not in itens:
                            
                            itens.append(elemento)
                
                pagina = '/html/body/app-root/nz-layout/nz-content/app-vehicles-list/section/div'
                element = driver.find_element('xpath', f'{pagina}')
                htmlElement = element.get_attribute('outerHTML')
                soup = BeautifulSoup(htmlElement, 'html.parser')

                carros = soup.find_all('h2', {'class': 'subtitle-car-primary'})
                local = soup.find_all('span', {'class': 'text-location'})
                quilometragem = soup.find_all('span', {'class': 'text-milage'})
                ano = soup.find_all('span', {'class': 'text-km'})
                preco = soup.find_all('span', {'class': 'text-price'})
                
                montadora = montadora.replace('%20', ' ')

                for i in range(len(carros)):

                    dados['montadora'].append(montadora)
                    dados['modelo'].append(carros[i].text)
                    dados['local_venda'].append(local[i].text)
                    dados['km'].append((quilometragem[i].text)[1:-5].replace('.',''))
                    dados['ano'].append((ano[i].text)[1:-2])
                    dados['preco'].append(int(preco[i].text[4:-1].replace('.', '')))

                print(f'NUMERO DE CARROS DA {montadora}: {numeroCarrosPagina}')

            except:
                
                continue

        driver.quit()

        self.dados = dados

    def formatando_dados(self):

        dadosSite = pd.DataFrame(self.dados)

        dadosSite['data_atualizacao'] = dt.date.today()
        
        dadosSite['modelo'] = dadosSite['modelo'].apply(lambda modelo: modelo.strip())
        dadosSite['verificador'] = dadosSite[['montadora', 'modelo','ano','km']].agg('_'.join, axis=1)
        dadosSite['verificador'] = dadosSite['verificador'].apply(lambda item: item.replace(' ','_'))
        dadosSite['km'] = dadosSite['km'].astype(int)

        self.dadosSite = dadosSite

    def pegando_dados_base(self):

        baseDados = pd.read_sql(f'SELECT * FROM {self.baseDadosCarros}',con= self.conexao)
        
        baseDados['km_str'] = baseDados['km'].astype(str)

        baseDados['verificador'] = baseDados[['montadora', 'modelo','ano','km_str']].agg('_'.join, axis=1)
        baseDados['verificador'] = baseDados['verificador'].apply(lambda item: item.replace(' ','_'))

        baseDados = baseDados.drop('km_str', axis=1)

        self.baseDados = baseDados

    def comparando_dados(self):

        self.dadosSite['status'] = self.dadosSite['verificador'].isin(self.baseDados['verificador'])
        self.baseDados['status'] = self.baseDados['verificador'].isin(self.dadosSite['verificador'][self.dadosSite.status == True])

        carrosVendidos = self.baseDados[self.baseDados['status'] == False]

        carrosVendidos = carrosVendidos.drop('status', axis=1)
        carrosVendidos = carrosVendidos.drop('verificador', axis=1)

        self.carrosVendidos = carrosVendidos

    def atulizando_dados_base(self):

        self.baseDadosVendas = pd.read_sql(f'SELECT * FROM {self.baseDadosCarrosVendidos}', con= self.conexao)

        if len(self.baseDadosVendas) != len(self.carrosVendidos):

            self.carrosVendidos.to_sql(f'{self.baseDadosCarrosVendidos}', self.conexao, index=False, if_exists='append')
            print(f'{len(self.carrosVendidos)} ITENS FORAM ADICIONADOS A BASE DE DADOS.')
        
        else:

            print('A BASE DE DADOS JA ESTA ATUALIZADA.')

        self.dadosSite = self.dadosSite.drop('status', axis=1)
        self.dadosSite = self.dadosSite.drop('verificador', axis=1)

        self.dadosSite.to_sql(f'{self.baseDadosCarros}', self.conexao, index=False, if_exists='replace')


if __name__ == '__main__':

    from dotenv import load_dotenv
    import os

    load_dotenv()

    user= 'root'
    senha = os.getenv('senha')
    banco_de_dados = 'carros_localiza_seminovos'
    host = 'localhost'
    porta = 3306

    conexao = create_engine(url= f'mysql+pymysql://{user}:{senha}@{host}:{porta}/{banco_de_dados}')
    
    listaMontadoras = ['FORD','VOLKSWAGEN','FIAT','JEEP','RENAULT','CITROEN','CHEVROLET','TOYOTA','NISSAN','HYUNDAI','PEUGEOT','MERCEDES%20BENZ','AUDI','VOLVO','MITSUBISHI','BMW','KIA','LAND%20ROVER','HONDA','JAGUAR','CHERY','JAC']

    carrosLocaliza = webscrappingLocalizaSeminovos(listaMontadoras= listaMontadoras, conexao= conexao, baseDadosCarros= 'carros_a_venda', baseDadosCarrosVendidos= 'carros_vendidos')

    # carrosLocaliza.pegando_carros_site()
    # carrosLocaliza.formatando_dados()
    # carrosLocaliza.pegando_dados_base()
    # carrosLocaliza.comparando_dados()
    # carrosLocaliza.atualizando_dados_base()

    # print('----------------------------------------------------------------------------------------------------')
    # print(carrosLocaliza.dadosSite)
    # print('----------------------------------------------------------------------------------------------------')
    # print(carrosLocaliza.carrosVendidos)
    # print('----------------------------------------------------------------------------------------------------')
