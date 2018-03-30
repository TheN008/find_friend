from BeautifulSoup import BeautifulSoup
import requests
import sys
import difflib

class unexpectedError(Exception):
    def __init__(self, msg="There was an unexpected error."):
        print msg

class friend_finder(object):

    def __init__(self, n):
        self.n = n
        self.firstname = n.split(" ")[0]
        self.lastname = n.split(" ")[-1]
        self.url = "http://locatefamily.com"


    def findPhoneNumber(self):

        first_character = self.lastname[0].upper()
        shortcut = self.lastname[0:3].upper() if len(self.lastname) > 3 else self.lastname.upper()
        i = 1
        details = []
        filtered_ul_elements = []
        first_names = []
        phone_numbers = []
        while True:
            j = 1
            prepared = "%s/%s/%s/%s-%d.html"%(self.url, first_character, shortcut, self.lastname.upper(), i)
            r = requests.get(prepared)
            if int(r.status_code) == 404:
                break
            parser = BeautifulSoup(r.text)
            all_ul_items = parser.findAll(itemtype="https://schema.org/Person")
            for element in  all_ul_items:
                try:
                    a = element.find(itemprop="givenName").b
                    filtered_ul_elements.append(element)
                except:
                    pass
            i += 1
        for elements in filtered_ul_elements:
                try:
                    firstName = elements.find(itemprop="givenName").b.string
                except:
                    try:
                        firstName = elements.find(itemprop="givenName").string
                    except:
                        continue
                if firstName.endswith('&nbsp;'):
                    firstName = firstName[:-6]
                try:
                    #phone_number = elements.find("a")["href"].encode("ascii")[4:]
                    ph_ob = elements.find(itemprop="telephone")
                    phone_number = ph_ob.a['href'].encode("ascii")[4:]
                except:
                    phone_number = None
                first_names.append(firstName)
                phone_numbers.append(phone_number)
        matches = difflib.get_close_matches(self.firstname, first_names)
        data = self.toDict(first_names, phone_numbers)
        informations = {}
        for m in matches:
            informations[m] = data[m]
        return informations



    @staticmethod
    def toDict(a,b): # converts two arrays into dictionary {key: value}
        if len(a) != len(b):
            raise unexpectedError()
            sys.exit(0)
        i = 0
        dictionary = {}
        while i<len(a):
            if a[i] in dictionary:
                if type([]) == type(dictionary[a[i]]):
                    dictionary[a[i]].append(b[i])
                else:
                    temp = []
                    temp.append(dictionary[a[i]])
                    temp.append(b[i])
                    dictionary[a[i]] = temp

            else:
                dictionary[a[i]] = b[i]
            i += 1
        return dictionary


name = raw_input("Enter your friend's name in format \"firstname lastname\":\n>>>")
f =  friend_finder(name)
phone_numbers = f.findPhoneNumber()
if len(phone_numbers)>0:
    count = 0
    print "Found some close name matches: "
    for key,value in phone_numbers.items():
        print "\tName:"
        print "\t\t%s %s"%(key, f.lastname)
        if type([]) == type(value):
            print "\tPhone numbers:"
            for i in value:
                print "\t\t%s"%i
        elif value == None:
            count += 1
        else:
            print "\tPhone number:"
            print "\t\t%s"%value

        if count  == len(phone_numbers):
            print "Sorry, there was an error and there was no number for your friend."
else:
    print "Sorry, found nothing."
