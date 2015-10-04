from bs4 import BeautifulSoup
import requests

import mechanize
import re
from collections import defaultdict
from time import sleep
import MySQLdb

# ========
# MySQL DB
# ========

sql_conn = MySQLdb.connect(host="localhost", user="USER", passwd="PASS", db="DATABASE", use_unicode=True, charset="utf8")
sql_conn.autocommit(True)
cursor = sql_conn.cursor(MySQLdb.cursors.DictCursor)
cursorcheck = sql_conn.cursor(MySQLdb.cursors.DictCursor)


# ===========
# LOG IN AREA
# ===========

LOGIN_URL = 'https://ello.co/enter'
USERNAME = 'ELLO_EMAIL'
PASSWORD = 'ELLO_PW'

#INITIALIZE A BROWSER
br = mechanize.Browser()  
br.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0')]
br.open(LOGIN_URL)        

#SELECT THE LOGIN FORM
br.select_form(nr=0)
# print br.form

#LOG IN
br['user[email]'] = USERNAME
br['user[password]'] = PASSWORD
resp = br.submit()          

# =============
# SCRAPING AREA
# =============

users_to_scrape = []
users_done = []
user_network = defaultdict(list)

username = ""
# start_username = "elloresearch"
start_username = "YOUR_ELLO_USERNAME"


def scrape_a_user(username, class_marker):

    temp_list_page_1 = []

    following_page = "http://ello.co/"+username+"/following?page=1"

    br.open(following_page)
    users_done.append(username)
    print br.response().code
    # sleep(3)
    soup = BeautifulSoup(br.response().read())

    for x in soup.findAll("p", { "class" : class_marker }):
        # print x.findChildren()[0]

        re1='(<a href="/.*?">)'
        rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
        m = rg.search(str(x))
        if m:
            string1=m.group(1)
            # print "string1", string1
            # string2=m.group(2)
            string1 = string1[10:]
            string1 = string1[:-2]
            following = string1
            if string1 == username:
                pass
            else:
                print username, ":", string1
                sql = "INSERT IGNORE into ello_network (username, following) VALUES (%s, %s)"
                cursor.execute(sql, (username, following))

                users_to_scrape.append(string1)
                user_network[username].append(string1)
                temp_list_page_1.append(string1)
        print "stage 1 for", username, "done"

    # print "temp list page 1"
    # print temp_list_page_1

    boolthing = True
    pagenum = 2
    while boolthing == True:
        temp_list_page_n = []
        following_page = "http://ello.co/"+username+"/following?page="+str(pagenum)

        br.open(following_page)
        users_done.append(username)
        # sleep(3)
        # print response.code

        soup = BeautifulSoup(br.response().read())

        for x in soup.findAll("p", { "class" : class_marker }):
            # print x.findChildren()[0]

            re1='(<a href="/.*?">)'
            rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
            m = rg.search(str(x))
            if m:
                string1=m.group(1)
                # print "string1", string1
                # string2=m.group(2)
                string1 = string1[10:]
                string1 = string1[:-2]
                following = string1
                if string1 == username:
                    pass
                else:
                    print username, ":", string1
                    sql = "INSERT IGNORE into ello_network (username, following) VALUES (%s, %s)"
                    cursor.execute(sql, (username, following))

                    users_to_scrape.append(string1)
                    user_network[username].append(string1)
                    temp_list_page_n.append(string1)

        # print temp_list_page_1
        # print temp_list_page_n
        # print "Length", len(temp_list_page_n)
        # if temp_list_page_n == temp_list_page_1:
        if len(temp_list_page_n) == 0:
            boolthing = False
            print username, "done done done done done"
            print "=============================================="
        else:
            boolthing = True
            pagenum += 1
        sql_conn.commit()   



    # print "users_to_scrape"
    # print users_to_scrape
    # print ""
    # print "users done"
    # print users_done
    # print ""
    # print "user network"
    # print user_network
    # print ""
    # sleep(5)
        # print ""

scrape_a_user(start_username, "profile__deets")

while True: #turn this on for endless scraping
    for x in set(users_to_scrape):
        sleep(3)
        if x in users_done:
            users_to_scrape.remove(x)
        else:
            scrape_a_user(x, "profile__deets")

# print user_network

# for k, v in user_network.items():
#   for vv in v:
#       print k, "\t", vv

