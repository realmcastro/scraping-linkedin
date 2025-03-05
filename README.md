# LinkedIn Job Scraper with Python

Um scraper simples para buscar vagas no LinkedIn com base em palavras-chave, tipo de vaga, local e data máxima. Permite buscas avançadas com lógica booleana (AND/OR) e filtros detalhados.

## 🚀 Funcionalidades

- 🔍 **Busca Avançada**: Utilize operadores booleanos (AND/OR) para combinações de palavras-chave
- 🗂️ **Filtros de Vaga**: Filtre por tipo de vaga (tempo integral, meio período, contrato, etc.)
- 📍 **Filtro de Localização**: Selecione entre presencial, remoto ou híbrido
- 📅 **Filtro de Data**: Filtre as vagas por intervalo de tempo (últimas 24h, 7 dias, 30 dias)
- 🎯 **Busca Simples**: Permite buscas simples por palavras-chave

## 🛠️ Tecnologias

- Python
- Requests
- BeautifulSoup
- argparse (para argumentos de linha de comando)

## 📦 Instalação

1. Clone o repositório:

git clone git@github.com:seu-usuario/linkedin-job-scraper.git  
cd linkedin-job-scraper

2. Instale as dependências:

pip install -r requirements.txt

3. Execute o scraper:

python scraper.py

## 🔧 Uso

### Busca Simples

Para realizar uma busca simples por uma palavra-chave como "react":

python scraper.py --keywords "react"

### Busca Avançada (AND/OR)

Para realizar uma busca combinada com operadores booleanos:

python scraper.py --keywords "react AND junior"  
python scraper.py --keywords "react OR angular"  
python scraper.py --keywords "react OR angular AND junior"

### Filtrar por Data Máxima

Para buscar vagas até uma data específica:

python scraper.py --keywords "react" --max-date "2023-10-01"

### Filtrar por Tipo de Vaga e Local

Para filtrar vagas por tipo e local:

python scraper.py --keywords "react" --job-type F --place 2

### Para que serve `--job-type` e `--place`?

- **--job-type**: Filtra o tipo de vaga. Valores possíveis:
  - F → Purnawaktu (Tempo integral)
  - CP → Paruh Waktu (Meio período)
  - CC → Kontrak (Contrato)
  - T → Sementara (Temporário)
  - CV → Sukarelawan (Voluntário)

- **--place**: Filtra o local de trabalho. Valores possíveis:
  - 1 → Presencial
  - 2 → Remoto
  - 3 → Híbrido

## 📁 Estrutura do Projeto

linkedin-job-scraper/  
├── scraper.py           # Arquivo principal que executa o scraper  
├── requirements.txt     # Dependências do projeto  
└── README.md            # Documentação do projeto

## ⚠️ Observações Importantes

- **Limitações**: O LinkedIn pode bloquear o acesso ao scraper após múltiplas requisições em um curto período.
- **Compatibilidade**: Este projeto foi testado no Python 3.x.

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
