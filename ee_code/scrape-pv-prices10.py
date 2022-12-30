from bs4 import BeautifulSoup
import requests
import pandas as pd
from azure.storage.blob import BlobClient


def scrape_pv(pages: int):
    def subpage_scraping(url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        #Standortinformationen
        table = soup.find('table', attrs={'class': 'table offer-view-base'})
        rows = table.find_all('tr')
        row_list = list()
        for tr in rows:
            td = tr.find_all('td')
            row = [i.text for i in td]
            row_list.append(row)
            row_list_trans = [list(i) for i in zip(*row_list)]

        #Angebote
        table1 = soup.find('table', attrs={'class': ['table offer-view-grid','table offer-view-grid offer-view-has-accepted-offer']})
        rows = table1.find_all('tr')
        row_list1 = list()
        for tr in rows:
            td = tr.find_all('td')
            row = [i.text for i in td]
            while len(row)<4:
                row.append('-')     
            row_list1.append(row)      
            row_list_trans1 = [list(i) for i in zip(*row_list1)]

        #Module
        tables = soup.find_all('table', attrs={'class': ['table offer-view-grid','table offer-view-grid offer-view-has-accepted-offer']})
        table2 = tables[1]
        rows = table2.find_all('tr')
        row_list2 = list()
        for tr in rows:
            td = tr.find_all('td')
            row = [i.text for i in td]
            while len(row)<4:
                row.append('-')    
            row_list2.append(row)       
            row_list_trans2 = [list(i) for i in zip(*row_list2)]    

        #Wechselrichter
        table3 = tables[2]
        rows = table3.find_all('tr')
        row_list3 = list()
        for tr in rows:
            td = tr.find_all('td')
            row = [i.text for i in td]
            while len(row)<4:
                row.append('-')    
            row_list3.append(row)        
            row_list_trans3 = [list(i) for i in zip(*row_list3)] 

        #Stromspeicher
        table4 = tables[4]
        rows = table4.find_all('tr')
        if len(rows) == 0:
            row_list_trans4 = [['-']*6]*4
        else:
            row_list4 = list()
            for tr in rows:
                td = tr.find_all('td')
                row = [i.text for i in td]
                while len(row)<4:
                    row.append('-')      
                row_list4.append(row) 
                row_list_trans4 = [list(i) for i in zip(*row_list4)]   
        
        #Montage und sonstige Leistungen
        table5 = tables[5]
        rows = table5.find_all('tr')
        #tags = rows[0]('span')
        #title = tags[0].get('title')
        row_list5 = list()
        for tr in rows:
            td = tr.find_all('td')
            row = [i.find('span').get('title') if i.find('span') is not None else i.text for i in td]
            while len(row)<4:
                row.append('-')     
            row_list5.append(row)    
            row_list_trans5 = [list(i) for i in zip(*row_list5)]

        
        return row_list_trans, row_list_trans1, row_list_trans2, row_list_trans3, row_list_trans4, row_list_trans5

    PVs = []

    for i in range(0,pages):
        url =  'https://www.photovoltaikforum.com/board/41-angebote/?pageNo='+str(i)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        table = soup.find('ol', attrs={'class': 'tabularList'})

        
        for row in table.findAll('li',
                                    attrs={'class': 'tabularListRow'}):
            children = row.findChildren("ol", recursive=False)

            for child in children:
                grandchildren = child.findChildren("li", recursive=False)
                for grandgrandchild in grandchildren:
                    prefinalchild = grandgrandchild.findChildren("h3", recursive=False)
                    try:
                        timestamp = grandgrandchild.findAll('time', attrs={'class': 'datetime'})
                        uhrzeit = timestamp[0]['datetime']
                    except:
                        uhrzeit = "nan"


                    for finalchild in prefinalchild:
                        PV_values = finalchild.findChildren("a", attrs={'class': 'messageGroupLink wbbTopicLink'}, recursive=False)
                        quote = row.a['href']
                        try:
                            PV_value1 = PV_values[0].string

                            PV_value1 = str(PV_value1).replace(',', '.')
                        except:
                            PV_value1 = "nan"
                        if ('Photovoltaikforum' in PV_value1) or ('PV-Forum' in PV_value1):
                            break
                        else:
                            PV_val = {}
                            PV_val['PV_Values'] = PV_value1
                            PV_val['timestamp'] = uhrzeit
                            PV_val['url'] = quote

                            # #Daten der Unterseiten ebenfalls crawlen!
                            try:
                                standort, angebote, module, wechselrichter, speicher, rest = subpage_scraping(quote)
                                #Standortinformationen auslesen
                                PV_val['PLZ'] = standort[1][1]
                                PV_val['Land'] = standort[1][2]
                                PV_val['Dachneigung'] = standort[1][3]
                                PV_val['Ausrichtung'] = standort[1][4]
                                PV_val['Art der Anlage'] = standort[1][5]
                                PV_val['Ertragsprognose'] = standort[1][13]
                                PV_val['Eigenkapital'] = standort[1][14]
                                #Angebote auslesen
                                try: 
                                    PV_val['A1_Einstellungsdatum'] = angebote[1][1]
                                    PV_val['A1_DatumdesAngebots'] = angebote[1][2]
                                    PV_val['A1_Preis_kWp'] = angebote[1][3]
                                    PV_val['A1_Ertragsprognose'] = angebote[1][4]
                                    PV_val['A1_Anlagengroesse'] = angebote[1][5]
                                    PV_val['A1_Infotext'] = angebote[1][6]                        
                                except Exception as e: 
                                    print(e)
                                    pass
                                try: 
                                    PV_val['A2_Einstellungsdatum'] = angebote[2][1]
                                    PV_val['A2_DatumdesAngebots'] = angebote[2][2]
                                    PV_val['A2_Preis_kWp'] = angebote[2][3]
                                    PV_val['A2_Ertragsprognose'] = angebote[2][4]
                                    PV_val['A2_Anlagengroesse'] = angebote[2][5]
                                    PV_val['A2_Infotext'] = angebote[2][6]                        
                                except Exception as e: 
                                    print(e)
                                    pass
                                try: 
                                    PV_val['A3_Einstellungsdatum'] = angebote[3][1]
                                    PV_val['A3_DatumdesAngebots'] = angebote[3][2]
                                    PV_val['A3_Preis_kWp'] = angebote[3][3]
                                    PV_val['A3_Ertragsprognose'] = angebote[3][4]
                                    PV_val['A3_Anlagengroesse'] = angebote[3][5]
                                    PV_val['A3_Infotext'] = angebote[3][6]                        
                                except Exception as e: 
                                    print(e)
                                    pass
                                try: 
                                    PV_val['A1_Modulanzahl'] = module[1][1]
                                    PV_val['A1_Modulhersteller'] = module[1][2]    
                                    PV_val['A1_Modulbezeichnung'] = module[1][3]
                                    PV_val['A1_Nennleistung_Modul'] = module[1][4]
                                    PV_val['A1_Preis_Modul'] = module[1][5]
                                except Exception as e: 
                                    print(e)
                                    pass 
                                try: 
                                    PV_val['A2_Modulanzahl'] = module[2][1]
                                    PV_val['A2_Modulhersteller'] = module[2][2]    
                                    PV_val['A2_Modulbezeichnung'] = module[2][3]
                                    PV_val['A2_Nennleistung_Modul'] = module[2][4]
                                    PV_val['A2_Preis_Modul'] = module[2][5]
                                except Exception as e: 
                                    print(e)
                                    pass  
                                try: 
                                    PV_val['A3_Modulanzahl'] = module[3][1]
                                    PV_val['A3_Modulhersteller'] = module[3][2]    
                                    PV_val['A3_Modulbezeichnung'] = module[3][3]
                                    PV_val['A3_Nennleistung_Modul'] = module[3][4]
                                    PV_val['A3_Preis_Modul'] = module[3][5]
                                except Exception as e: 
                                    print(e)
                                    pass  
                                try: 
                                    PV_val['A1_WR_Anzahl'] = wechselrichter[1][1]
                                    PV_val['A1_WR_Hersteller'] = wechselrichter[1][2]    
                                    PV_val['A1_WR_Bezeichnung'] = wechselrichter[1][3]
                                    PV_val['A1_WR_Preis'] = wechselrichter[1][4]
                                except Exception as e: 
                                    print(e)
                                    pass   
                                try: 
                                    PV_val['A2_WR_Anzahl'] = wechselrichter[2][1]
                                    PV_val['A2_WR_Hersteller'] = wechselrichter[2][2]    
                                    PV_val['A2_WR_Bezeichnung'] = wechselrichter[2][3]
                                    PV_val['A2_WR_Preis'] = wechselrichter[2][4]
                                except Exception as e: 
                                    print(e)
                                    pass   
                                try: 
                                    PV_val['A3_WR_Anzahl'] = wechselrichter[3][1]
                                    PV_val['A3_WR_Hersteller'] = wechselrichter[3][2]    
                                    PV_val['A3_WR_Bezeichnung'] = wechselrichter[3][3]
                                    PV_val['A3_WR_Preis'] = wechselrichter[3][4]
                                except Exception as e: 
                                    print(e)
                                    pass    
                                try: 
                                    PV_val['A1_BS_Anzahl'] = speicher[1][1]
                                    PV_val['A1_BS_Hersteller'] = speicher[1][2]    
                                    PV_val['A1_BS_Bezeichnung'] = speicher[1][3]
                                    PV_val['A1_BS_Kapazitaet'] = speicher[1][4]
                                    PV_val['A1_BS_Preis'] = speicher[1][5]
                                except Exception as e: 
                                    print(e)
                                    pass 
                                try: 
                                    PV_val['A2_BS_Anzahl'] = speicher[2][1]
                                    PV_val['A2_BS_Hersteller'] = speicher[2][2]    
                                    PV_val['A2_BS_Bezeichnung'] = speicher[2][3]
                                    PV_val['A2_BS_Kapazitaet'] = speicher[2][4]
                                    PV_val['A2_BS_Preis'] = speicher[2][5]
                                except Exception as e: 
                                    print(e)
                                    pass  
                                try: 
                                    PV_val['A3_BS_Anzahl'] = speicher[3][1]
                                    PV_val['A3_BS_Hersteller'] = speicher[3][2]    
                                    PV_val['A3_BS_Bezeichnung'] = speicher[3][3]
                                    PV_val['A3_BS_Kapazitaet'] = speicher[3][4]
                                    PV_val['A3_BS_Preis'] = speicher[3][5]
                                except Exception as e: 
                                    print(e)
                                    pass   
                                try: 
                                    PV_val['A1_Komplettmontage'] = rest[1][0]
                                    PV_val['A1_Geruest'] = rest[1][1]    
                                    PV_val['A1_Mithilfe'] = rest[1][2]
                                    PV_val['A1_ACAnschluss'] = rest[1][3]
                                    PV_val['A1_Aufstaenderung'] = rest[1][4]
                                except Exception as e: 
                                    print(e)
                                    pass    
                                try: 
                                    PV_val['A2_Komplettmontage'] = rest[2][0]
                                    PV_val['A2_Geruest'] = rest[2][1]    
                                    PV_val['A2_Mithilfe'] = rest[2][2]
                                    PV_val['A2_ACAnschluss'] = rest[2][3]
                                    PV_val['A2_Aufstaenderung'] = rest[2][4]
                                except Exception as e: 
                                    print(e)
                                    pass     
                                try: 
                                    PV_val['A3_Komplettmontage'] = rest[3][0]
                                    PV_val['A3_Geruest'] = rest[3][1]    
                                    PV_val['A3_Mithilfe'] = rest[3][2]
                                    PV_val['A3_ACAnschluss'] = rest[3][3]
                                    PV_val['A3_Aufstaenderung'] = rest[3][4]
                                except Exception as e: 
                                    print(e)
                                    pass                                                                                                           
                            except Exception as e: 
                                print(e)
                                pass
                            
                            PVs.append(PV_val)
        print(f"Finished with page {i}")
    my_df = pd.DataFrame(PVs)
    my_df['PLZ'] = my_df.PLZ.str.strip() #remove trash \t\t\t\t\r ..
    
    return my_df

if __name__ == "__main__":
    
    ## --- Store the Dataframe --- ##
    my_df = scrape_pv(pages=11)
    my_df.to_csv('C:/Git/AzureLearn/.local/pv_prices.csv')

    # Define parameters
    connectionString = "https://sahrazurelearnadfdev.blob.core.windows.net/"
    containerName = "bronze"
    outputBlobName	= "pv_prices.csv"

    # Establish connection with the blob storage account
    blob = BlobClient.from_connection_string(conn_str=connectionString, container_name=containerName, blob_name=outputBlobName)
    with open(outputBlobName, "rb") as data:
        blob.upload_blob(my_df)