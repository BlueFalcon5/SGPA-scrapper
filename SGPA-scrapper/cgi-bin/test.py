#!venv/bin/python3
import re
import cgi
import requests
from bs4 import BeautifulSoup


sgpa = []
sem_no=0
grade_values = {'O':10,'A+':9,'A':8,'B+':7,'B':6,'C':5,'P':4,'F':0}

form = cgi.FieldStorage()
username = form.getvalue('Username')
password = form.getvalue('Password')
data = {'__EVENTTARGET':'lnkStudent' , '__EVENTARGUMENT':''}
url = 'http://srecexams.com'

def params_fetcher(tmp_soup):
    global data
    data['__VIEWSTATE'] = tmp_soup.select_one('#__VIEWSTATE')['value']
    data['__VIEWSTATEGENERATOR'] = tmp_soup.select_one('#__VIEWSTATEGENERATOR')['value']
    data['__EVENTVALIDATION'] = tmp_soup.select_one('#__EVENTVALIDATION')['value']

def is_marks_table(tag):
    return (tag.name == 'table' and tag.has_attr('rules'))

def required_tr(tag):
    return not tag.has_attr('style')

def required_fields(tag):
    if (re.compile("^[1-4AOBCPF]\+?$").match(str(tag.string)) and  not tag.has_attr('width')):
        return True
    else:
        return False


with requests.Session() as s:
    page = s.get(url)
    soup = BeautifulSoup(page.content,'lxml')
    params_fetcher(soup)

    login_page = s.post(url,data = data)
    soup = BeautifulSoup(login_page.text,'lxml')
    params_fetcher(soup)
    data['__EVENTTARGET'] = ''
    data['btnLogin'] = 'Login'
    data['txtPwd'] = username
    data['txtUserId'] = password

    stud_page = s.post('http://srecexams.com/Login.aspx',data = data,allow_redirects=True)
    soup = BeautifulSoup(stud_page.text,'lxml')
    params_fetcher(soup)
    data['__EVENTTARGET'] = 'ctl00$lnkOverallMarks'
    del data['btnLogin'],data['txtUserId'],data['txtPwd']

    marks_page = s.post('http://srecexams.com/StudentLogin/MainStud.aspx',data = data)
    soup = BeautifulSoup(marks_page.content,'lxml')
    '''params_fetcher(soup)
    data['__EVENTTARGET'] = ''
    data['ctl00$btnLogout.x'] = '39'
    data['ctl00$btnLogout.y'] = '12'
    s.post("http://srecexams.com/StudentLogin/Student/overallMarks.aspx",data=data)'''


for tag in soup.find_all(is_marks_table):
    crd = 0
    sum = 0
    sem_marks_list = []

    list = []
    sem_no += 1
    for ctag in tag.find_all(required_fields):
        list.append(str(ctag.string))
    #print(list)
    while(True):
        try:
            int(list[-3])
            break
        except:
            del list[-1]
    for i in range(0,len(list),3):
        crd += int(list[i])
        sem_marks_list.append(int(list[i])*grade_values[list[i+2]])
        sum += sem_marks_list[i//3]
    sgpa.append((sem_no,round(sum/crd,2)))


print('Content-Type: text/html; charset=utf-8\n\n')

print('<table>')
print('<tr><th>sem</th><th>sgpa</th></tr>')
for i in sgpa:
    print('<tr><td>'+str(i[0])+'</td>')
    print('<td>'+str(i[1])+'</td></tr>')
print('</table>')