#!/usr/bin/python3
import xlsxwriter
import re
import requests
from bs4 import BeautifulSoup
import argparse


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', action='count', help='increase the verbosity', default=0)
parser.add_argument('-O', '--output', help='file location you want to save contents to', default="/home/awnix.net/bbronson/hyperlink.xlsx")
parser.add_argument('-p', '--results-per-page', help='results per page on IDC search query', default=100, type=int, dest="rpp",choices=[25, 50, 100])
parser.add_argument('-s', '--start-page', help='start on specific page', default="1", dest="start_page", type=int)
parser.add_argument('-e', '--end-page', help='end on specific page', dest="end_page", type=int)
parser.add_argument('-a', '--authors', help='number of author columns', default=20, dest="num_authors", type=int)
args = parser.parse_args()

idc_url = "https://www.idc.com"

workbook = xlsxwriter.Workbook(args.output)
worksheet = workbook.add_worksheet('IDC Report')

def main():
    worksheet.set_column('A:A', 55)
    worksheet.set_column('B:T',13)
    worksheet.write('A1', 'TITLE')
    i = 1
    while i <= args.num_authors:
        worksheet.write(column_number(i - 1) + "1", 'AUTHOR ' + str(i))
        i = i + 1

    url = 'https://www.idc.com/search/simple/perform_.do?query=&page=1&hitsPerPage=25&sortBy=DATE&lang=English&athrT=10&cmpT=10'
    temp_contents = BeautifulSoup(requests.get(url).text, 'html.parser')
    countregex = re.compile(r"\d+,?\d+(?= r)")
    result_count = countregex.findall(temp_contents.find('div', class_='results-header__count').text.strip())[0].replace(',', '')
    if args.end_page:
        pages = args.end_page
    else:
        pages = round(int(result_count) / args.rpp)
    iter = 2
    page = args.start_page
    while page <= pages:
        url = 'https://www.idc.com/search/simple/perform_.do?query=&page=' + str(args.start_page) + '&hitsPerPage=' + str(args.rpp) + '&sortBy=DATE&lang=English&athrT=10&cmpT=10'
        contents = BeautifulSoup(requests.get(url).text, 'html.parser')
        results = contents.find_all('div', class_='result-content')
        for result in results:
            title = result.find('a', class_='result-title').text.strip()
            link = '{}{}'.format(idc_url, result.find('a')['href'])
            authors = result.find_all('div', class_='result-authors')
            if None in (title,link,authors):
                continue
            item_format(iter,-1,title,link)
            for author in authors:
                nameregex = re.compile(r"[a-zA-Z_.-]+\,? *[a-zA-Z_.-]+,?[\ |']*[a-zA-Z_.-]+")
                authors_list = nameregex.findall(author.text.strip())
                author_count = 0
                author_links = author.find_all('a', href=True)
                for auth in authors_list:
                    try:
                        item_format(iter,author_count,auth,'{}{}'.format(idc_url, author_links[author_count]['href']))
                    except IndexError:
                        item_format(iter,author_count,auth,'{}{}'.format(idc_url, '/getdoc.jsp?containerId=PRF000000'))
                    author_count = author_count + 1
            iter = iter + 1
        print(page, '/', pages, 'pages')
        page = page + 1
    workbook.close()

def item_format(iter,count,item,link):
    worksheet.write_url(get_cell(count,iter), link, string=item)

def column_number(argument):
    switcher = {
        -1: "A",
        0: "B",
        1: "C",
        2: "D",
        3: "E",
        4: "F",
        5: "G",
        6: "H",
        7: "I",
        8: "J",
        9: "K",
        10: "L",
        11: "M",
        12: "N",
        13: "O",
        14: "P",
        15: "Q",
        16: "R",
        17: "S",
        18: "T",
        19: "U",
    }
    return switcher.get(argument, "V")

def get_cell(count,int):
    cell = column_number(count) + str(int)
    return(cell)

if __name__ == "__main__":
    main()