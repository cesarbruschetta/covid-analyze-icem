# Projeto para extrair e analizar os dados do Covid-19 da cidade de Icem-SP

## Icem-SP

**Icém** é um município brasileiro do estado de São Paulo, na divisa com Minas Gerais, tem uma população de 8.243 habitantes (IBGE/2019). Está situado próximo a importantes centros urbanos (Barretos, São José do Rio Preto, Catanduva), tem nestes municípios grandes polos emissores. Está situado a 84 km de Barretos, 55 km de São José do Rio Preto e 112 km de Catanduva. A cidade se localiza às margens do Rio Grande.
[Mais informações](https://pt.wikipedia.org/wiki/Ic%C3%A9m)

## Dados 
Os dados foram obtidos atraves da FanPage da [Prefeitura de Icem](https://www.facebook.com/prefeituradeicem/) e os dados contemplam as datas de 21/03/2020 ate 29/06/2020, os dados eram publicados em _posts_ diarios com os dados de casos **investigados**, **descartados**, **confirmados**.

## Ferramentas utilizadas

### Crawler

O Crawler foi ecrito em python utilizando o framework [Scrapy](https://scrapy.org/) e utilizando o projeto [Fbcrawl](https://github.com/rugantio/fbcrawl) como base. 
Foi utilizados para extrair os _posts_ do FanPage do Facebook 

### Vision AI

Para extrair os dados das imagens dos _posts_, foi utilizado o **Google Vision OCR** que é uma api de machine learning e IA do Google Cloud que detecta e extrai texto de imagens.

### Selenium

Ele foi utilizado para optenção das imagens dos _posts_ do FanPage do Facebook. O Selenium é uma ferramenta utilizada para automatização de testes de sistemas que permite ao usuário reproduzi-los rapidamente no ambiente real da aplicação, em função da sua integração direta com o navegador. Através de uma extensão podemos criar os scripts de testes de forma simples e utilizar nas mais diversas linguagens de programação. 

### Outras Ferramentas
* Pandas
* Python

## Licence
[Apache License](./LICENSE) - Version 2.0, January 2004 

## Autor
[Cesar Augusto](https://cesarbruschetta.github.io/)