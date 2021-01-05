from selenium import webdriver
import threading
import time
import PySimpleGUI as sg
import requests

poll_finish = False
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
        options.add_argument('--headless')
        driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', options=options)
        driver.get(url)
        scan_active = True
    except:
        current_state = "Webdriver Error"


def to_vMix(info_list):
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=0&Value="+str(info_list[0]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=1&Value="+str(info_list[1]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=2&Value="+str(info_list[1]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=3&Value="+str(info_list[2]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=4&Value="+str(info_list[3]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=5&Value="+str(info_list[3]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=6&Value="+str(info_list[4]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=7&Value="+str(info_list[5]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=8&Value="+str(info_list[5]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=9&Value="+str(info_list[6]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=10&Value="+str(info_list[7]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=11&Value="+str(info_list[7]))
    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=12&Value="+str(info_list[8]))

    requests.post("http://localhost:8088/api/?Function=SetText&Input=sondage&SelectedIndex=13&Value="+str(info_list[9])+str(" VOTES"))



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

def Ranking(current_score):
    print ("Current_Score: ",current_score)
    print ("Sum: ", sum(current_score))
    if sum(current_score) != 0:
        max_value = max(current_score)
        max_index = current_score.index(max_value)
        if max_index == 0:
            a1_lead = True
            a2_lead = False
            a3_lead = False
            a4_lead = False
        if max_index == 1:
            a1_lead = False
            a2_lead = True
            a3_lead = False
            a4_lead = False
        if max_index == 2:
            a1_lead = False
            a2_lead = False
            a3_lead = True
            a4_lead = False
        if max_index == 3:
            a1_lead = False
            a2_lead = False
            a3_lead = False
            a4_lead = True
        if a1_lead:
            requests.post("http://localhost:8088/api/?Function=TitleBeginAnimation&Input=sondage&Value=Page2")
        if a2_lead:
            requests.post("http://localhost:8088/api/?Function=TitleBeginAnimation&Input=sondage&Value=Page3")
        if a3_lead:
            requests.post("http://localhost:8088/api/?Function=TitleBeginAnimation&Input=sondage&Value=Page4")
        if a4_lead:
            requests.post("http://localhost:8088/api/?Function=TitleBeginAnimation&Input=sondage&Value=Page5")

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
                Ranking(current_score)
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
                    to_vMix(infos)
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
    image_to_center = [[sg.Image(filename="logo2hdp.png")]]
    #[sg.Column(image_to_center, vertical_alignment='center', justification='center', k='-C-')],
    layout = [
                 [sg.Frame('Status :', layout=[
                     [
                         sg.T(current_state, key='_STATE_',size=(18, 1))
                     ]]),sg.Image(filename="logo2hdp.png")],
                [sg.Input(key='_URL_POLL_',default_text="https://www.twitch.tv/popout/2hdp/poll")],
                [sg.Button('Start',key='_START_'),
                sg.Button('Stop', key='_STOP_',disabled=True),
                sg.Exit()],
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

