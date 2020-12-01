from bs4 import BeautifulSoup
from selenium import webdriver
import threading
import time
import PySimpleGUI as sg
import requests

thread_stop = False
current_state = "Waiting..."

def Start_Threads():
    t01 = threading.Thread(target=GUI)
    t01.start()

def WebController(url):
    global driver
    global scan_active
    global current_state
    global thread_stop
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--mute-audio')
        options.add_argument('--disable-gpu')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--headless')
        driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', options=options)
        driver.get(url)
        scan_active = True
    except:
        current_state = "Webdriver Error"


def to_vMix(info_list):
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=0&Value="+str(info_list[0]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=2&Value="+str(info_list[1]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=1&Value="+str(info_list[2]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=4&Value="+str(info_list[3]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=3&Value="+str(info_list[4]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=6&Value="+str(info_list[5]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=5&Value="+str(info_list[6]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=8&Value="+str(info_list[7]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=7&Value="+str(info_list[8]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=9&Value="+str(info_list[9])+str(" VOTES"))



def Parse_Info():
    global answer_list,scores_list,current_state,thread_stop
    answer_list = []
    scores_list = []
    votes = []
    try:
        ##Get Title
        title = driver.find_elements_by_xpath("//p[contains(@class,\"tw-c-text-overlay tw-font-size-4 tw-line-height-heading tw-strong tw-word-break-word\")]")
        for txt in title:
            title_txt = txt.text
        ##Get Answer
        answers = driver.find_elements_by_xpath("//p[contains(@data-test-selector,\"title\")]")
        for txt in answers:
            answer_list.append(txt.text)
        ##Get Score
        scores = driver.find_elements_by_xpath("//p[contains(@data-test-selector,\"Count\")]")
        for txt in scores:
            score_txt = txt.text
            split_string = score_txt.split("%", 1)
            #scores_list.append(split_string[0]+str("%"))
            scores_list.append(split_string[0])
            vote = split_string[1].replace("(","")
            vote = vote.replace(")","")
            vote = vote.replace(" ","")
            votes.append(int(vote))
        total_votes = sum(votes)

        return (title_txt,answer_list[0],scores_list[0],answer_list[1],scores_list[1],answer_list[2],scores_list[2],answer_list[3],scores_list[3],total_votes)
    except:
        current_state = "Parsing error..."
        return

def Check_Poll():
    global current_state
    global thread_stop
    try:
        finish = driver.find_element_by_xpath("//div[contains(@id,\"root\")]")
        if finish.get_attribute("data-a-page-loaded-name") == "RootPollPage":
            print("Title = No Content")
            current_state = "Poll Finished"
    except:
        return

def Scan_Loop(url):
    global scan_active
    global current_state
    global thread_stop
    current_state = "Loading URL..."
    WebController(url)
    print("Scanning URL : ", url)
    while True:
        time.sleep(1)
        try:
            if scan_active:
                current_state = "Scanning..."
                #Check_Poll()
                infos = Parse_Info()
                print("Infos : ",infos)
                if infos:
                    to_vMix(infos)
                else:
                    current_state = "Poll Finished"
            if thread_stop:
                current_state = "Stopped"
                break
        except:
            current_state = "Error"

def GUI():
    global thread_stop
    global current_state
    sg.theme('DarkBrown1')
    layout = [
                 [sg.Frame('Status :', layout=[
                     [
                         sg.T(current_state, key='_STATE_',size=(38, 1))
                     ]])],
                [sg.Text('Poll URL :')],
                [sg.Input(key='_URL_POLL_')],
                [sg.Button('Start',key='_START_'),
                sg.Button('Stop', key='_STOP_',disabled=True),
                sg.Exit()]
            ]


    window = sg.Window('2HDP - Twitch Poll to vMix', layout, keep_on_top=True, auto_size_text=True)

    while True:
        event, values = window.read(timeout=1000)
        print(event, values)
        window['_STATE_'].update(current_state)
        if event == sg.WIN_CLOSED or event == 'Exit':
            thread_stop = True
            break
        if event == '_START_':
            window['_START_'].update(disabled=True)
            window['_STOP_'].update(disabled=False)
            url = values['_URL_POLL_']
            t = threading.Thread(target=Scan_Loop, args=(url,))
            t.start()
            thread_stop = False
        if event == '_STOP_':
            window['_START_'].update(disabled=False)
            window['_STOP_'].update(disabled=True)
            thread_stop = True

    window.close()

if __name__ == "__main__":
    Start_Threads()

