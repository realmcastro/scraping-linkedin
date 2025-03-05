import math
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote as encode
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
import argparse

INIT_URL = 'https://www.linkedin.com/jobs/search'
PAGE_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
POST_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/'

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

def log_error(e):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} ERROR {e}\n")

def log_info(i):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} INFO {i}\n")

def params(start=0):
    params = [
        ('f_TPR', time_range),
        ('position', '1'),
        ('pageNum', '0'),
        ('start', str(start)),
        ('sortBy', 'DD')
    ]
    
    if keywords: params.append(('keywords', encode(keywords)))
    if location: params.append(('location', encode(location)))
    if distance: params.append(('distance', distance))
    if job_type: params.append(('f_JT', ','.join(job_type)))
    if place: params.append(('f_WT', ','.join(place)))
    
    return '?' + '&'.join([f"{k}={v}" for k, v in params])

def job_result():
    if limit_jobs > 0:
        return limit_jobs

    try:
        uri = INIT_URL + params()
        res = requests.get(uri, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        job_count_element = (soup.find('span', {'class': 'results-context-header__job-count'}) or 
                            soup.find('span', {'class': 'results-context-header__new-jobs'}))
        
        if job_count_element:
            job_count = job_count_element.text.strip().replace(",", "").replace("+", "")
            return min(int(job_count), 1000)  # Limite máximo de segurança
        return 1000  # Default se não encontrar contagem
    
    except Exception as e:
        log_error(f"Error getting job count: {e}")
        return 1000  # Default para continuar a execução

def job_id_list_per_page(start):
    try:
        uri = PAGE_URL + params(start)
        res = requests.get(uri, headers=HEADERS, timeout=30)
        
        if res.status_code == 404:
            return []
            
        if not res.ok:
            log_info(f"Retrying page {start}...")
            sleep(2)
            return job_id_list_per_page(start)

        soup = BeautifulSoup(res.text, 'html.parser')
        return [li.find('div')['data-entity-urn'].split(':')[-1] 
                for li in soup.find_all('li') 
                if li.find('div') and li.find('div').has_attr('data-entity-urn')]
                
    except Exception as e:
        log_error(f"Page {start} failed: {e}")
        sleep(1)
        return []

def job_detail(job_id):
    try:
        uri = POST_URL + job_id
        res = requests.get(uri, headers=HEADERS, timeout=30)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        detail = {
            'title': soup.find('h2', {'class': 'top-card-layout__title'}).get_text(strip=True) if soup.find('h2', {'class': 'top-card-layout__title'}) else None,
            'company': soup.find('a', {'class': 'topcard__org-name-link'}).get_text(strip=True) if soup.find('a', {'class': 'topcard__org-name-link'}) else None,
            'location': soup.find('span', {'class': 'topcard__flavor--bullet'}).get_text(strip=True) if soup.find('span', {'class': 'topcard__flavor--bullet'}) else None,
            'id': job_id,
            'link': uri,
            'description': (soup.find('div', {'class': 'show-more-less-html__markup'}).get_text(strip=True) 
                          if soup.find('div', {'class': 'show-more-less-html__markup'}) else None),
            'time': soup.find('span', {'class': 'posted-time-ago__text'}).get_text(strip=True) if soup.find('span', {'class': 'posted-time-ago__text'}) else None,
        }

        criterias = soup.find_all('li', {'class': 'description__job-criteria-item'})
        for crit in criterias:
            key = crit.find('h3').get_text(strip=True)
            value = crit.find('span').get_text(strip=True)
            detail[key] = value
            
        return detail
    
    except Exception as e:
        log_error(f"Job {job_id} failed: {e}")
        return {'id': job_id, 'error': str(e)}

def calculate_time_range(max_date):
    if not max_date:
        return 'r86400'  # Default: 24 horas
    
    max_date = datetime.strptime(max_date, '%Y-%m-%d')
    delta = datetime.now() - max_date
    return f"r{int(delta.total_seconds())}"

def main():
    global keywords, location, time_range, distance, job_type, place, limit_jobs
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', type=str, default='', help='Palavras-chave para busca (ex: "react AND junior", "react OR angular")')
    parser.add_argument('--location', type=str, default='Indonesia', help='Localização para filtrar')
    parser.add_argument('--max-date', type=str, default='', help='Data máxima no formato YYYY-MM-DD')
    parser.add_argument('--distance', type=str, default='', help='Distância em milhas')
    parser.add_argument('--job-type', nargs='+', default=[], help='Tipos de emprego (F, CP, CC, etc)')
    parser.add_argument('--place', nargs='+', default=[], help='Local de trabalho (1=Presencial, 2=Remoto)')
    parser.add_argument('--limit-jobs', type=int, default=0, help='Limitar número de vagas')
    args = parser.parse_args()
    
    # Atualizar variáveis globais com os argumentos
    keywords = args.keywords
    location = args.location
    time_range = calculate_time_range(args.max_date)
    distance = args.distance
    job_type = args.job_type
    place = args.place
    limit_jobs = args.limit_jobs

    try:
        total_jobs = job_result()
        num_pages = math.ceil(total_jobs / 25)
        print(f"⏳ Encontradas ~{total_jobs} vagas ({num_pages} páginas)")

        job_ids = []
        for page in tqdm(range(num_pages), desc='📃 Páginas'):
            job_ids += job_id_list_per_page(page * 25)
            sleep(0.1)
        
        if limit_jobs > 0:
            job_ids = job_ids[:limit_jobs]

        jobs = []
        for job_id in tqdm(job_ids, desc='🔍 Vagas'):
            jobs.append(job_detail(job_id))
            sleep(0.2)

        df = pd.DataFrame(jobs).drop_duplicates('id')
        df.to_csv('vagas.csv', index=False, encoding='utf-8-sig')
        print(f"✅ {len(df)} vagas salvas em vagas.csv")

    except Exception as e:
        log_error(f"Fatal error: {e}")
        print("❌ Erro grave - verifique log.txt")

if __name__ == "__main__":
    main()