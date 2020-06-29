# Crawler para posts do facebook

### Instalação

Para rodar o `Scrapy` é necessario insta-lo em um virtual env de python 3.7 ou superior

``` 
$ pip install scrapy
```

### Executando

Para executar o Crawler, execute o comando abaixo 

```
$ scrapy crawl fb \
    -a email="<Email de login>" \
    -a password="<senha de login>" \
    -a page="<ID da pagina alvo>" \
    -a date="<data limite do crowler>" \
--output ../posts_facebook.csv --output-format csv
```