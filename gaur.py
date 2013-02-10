import requests
import re
from urlparse import urljoin
import lxml.html

ROOT = 'https://gestion-alumnos.ehu.es/pls/entrada/'

LOGIN = 'sasw0500.analiza'
EXAMS_COURSES = 'exaw3000.htm'
EXAMS = 'exaw3000.htm_filtro_next'



class GaurAPI():
    
    def __init__(self,username,password):
        
        payload = {
        'p_cod_idioma':'CAS',
        'p_host':'gestion-alumnos.ehu.es',
        'p_colectivo': 'UNIVERSITA',
        'p_usuario': username,
        'p_password': password
        }
        p = requests.post(urljoin(ROOT,LOGIN),data=payload)
        m = re.search(r"self.parent.location( )*=( )*\'(.*)\'",p.content)
        url = m.groups()[-1]
        self.session = re.search(r"p_sesion=([0-9a-z]*)\&?",url).groups()[0]


    def all_marks(self):
        exams_courses = self.lxml_request(EXAMS_COURSES)
        courses_years = exams_courses.cssselect('tr.tr_celda')
        courses = courses_years[0].cssselect('td')[1]
        years = courses_years[1].cssselect('td')[1]
        for course in courses.cssselect('option'):
            if course.get('value') !='':
                for year in years.cssselect('option'):
                    if year.get('value') != '':
                        marks = self.lxml_request(EXAMS,post=True,payload={
                                             'p_plan' : course.get('value'),
                                             'p_anyoAcademico': year.get('value'),
                                             'p_origen_programa' : 'pagina_filtro',
                                             'p_origen_boton' : 'btn_mostrar'})
                        self.process_marks(marks)

    def process_marks(self,marks):
        marks_table = marks.cssselect('table')[0].cssselect('table')[3]
        subjects = marks_table.cssselect('tr')[1:]
        for subject in subjects:
            mark = subject.cssselect('td')[4].text
            calification = subject.cssselect('td')[5].text
            name = subject.cssselect('td')[2].text
            if name is None:
                name = subject.cssselect('td')[2].cssselect('a')[0].text
            if calification is None:
                calification = ''
            if mark == '' or mark is None:
                mark = 'Todavia no hay nota'
            print name +":\n" + mark+ " " + calification +"\n" 


    def request(self,method,root=ROOT,post=False,payload=None):
        if payload is None:
            payload = {'p_sesion': self.session}
        payload.update({'p_sesion': self.session})
        if post:
            return requests.post(urljoin(root,method),data=payload)
        else:
            return requests.get(urljoin(root,method),params=payload)
                

    def lxml_request(self,method,root=ROOT,post=False,payload=None):
        return lxml.html.fromstring(self.request(method,root,post,payload).content)

print ''' ------------------------------------
|                                    |
| Gaur viewer 0.2 by Alejandro Garcia|
|                                    |
 ------------------------------------
'''
username = raw_input('Usuario: ')
password = raw_input('Clave: ')


GaurAPI(username,password).all_marks()
print "..."
raw_input()
