from selenium import webdriver
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
import matplotlib.pyplot as plt
from datetime import date, timedelta

def spread_ratio(infections_today, infections_yesterday):
    return (infections_today / infections_yesterday)

def convert_to_int(string):
    string = string.replace('+', '')
    return int(string.replace('.', ''))

#Setting the dates
today = date.today()
yesterday = today - timedelta(days=1)
today = today.strftime("%d_%m_%Y")
yesterday = yesterday.strftime("%d_%m_%Y")

#Connection
cred = credentials.Certificate('/Users/leonsick/PycharmProjects/WebAutomation/YOURCERTIFICATE.json')
firebase_admin.initialize_app(cred,
                              {
                                  'databaseURL': 'YOURURL'
                              })
ref = db.reference('/')

#print(ref.get())
#Getting the data from today
browser = webdriver.Chrome('/Users/leonsick/Desktop/Developer/Webautomation Chrome/ChromeDriver/chromedriver')
browser.get('https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html')

#For Germany
cases_ger = browser.find_element_by_xpath('//*[@id="main"]/div[1]/table/tbody/tr[17]/td[2]').text
diff_ger = browser.find_element_by_xpath('//*[@id="main"]/div[1]/table/tbody/tr[17]/td[3]').text

#For Baden-Württemberg
cases_bw = browser.find_element_by_xpath('//*[@id="main"]/div[1]/table/tbody/tr[1]/td[2]').text
diff_bw = browser.find_element_by_xpath('//*[@id="main"]/div[1]/table/tbody/tr[1]/td[3]').text

#Converting it to integers
#For Germany
cases_ger = convert_to_int(cases_ger)
diff_ger = convert_to_int(diff_ger)

#For Baden-Württemberg
cases_bw = convert_to_int(cases_bw)
diff_bw = convert_to_int(diff_bw)

#Getting yesterday's data
#TODO: Get all data that is currently in the db and use .set() to add ALL DATA plus the new data
key_query = ref.order_by_key().limit_to_last(1).get()
key_yesterday = next(iter(key_query))
print(key_yesterday)
query_ref_ger = ref.child(key_yesterday).child(yesterday).child('cases_ger')
query_ref_bw = ref.child(key_yesterday).child(yesterday).child('cases_bw')
cases_ger_yesterday = query_ref_ger.get()
cases_bw_yesterday = query_ref_bw.get()

#Calculating the spread ratio for today
spread_ratio_ger = spread_ratio(cases_ger, cases_ger_yesterday)
spread_ratio_bw = spread_ratio(cases_bw, cases_bw_yesterday)

#Uploading the data
new_data_ref = ref
new_data_ref.push({
            today:{
                'cases_ger': cases_ger,
                'diff-ger': diff_ger,
                'cases_bw': cases_bw,
                'diff_bw': diff_bw,
                'spread_ratio_ger': spread_ratio_ger,
                'spread_ratio_bw': spread_ratio_bw
            }
})


#Data analysis

#print(ref.order_by_key().get())
cases_ger_list = []
cases_bw_list = []
spread_ratio_ger_list = []
spread_ratio_bw_list = []
days = []

keys = ref.order_by_key().get()
for key in keys:
    dates = ref.child(key).get()
    for date in dates:
        cases_ger_list.append(ref.child(key).child(date).child('cases_ger').get())
        cases_bw_list.append(ref.child(key).child(date).child('cases_bw').get())
        spread_ratio_ger_list.append(ref.child(key).child(date).child('spread_ratio_ger').get() - 1)
        spread_ratio_bw_list.append(ref.child(key).child(date).child('spread_ratio_bw').get() - 1)
        days.append(date)

#plt.plot(x-axis, y-axis)
plt.plot(days, spread_ratio_ger_list)
plt.show()
