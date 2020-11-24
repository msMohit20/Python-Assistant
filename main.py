# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# def print_hi(name):
# Use a breakpoint in the code line below to debug your script.
#  print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#   print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import pyttsx3
import speech_recognition as sr
import re
import requests
import json
import threading
import time
API_KEY = "tMmXP1AM0TaZ"
PROJECT_TOKEN = "teT6Sw9hdOkN"
RUN_TOKEN = "timNTQPyxa08"

#printing all data once for checking that every data has transfered properly.
#print(data['total'])

class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key" : api_key
        }
        self.data = self.get_data()
# this for upper statement: here is the part where data will be update from it own site means it will call in the parse hub and it will rerun the whole project and get recent data.

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data',
                                params={"api_key": API_KEY})
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        data = self.data['total']
        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['selection1']
        print()

    def get_total_deaths(self):
        data = self.data['total']
        for content in data:
            if content['name'] == "Deaths:":
                return content['selection1']
        print()

    def get_total_recovered(self):
        data = self.data['total']
        for content in data:
            if content['name'] == "Recovered:":
                return content['selection1']
        print()

    def get_country_data(self, country):
        data = self.data['country']
        for content in data:
            if content['name'].lower() == country.lower():
                return content
        print()

    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower())

        return countries

    def update_date(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/run', params={"api_key": API_KEY})
        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data Updated")
                    break
                time.sleep(5)
        t = threading.Thread(target=poll)
        t.start()

# data = Data(API_KEY, PROJECT_TOKEN)
# write here or in main function both will okay.

# print(data.get_country_data("usa")['total_case'])
# single quote is necessary in total_case remind that.

# print(data.get_list_of_countries())
# here is print the total name og country which are used in the list.

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# speak("Hello yash how are you?")
# here we get sound as output

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio= r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception is :", str(e))
    return said.lower()
# pip install sounddevice <--- important to run here.
#print(get_audio())

def main():
    print("Start program : ")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop"
    result = None
    country_list = data.get_list_of_countries()
    TOTAL_PATTERNS = {
        re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total [\w\s]+ recovered"): data.get_total_recovered,
        re.compile("[\w\s]+ total recovered"): data.get_total_recovered
    }

    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_case'],
        re.compile("[\w\s]+ case [\w\s]+"): lambda country: data.get_country_data(country)['total_case'],
        re.compile("[\w\s]+ dealths [\w\s]+"): lambda country: data.get_country_data(country)['total_dealth'],
        re.compile("[\w\s]+ dealth [\w\s]+"): lambda country: data.get_country_data(country)['total_dealth']
    }

    UPDATE_COMMAND = "update"

    while True:
        print("Listening.....")
        text = get_audio()
        print(text)

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                break

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break
        if text == UPDATE_COMMAND:
            result = "DATA is being get updated on the server wait to refresh."
            data.update_date()

        if result:
            speak(result)

        if text.find(END_PHRASE) != -1: # stop the loop from getting in infinite
            print("Exit")
            break

#calling function
main()
