import os
import pandas as pd
import re
import pickle
from selenium import webdriver
import warnings
warnings.filterwarnings("ignore")

# ==========================================================================================================================

# Create functions to find all the indexes of a specific character
def find_str(string, char):
    indices = [i.start() for i in re.finditer(char, string)]
    return indices

# Create functions to find the relevant personal details
def birthdate(details):
    det = details[details.find('Né(e) en :'):]
    det = det[:det.find('\n')]
    beg = det.find(':')+2
    return det[beg:]

def height(details):
    det = details[details.find('Taille / Poids :'):][len('Taille / Poids : '):]
    det = det[:det.find(' /')]
    return det

def weight(details):
    det = details[details.find('Taille / Poids :'):]
    det = det[:det.find('\n')]
    beg = find_str(det, '/')[1]+1
    return det[beg:]

def gender(details):
    det = details[details.find('Cat. / Nat. :'):]
    det = det[:find_str(det, '/')[2]]
    beg = find_str(det, '/')[1]+1
    return det[beg:]

def license_nb(details):
    det = details[details.find('N° Licence :'):]
    det = det[:det.find('\n')]
    beg = det.find(':')+2
    return det[beg:]   

# Create function to organize the results in a dataframe
def results(details, distances, disciplines):
    df = pd.DataFrame(columns = ['ID', 'Birthdate', 'Height', 'Weight', 'Gender', 'Distance', 'Time', 'Date'])
    l_nb = license_nb(details)
    bd = birthdate(details)
    h = height(details)
    w = weight(details)
    g = gender(details)
    
    for distance in distances: 
        if details.find('\n'+distance+'\n') != -1:  
            try:
                beg = details.find('\n'+distance+'\n')+1
                end = details.find('\n'+disciplines[disciplines.index(distance)+1]+'\n')
                result = details[beg:end]
            except:
                result = details[details.find('\n'+distance+'\n')+1:details.find('\n>> Fermer cette Fenêtre <<')]
            
            locs = find_str(result, '\n')
            dist = result[:locs[0]]
            
            for i in range(len(locs)):
                if i < len(locs)-1:            
                    res = result[locs[i]+1:locs[i+1]]
                else:
                    res = result[locs[i]+1:]
                
                loc_spaces = find_str(res, ' ')
                date = res[loc_spaces[0]+1:loc_spaces[1]]
                perf = res[loc_spaces[1]+1:loc_spaces[2]]
                df2 = pd.DataFrame([l_nb, bd, h, w, g, dist, perf, date]).T
                df2.columns = df.columns
                df = pd.concat([df,df2], axis = 0)
    
    return df

# ==========================================================================================================================

# Web scrapping
path = 'C:/Users/h.gisserot/Desktop/MIT/15.077/Final Project/Option 1 - Running prediction/chromedriver.exe'
driver = webdriver.Chrome(path)

# Relevant urls
urls = ['https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=208&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=,',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=215&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=230&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=250&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=252&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=260&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=261&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=271&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=295&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=299&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=298&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=209&frmplaces=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=211&frmplaces=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=216&frmplaces=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=231&frmplaces=&frmamaxi=&frmsexe=M&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=208&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=,',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=215&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=230&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=250&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=252&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=260&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=261&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=271&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=295&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=VR',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=299&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=298&frmplaces=&frmnationalite=&frmamini=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=209&frmplaces=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=211&frmplaces=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=216&frmplaces=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=',
        'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=1&frmespace=0&frmannee=2019&frmathlerama=&frmfcompetition=&frmfepreuve=&frmepreuve=231&frmplaces=&frmamaxi=&frmsexe=F&frmcategorie=&frmvent=']

# Relevant distances
distances = ['800m', '800m - Salle', '1 000m', '1 000m - Salle', '1 500m', '1 500m - Salle', '3 000m', '3 000m - Salle', 
             '5 000m', '5 000m - Salle', '5 Km Route', '10 000m', '10 Km Route', '15 Km Route', '20 Km Route', '20 000m', 
             '1/2 Marathon', 'Marathon', '100 Km Route', '24 Heures']

# Scrapping parameters
url_nb_beg = 0
url_nb_end = len(urls)
page_nb = 1
max_page_nb = 20

for url in urls[url_nb_beg:url_nb_end]:
    driver.get(url)
    element = driver.find_element_by_class_name('barSelect')
    pages = element.find_elements_by_tag_name('option')
    nb_pages = len(pages)
    
    for p in range(page_nb-1, nb_pages):
        element = driver.find_element_by_class_name('barSelect')
        pages = element.find_elements_by_tag_name('option')
        pages[p].click()
        buttons = driver.find_elements_by_xpath("//a[@title='cliquez pour le détail']")
        
        for button in buttons:       
            try:
                button.click()
                driver.switch_to.window(driver.window_handles[1])
                details = driver.find_element_by_id('ctnContentDetails').text
                disciplines = driver.find_elements_by_class_name('innersubLabels')
                disciplines = [disc.text for disc in disciplines]
                
                if (buttons.index(button) == 0) & (p % max_page_nb == 0):
                    if p >= page_nb:
                        data.to_csv('dataset' + str(urls.index(url)) + ' (pages ' + str(p-max_page_nb+1) + ' to ' + str(p) + ')' + '.csv')
                    
                    data = results(details, distances, disciplines)
                else:
                    data = pd.concat([data, results(details, distances, disciplines)], axis = 0)
                                  
            except:
                pass
            
            driver.switch_to.window(driver.window_handles[0])
        
        print('page ' + str(p+1) + '/' + str(len(pages)))
        print(data)
    
    if p < max_page_nb:
        data.to_csv('dataset' + str(urls.index(url)) + '.csv')
    else:
        data.to_csv('dataset' + str(urls.index(url)) + ' (pages ' + str(max_page_nb*(p//max_page_nb)+1) + ' to ' + str(p+1) + ')' + '.csv')
    
    page_nb = 1
    
driver.quit()

# ==========================================================================================================================

# Group datasets and remove duplicates
files = os.listdir()
files = [file for file in files if file.startswith('dataset')]
print("Dataset 1/" + str(len(files)))
data = pd.read_csv(files[0]).iloc[:,1:]

for file in files[1:]:
    print("Dataset " + str(files.index(file)+1) + "/" + str(len(files)))
    df = pd.read_csv(file).iloc[:,1:]
    data = pd.concat([data, df], axis = 0)

data = data.drop_duplicates()

# Convert IDs to simple numbers
ids = list(data.ID.unique())
for i in range(data.shape[0]):
    print(str(i) + "/" + str(data.shape[0]))
    data.ID.values[i] = ids.index(data.ID.values[i])

# Store dataset
f = open('data_raw.pckl', 'wb')
pickle.dump(data, f)
f.close()