"""
sec.gov crawler that downloads exhibit 10 form filings of type 10-K, 10-Q, and 8-K (i.e. material contracts)
sec.gov allows 10 requests per second https://www.sec.gov/privacy.htm#security

Modified from https://github.com/dtuggener/LEDGAR_provision_classification/blob/71c31dad8988ec0cccc73f5fb515576538cc4590/sec_crawler.py
"""

import re
import requests
import os
import time
import zipfile

OUTDIR = './sec_data'
BASE_URL = 'https://www.sec.gov/Archives/'
#2020
YEARS = range(2024, 2020, -1)
QS = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
VALID_FORMS = ['10-K', '10-Q', '8-K']
SLEEP_TIME = 1
MAX_RETRIES = 5

def fetch_master_files():
    """Get the master files"""
    for year in YEARS:
        # print(year)
        year = str(year)
        outdir_year = os.path.join(OUTDIR, year)
        # print(outdir_year)
        # print("Printed Year")
        if not os.path.exists(outdir_year):
            os.makedirs(outdir_year)

        for q in QS:
            retry_delay = SLEEP_TIME
            outdir_year_q = os.path.join(outdir_year, q)
            if not os.path.exists(outdir_year_q):
                os.makedirs(outdir_year_q)

            outdir_year_q_master = os.path.join(outdir_year_q, 'master.zip')
            if not os.path.exists(outdir_year_q_master):
                # ex: https://www.sec.gov/Archives/edgar/full-index/2024/QTR1/master.zip
                master_url = BASE_URL + 'edgar/full-index/' + year + '/' + q + '/master.zip'
                print('Downloading', master_url)
                for i in range(MAX_RETRIES):
                    try:
                        response = requests.get(master_url, headers={
        'User-Agent': 'Rice University Amar Kanakamed ask20@rice.edu',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
        })
                        # print(response.content)
                        response.raise_for_status()
                        f = open(outdir_year_q_master, 'wb')
                        f.write(response.content)
                        f.close()
                        break
                    except:
                        retry_delay *= 2
                        time.sleep(retry_delay)


def crawl_master_files():
    """Get crawlable URLs from master files and download contracts"""

    for year in YEARS:
        print(year)
        year = str(year)
        outdir_year = os.path.join(OUTDIR, year)

        for q in QS:
            print(q)
            outdir_year_q = os.path.join(outdir_year, q)
            outdir_year_q_master = os.path.join(outdir_year_q, 'master.zip')
            try:
                z = zipfile.ZipFile(outdir_year_q_master)  # Fails for non-existant Qs, e.g. 2019 Q3
            except:
                continue

            with z.open('master.idx') as f:

                for line in f:
                    line = line.decode('utf8', errors='ignore')

                    if line[0].isdigit():  # CIK number
                        line = line.split('|')

                        if line[2] in VALID_FORMS:
                            filing_txt = line[4].strip().split('/')[-1]
                            filing_id = filing_txt.replace('-', '').replace('.txt', '')
                            print(filing_id)
                            filing_dir = os.path.join(outdir_year_q, filing_id)

                            filing_index = os.path.join(filing_dir, filing_txt.replace('.txt', '') + '-index.html')
                            if not os.path.exists(filing_index):  # Check if we already have downloaded the filing index
                                index_url = os.path.join(BASE_URL, 'edgar/data', filing_id, filing_txt.replace('.txt', '') + '-index.html')
                                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), year, q, 'Downloading index', index_url)
                                retry_delay = SLEEP_TIME
                                for i in range(MAX_RETRIES):
                                    try:
                                        index_html = requests.get(index_url, headers={
                        'User-Agent': 'Rice University Amar Kanakamed ask20@rice.edu',
                        'Accept-Encoding': 'gzip, deflate',
                        'Host': 'www.sec.gov'
                        })
                        # print(response.content)
                                        index_html.raise_for_status()
                                        break
                                    except:
                                        retry_delay *= 2
                                        time.sleep(retry_delay)
                                # with open(filing_index, 'w') as f:
                                #     f.write(index_html.text)
                                # f.close()

                            # Load the index_html
                            index_html = index_html.text
                            trs = re.findall('<tr[^>]*>(.*?)</tr>', index_html, re.S)

                            for row in trs:
                                if '<td' not in row:
                                    continue

                                tds = re.split('</?td[^>]*>', row)
                                if tds[7].startswith('EX-10'):
                                    file_name = re.search('"(.+)"', tds[5]).group(1)
                                    file_url = 'https://www.sec.gov' + file_name

                                    #if file_url.endswith('htm'):
                                    if file_url.endswith('htm') or file_url.endswith('html'):
                                        filing_file = os.path.join(filing_dir, file_name.split('/')[-1])

                                        if not os.path.exists(filing_file):
                                            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), year, q, 'Downloading contract', file_url)
                                            try:
                                                filing_html = requests.get(file_url, headers={
        'User-Agent': 'Rice University Amar Kanakamed ask20@rice.edu',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
        })
                                                if not os.path.exists(filing_dir):
                                                    os.makedirs(filing_dir)
                                                with open(filing_file, 'w') as f:
                                                    f.write(filing_html.text)
                                            except:
                                                print("skipping", filing_file)
                                                continue

                                                

if __name__ == '__main__':

    # print('Fetching master files')
    # fetch_master_files()

    print('Fetching contracts')
    crawl_master_files()
