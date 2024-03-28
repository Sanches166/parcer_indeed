import grequests
import requests
import os
import json
import csv
import headers
import extentions
import time
import re
import browser_cookie3

def set_cookie(force = False): 
    if os.path.exists('cookie.txt') and not force:
        with open('cookie.txt', 'r') as f:
            cookies = requests.utils.cookiejar_from_dict(json.load(f))
    else:
        er = input("Файлы cookie устарели или отсутствуют, пожалуйста, войдите в личный кабинет через браузер Google Chrome")
        cookies = browser_cookie3.chrome(domain_name="indeed.com")
        with open('cookie.txt', 'w') as f:
            json.dump(requests.utils.dict_from_cookiejar(cookies), f)
    return cookies
     
def get_csrf(cookies):
    csrf = [cookie for cookie in cookies if cookie.name == 'CSRF']
    return csrf[0].value

url_id = 'https://employers.indeed.com/api/ctws/preview/candidates?encryptedJobId=533027b6caa7'

class Candidate:
    def __init__(self, name, tel, email) -> None:
        self.name = name
        self.tel = tel
        self.email = email
    def __iter__(self):
        return iter([self.name, self.tel, self.email])

start_time = None

# finding name, tel
def get_candidate_data(response):
    top = input("Enter the number of candidates to upload to 'Output.csv'('all' for everyone): ")
    global start_time
    start_time = time.time()
    if top == 'all':
        top = -1
    candidates = response.json()['candidates'][:int(top)]
    cand_list = []
    csrf = get_csrf(response.request._cookies)
    rs = (grequests.get(
        f'https://employers.indeed.com/api/catws/resume/download?id={candidate["candidateId"]}&isPDFView=false&asText=true&indeedcsrftoken={csrf}&indeedClientApplication=candidates-review',
            headers=headers.pdf, cookies = response.request._cookies)
            for candidate in candidates)
    
    res = grequests.map(rs, size = 100)
    print("[+] Parsing start...")
    for r in res:
        cand_id = re.search(r'id=([0-9a-fA-F]{12})', r.request.url).group(1)
        for candidate in candidates:
            if candidate['candidateId'] == cand_id:
                cand_name = candidate['name']
                tel = candidate['phoneNumber']
                break
        if r.status_code == 200:
           email = extentions.parser(r)
        else:
            cand_id = re.search(r'id=([0-9a-fA-F]{12})', r.request.url).group(1)
            email = extentions.fetch_indeed_email(cand_id, cookie=r.request._cookies)
        print(cand_name, tel, email)
        cand_list.append(Candidate(cand_name, tel, email))
    return cand_list

def save_file(filename, cand_list):    
    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        wr = csv.writer(csv_file, delimiter=',')
        for cdr in cand_list:
            wr.writerow(list(cdr))

def main():
    cookies = set_cookie()
    response = requests.get(url_id, headers=headers.default, cookies=cookies)
    if response.status_code != 200:
        cookies = set_cookie(True)
        response = requests.get(url_id, headers=headers.default, cookies=cookies)
        if response.status_code != 200:
            raise RuntimeError('[-] CloudFlare detected')
    cand_list = get_candidate_data(response)
    save_file('Output.csv', cand_list)
    end_time = time.time()
    t = end_time-start_time
    print(f'[+] Parsing completed with time: {round(t,2)} sec')

if __name__ == '__main__':
    main()



