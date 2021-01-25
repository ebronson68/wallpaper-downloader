#!/usr/bin/python3
import xlsxwriter
import re
import requests
from bs4 import BeautifulSoup
import argparse

# Creating arguments for script
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', action='count', help='increase the verbosity', default=0)
parser.add_argument('-O', '--output', help='file location you want to save contents to', default="/home/awnix.net/bbronson/hyperlink.xlsx")
parser.add_argument('-p', '--results-per-page', help='results per page on IDC search query', default=100, type=int, dest="rpp",choices=[25, 50, 100])
parser.add_argument('-s', '--start-page', help='start on specific page', default="1", dest="start_page", type=int)
parser.add_argument('-e', '--end-page', help='end on specific page', dest="end_page", type=int)
parser.add_argument('-a', '--authors', help='number of author columns', default=20, dest="num_authors", type=int)
args = parser.parse_args()

# Setting IDC URL to use for href a class to link conversions
idc_url = "https://www.idc.com"

# Initializing the Excel sheet
workbook = xlsxwriter.Workbook(args.output)
worksheet = workbook.add_worksheet('IDC Report')

def main():
    # Setting default formatting and values
    worksheet.set_column('A:A', 55)
    worksheet.set_column('B:T',13)
    worksheet.write('A1', 'TITLE')
    # Setting value to iterate off of
    i = 1
    # Looping while count is less than or equal to argument used when calling the script (or the default value if not used)
    while i <= args.num_authors:
        # Setting default values for author columns
        worksheet.write(column_number(i - 1) + "1", 'AUTHOR ' + str(i))
        # Iterating value
        i = i + 1
    # Getting basic URL for scraping page once
    url = 'https://www.idc.com/search/simple/perform_.do?query=&page=1&hitsPerPage=25&sortBy=DATE&lang=English&athrT=10&cmpT=10'
    # Setting up BeautifulSoup HTML parser for scraping page once
    temp_contents = BeautifulSoup(requests.get(url).text, 'html.parser')
    # Regex for page number value
    countregex = re.compile(r"\d+,?\d+(?= r)")
    # Getting page count and stripping it for usability sake
    result_count = countregex.findall(temp_contents.find('div', class_='results-header__count').text.strip())[0].replace(',', '')
    # Setting page to end on if the argument was used when calling the script
    if args.end_page:
        pages = args.end_page
    else:
        pages = round(int(result_count) / args.rpp)
    # Setting value to iterate off of
    iter = 2
    # Setting page variable to value of start_page argument since we won't be able to change that in the script AFAIK.
    page = args.start_page
    # Looping through all the pages
    while page <= pages:
        # Setting URL with argument variables
        url = 'https://www.idc.com/search/simple/perform_.do?query=&page=' + str(args.start_page) + '&hitsPerPage=' + str(args.rpp) + '&sortBy=DATE&lang=English&athrT=10&cmpT=10'
        # Setting up BeautifulSoup HTML parser
        contents = BeautifulSoup(requests.get(url).text, 'html.parser')
        # Creating list of each result on page
        results = contents.find_all('div', class_='result-content')
        # Looping through each of the individual journals
        for result in results:
            # Converting HTML result-title a class to title variable
            title = result.find('a', class_='result-title').text.strip()
            # Converting HTML href a class to link variable
            link = '{}{}'.format(idc_url, result.find('a')['href'])
            # Converting HTML result-authors div class to authors variable
            authors = result.find_all('div', class_='result-authors')
            # Skipping over None type vars
            if None in (title,link,authors):
                continue
            # Inserting journal titles into first column
            item_format(iter,-1,title,link)
            # Looping through individual authors
            for author in authors:
                # Regex for first and last name including any titles or unique characters
                nameregex = re.compile(r"[a-zA-Z_.-]+\,? *[a-zA-Z_.-]+,?[\ |']*[a-zA-Z_.-]+")
                # Using above regex to find author names
                authors_list = nameregex.findall(author.text.strip())
                # Setting value to iterate off of
                author_count = 0
                # Getting list of author hyperlinks through href a classes
                author_links = author.find_all('a', href=True)
                # Looping through authors
                for auth in authors_list:
                    # Insert author name and hyperlink into excel sheet.
                    # Try above unless no link is found for author and instead to use 404 URL
                    try:
                        item_format(iter,author_count,auth,'{}{}'.format(idc_url, author_links[author_count]['href']))
                    except IndexError:
                        item_format(iter,author_count,auth,'{}{}'.format(idc_url, '/getdoc.jsp?containerId=PRF000000'))
                    # Iterating value
                    author_count = author_count + 1
            # Iterating value
            iter = iter + 1
        # Debugging progress through pages
        print(page, '/', pages, 'pages')
        # Iterating value
        page = page + 1
    # Closing file to save changes
    workbook.close()

# Function to insert values into Excel sheet
def item_format(iter,count,item,link):
    worksheet.write_url(get_cell(count,iter), link, string=item)

# Function to convert number to alphabet
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

# Concatenating column letter and row number
# TO-DO: Use this for setting default values for author columns
def get_cell(count,int):
    cell = column_number(count) + str(int)
    return(cell)

# Running everything
if __name__ == "__main__":
    main()
