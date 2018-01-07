from bs4 import BeautifulSoup
from urllib2 import urlopen
import requests
import json

urls = ["http://www.cphm.ca/company/roster/companyRosterView.html?companyRosterId=5&page={}".format(i) for i in range(1, 10)]
pharmacy_list = {}
iterator = 0

# for each url in urls
for url in urls:
    headers = {'User-Agent': 'Mozilla/5.0'}

    # get the data from the page
    response = requests.get(url, headers=headers)
    data = response.text

    # create soup
    soup = BeautifulSoup(data, "lxml")
    colsm = soup.find("div", "col-sm-12")
    pharmacyTables = colsm.find_all('table')

    # for each pharmacy table in col-sm-12
    for pharmacy in colsm.find_all('table'):

        # get the pharmacy information
        pharmacyName = pharmacy.tbody.tr.td.string
        pharmacyAddressRaw = pharmacy.tbody.tr.find_next_sibling('tr')   # pharmacyAddress.td.text
        pharmacyPhone = pharmacyAddressRaw.td.find_next_sibling('td')    # pharmacyPhone.text

        # pharmacyAddress = pharmacyAddress.td.text
        # pharmacyAddress = pharmacyAddress[0:pharmacyAddress.find("Canada")]
        pharmacyAddress = pharmacyAddressRaw.td.br.previous_sibling
        pharmacyFullCity = pharmacyAddressRaw.td.br.next_sibling

        pharmacyCommaIndex = pharmacyFullCity.find(",")
        print(pharmacyFullCity[:pharmacyCommaIndex])
        print(pharmacyFullCity[pharmacyCommaIndex + 2:])
        pharmacyFullProvince = pharmacyFullCity[pharmacyCommaIndex + 2:]
        pharmacyPostalIndex = pharmacyFullProvince.find("R")

        # pharmacyPostal = pharmacyCity
        pharmacyCity = pharmacyFullCity[:pharmacyCommaIndex]
        pharmacyProvince = pharmacyFullCity[pharmacyCommaIndex + 2:pharmacyFullCity.find('R') - 1]
        pharmacyPostal = pharmacyFullProvince[pharmacyPostalIndex:]
        pharmacyPhone = pharmacyPhone.text

        # find the part of the string that we want
        faxStartIndex = pharmacyPhone.find("Fax")
        licenseStartIndex = pharmacyName.find("License")
        licenseEndIndex = licenseStartIndex + 15
        pharmacyLicense = pharmacyName[licenseStartIndex+9:licenseEndIndex]
        pharmacyName = pharmacyName[:licenseStartIndex]

        if faxStartIndex == 37:
            pharmacyFax = pharmacyPhone[43:57]
        elif faxStartIndex == 52:
            pharmacyFax = pharmacyPhone[58:72]
        else:
            pharmacyFax = ""

        # create a json list of the pharmacy info
        json_list = {
            'pharmacy': {
                        'name': pharmacyName,
                        'address': pharmacyAddress,
                        'city': pharmacyCity,
                        'province': pharmacyProvince,
                        'postal': pharmacyPostal,
                        'fax': pharmacyFax,
                        'license': pharmacyLicense
                        }
        }

        # add the pharmacy json to the pharmacy list
        pharmacy_list[iterator] = json_list

        # add an iteration
        iterator += 1

json_str = json.dumps(pharmacy_list)

f = open("manitoba_pharmacy_data.json", 'w')
f.write(json_str)
f.close()

print('finished parsing')
