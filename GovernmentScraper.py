import requests
import io
import urllib3
from bs4 import BeautifulSoup
import lxml
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def numOfPages(Page_Possibilities,driver):
    [firstgoToPage,firstOnPage] = Page_Possibilities[0]
    num = 0
    if not pageExists(firstgoToPage,firstOnPage,driver) :
        return 1
    else:
        for i in range(len(Page_Possibilities)):
            
            goTo = Page_Possibilities[i][1]
            onPage = Page_Possibilities[i][0]
            if pageExists(onPage,goTo,driver):
                num = i+1
    return num
            
def NavigateToPage(goToPage,driver):
    button = driver.find_element_by_xpath(goToPage)
    button.click()
def pageExists(onPage,goToPage, driver):
    Status = True
        
    try:
        driver.find_element_by_xpath(onPage)

    except NoSuchElementException:
        try:
            driver.find_element_by_xpath(goToPage)
        except NoSuchElementException:
            Status = False
    return Status
def isOnPage(onPage,goToPage,driver):
    if not pageExists(onPage,goToPage,driver):
        if 'td[1]' in onPage:
            return True
        else:
            return False
    try:
        driver.find_element_by_xpath(onPage)
    except:
        return False
    return True

def addStudiesFromPage():
    url = 'http://pse5-esd5.aadnc-aandc.gc.ca/pubcbw/publication/catalog.aspx?l=E'
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    text = ""
    soup = BeautifulSoup(response.data)
    table = soup.find_all('tr')
    span = []
    print(len(table))
    
            
    

driver = webdriver.Firefox()  # Optional argument, if not specified will search path.
driver.get('http://pse5-esd5.aadnc-aandc.gc.ca/pubcbw/publication/catalog.aspx?l=E');
select = Select(driver.find_element_by_id("ContentPlaceHolder1_ddlCategory"))

onPage1 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[102]/td/table/tbody/tr/td[1]/span'
onPage2 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[102]/td/table/tbody/tr/td[2]/span'
onPage3 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[16]/td/table/tbody/tr/td[3]/span'
onPage4 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[78]/td/table/tbody/tr/td[4]/span'
onPage5 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[45]/td/table/tbody/tr/td[5]/span'
goToPage1 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[16]/td/table/tbody/tr/td[1]/a'
goToPage2 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[102]/td/table/tbody/tr/td[2]/a' 
goToPage3 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[102]/td/table/tbody/tr/td[3]/a'
goToPage4 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[102]/td/table/tbody/tr/td[4]/a'
goToPage5 = '/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[102]/td/table/tbody/tr/td[5]/a'

categories = []
for option in select.options:
    categories.append(option.text)

Gobutton = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnGo"]')

analytical_text = ""

for currentCategories in categories:
   PageList = []
   Page_Possibilities = [[onPage1,goToPage1],[onPage2,goToPage2],[onPage3,goToPage3],[onPage4,goToPage4],[onPage5,goToPage5]]
   
   
   select = Select(driver.find_element_by_id("ContentPlaceHolder1_ddlCategory"))
   WebDriverWait(driver,100).until(ec.visibility_of_element_located((By.XPATH,'//*[@id="ContentPlaceHolder1_ddlCategory"]')))
   select.select_by_visible_text(currentCategories)
   WebDriverWait(driver,100).until(ec.visibility_of_element_located((By.XPATH,'//*[@id="ContentPlaceHolder1_btnGo"]')))
   Gobutton = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnGo"]')
   Gobutton.click()
   if not isOnPage(onPage1,goToPage1,driver):
       NavigateToPage(onPage1)
       
   PageFlag = True
   currentPage = 0
   num = numOfPages(Page_Possibilities,driver)
   print(currentCategories+":"+str(num))
   while PageFlag:
       onPage = Page_Possibilities[currentPage][0]
       goToPage = Page_Possibilities[currentPage][1]
       if pageExists(onPage,goToPage,driver):
           if isOnPage(onPage,goToPage,driver):
               analytical_text += addStudiesFromPage()
           else:
               if currentCategories == "Acts, Agreements and Land Claims" and currentPage == 3:
                   goToPage = "/html/body/div/div/main/form/div[3]/div[4]/div[2]/div[6]/div/table/tbody/tr[102]/td/table/tbody/tr/td[3]/span"
               NavigateToPage(goToPage,driver)
               WebDriverWait(driver,100).until(ec.visibility_of_element_located((By.XPATH,onPage)))
               
               analytical_text += addStudiesFromPage()
       else:
           if currentPage == 0:
               analytical_text += addStudiesFromPage()
       currentPage+=1
       
       if currentPage == 5:
           PageFlag = False
       if not pageExists(Page_Possibilities[currentPage][0],Page_Possibilities[currentPage][0],driver):
           PageFlag = False

print(analytical_text)
       
       
       
    
           
        

time.sleep(5) # Let the user actually see something!


            
        
    
def GetAllHtmlLinks(UrlGiven):
    url = UrlGiven
    http = urllib3.PoolManager()
    response = http.request('GET',url)
    soup = BeautifulSoup(response.data, 'lxml')
    htmllinks = []
    for link in soup.find_all('div'):
        print(link)
        #if "pdf=n" in link.get('href'):
        #   htmllinks.append(link.get('href'))
    return htmllinks
