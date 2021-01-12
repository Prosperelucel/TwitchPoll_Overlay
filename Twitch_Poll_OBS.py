from selenium import webdriver
import threading
import time
import PySimpleGUI as sg
import requests
from obswebsocket import obsws, requests, events

poll_finish = False
thread_stop = False
current_state = "Waiting..."

host = "localhost"
port = 4444
password = "cacaprout"
ws = obsws(host, port, password)
ws.connect()


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
        options.add_argument('--headless')
        driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', options=options)
        driver.get(url)
        scan_active = True
    except:
        current_state = "Webdriver Error"

def to_OBS(info_list):
    ws.call(requests.SetTextGDIPlusProperties(source="question", text=str(info_list[0])))
    ws.call(requests.SetTextGDIPlusProperties(source="r01", text=str(info_list[1])))
    ws.call(requests.SetTextGDIPlusProperties(source="r02", text=str(info_list[3])))
    ws.call(requests.SetTextGDIPlusProperties(source="r03", text=str(info_list[5])))
    ws.call(requests.SetTextGDIPlusProperties(source="r04", text=str(info_list[7])))
    ws.call(requests.SetTextGDIPlusProperties(source="prct01", text=str(info_list[2])))
    ws.call(requests.SetTextGDIPlusProperties(source="prct02", text=str(info_list[4])))
    ws.call(requests.SetTextGDIPlusProperties(source="prct03", text=str(info_list[6])))
    ws.call(requests.SetTextGDIPlusProperties(source="prct04", text=str(info_list[8])))
    ws.call(requests.SetTextGDIPlusProperties(source="total", text=str(info_list[9])+str(" VOTES")))


def Parse_Info():
    global answer_list,scores_list,current_state,thread_stop
    global current_score
    answer_list = []
    scores_list = []
    current_score = []
    votes = []
    print("Parsing info...")
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

        current_score = [int(scores_list[0]),int(scores_list[1]),int(scores_list[2]),int(scores_list[3])]
        print("Title: ", title_txt)
        print("Answer_List: ", answer_list)
        print("Scores_list: ", scores_list)

        return (title_txt,answer_list[0],scores_list[0],answer_list[1],scores_list[1],answer_list[2],scores_list[2],answer_list[3],scores_list[3],total_votes)
    except:
        current_state = "Parsing error..."
        print("Parsing error...")
        return

def Check_Poll():
    global current_state
    global thread_stop
    global scan_active
    global poll_finish
    try:
        finish = driver.find_element_by_xpath("//p[contains(@data-test-selector,\"header\")]")
        if finish.text == "Sondage terminé":
            print("Sondage terminé")
            scan_active = False
            current_state = "Sondage terminé"
            if not poll_finish:
                poll_finish = True
    except:
        current_state = "Waiting..."
        scan_active = True


def Scan_Loop(url):
    global scan_active
    global current_state
    global thread_stop
    global poll_finish
    current_state = "Loading URL..."
    WebController(url)
    print("Scanning URL : ", url)
    while True:
        time.sleep(1)
        try:
            Check_Poll()
            if scan_active:
                current_state = "Scanning..."
                infos = Parse_Info()
                print("Infos : ",infos)
                if infos:
                    to_OBS(infos)
                else:
                    current_state = "Aucun sondage en cours..."
                    poll_finish = False

            if thread_stop:
                current_state = "Stopped"
                break
        except:
            current_state = "Error"

def GUI():
    global thread_stop
    global current_state
    sg.theme('DarkBrown1')
    #[sg.Column(image_to_center, vertical_alignment='center', justification='center', k='-C-')],
    layout = [
                 [sg.Frame('Status :', layout=[
                     [
                         sg.T(current_state, key='_STATE_',size=(18, 1))
                     ]])],
                [sg.Input(key='_URL_POLL_',default_text="https://www.twitch.tv/popout/2hdp/poll")],
                [sg.Button('Start',key='_START_'),
                sg.Button('Stop', key='_STOP_',disabled=True),
                sg.Exit()],
            ]


    window = sg.Window('2HDP - Twitch Poll to OBS', layout, keep_on_top=True, auto_size_text=True)

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

