from selenium import webdriver
import undetected_chromedriver as uc
import threading
import time
import PySimpleGUI as sg
import requests
import os
import json
path = os.getcwd()
from pythonosc.udp_client import SimpleUDPClient
ip = "192.168.100.210"
port = 8000
client = SimpleUDPClient(ip, port)

poll_finish = False
thread_stop = False
current_state = "Waiting..."

def WebController(url):
    global driver
    global scan_active
    global current_state
    global thread_stop
    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        #driver = uc.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', options=options)
        driver.get("https://www.twitch.tv/popout/"+str(poll)+"/poll")
        scan_active = True
    except:
        current_state = "Webdriver Error"


def to_vMix(info_list):

    idx_question = "4"
    idx_vote = ""
    idx_score1 = "1"
    idx_score2 = "3"
    idx_name1 = "0"
    idx_name2 = "2"

    #return (title_txt, answer_list[0], scores_list[0], answer_list[1], scores_list[1], total_votes)

    txt_question = str(info_list[0])
    txt_reponse1 = str(info_list[1])
    txt_score1 = str(info_list[2])
    txt_reponse2 = str(info_list[3])
    txt_score2 = str(info_list[4])
    txt_score1 = txt_score1.replace(" ", "")
    txt_score2 = txt_score2.replace(" ", "")

    client.send_message("/score1/", txt_score1)
    client.send_message("/score2/", txt_score2)
    ##requests.post(vmix_url+"SetText&Input="+vmix_input+"&SelectedIndex="+idx_vote+"&Value="+"VOTES : "+str(info_list[5]))

    requests.post(vmix_url+"SetText&Input="+vmix_input+"&SelectedIndex="+idx_question+"&Value="+txt_question)
    requests.post(vmix_url+"SetText&Input="+vmix_input+"&SelectedIndex="+idx_score1+"&Value="+txt_score1+"%")
    requests.post(vmix_url+"SetText&Input="+vmix_input+"&SelectedIndex="+idx_score2+"&Value="+txt_score2+"%")
    requests.post(vmix_url+"SetText&Input="+vmix_input+"&SelectedIndex="+idx_name1+"&Value="+txt_reponse1)
    requests.post(vmix_url+"SetText&Input="+vmix_input+"&SelectedIndex="+idx_name2+"&Value="+txt_reponse2)



def Parse_Info():
    global answer_list,scores_list,current_state,thread_stop
    global current_score
    answer_list = []
    scores_list = []
    current_score = []
    votes = []
    print("Parsing info...")
    try:
        ##Get all the text field
        data_list = driver.find_elements_by_xpath("//p[contains(@class,\"sc-AxirZ\") and not(@class=\"sc-AxirZ ktnnZK\") and not(@class=\"sc-AxirZ epwTZM\") and not(@class=\"sc-AxjAm StDqN\")]")
        state = data_list[0].text
        title_txt = data_list[1].text
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
        current_score = [int(scores_list[0]),int(scores_list[1])]
        print("Title: ", title_txt)
        print("Answer_List: ", answer_list)
        print("Scores_list: ", scores_list)
        print("Total_Votes: ", total_votes)

        return (title_txt,answer_list[0],scores_list[0],answer_list[1],scores_list[1],total_votes)
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
            print(finish.text)
            scan_active = False
            current_state = "Sondage terminé"
            if not poll_finish:
                Ranking(current_score)
                poll_finish = True
    except:
        current_state = "Waiting..."
        scan_active = True


def Scan_Loop(poll):
    global scan_active
    global current_state
    global thread_stop
    global poll_finish
    current_state = "Loading URL..."
    WebController(poll)
    print("Scanning URL : ", poll)
    while True:
        time.sleep(0.25)
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


if __name__ == "__main__":
    poll = "3hitcombo"
    vmix_ip = "127.0.0.1"
    vmix_port = "8088"
    vmix_input = "Sondage_B"

    sg.theme('DarkBrown1')
    #[sg.Column(image_to_center, vertical_alignment='center', justification='center', k='-C-')],
    layout = [
                 [sg.Frame('Status :', layout=[
                     [sg.T(current_state, key='_STATE_',size=(18, 1))
                     ]]),sg.Image(filename="Logo_NES.png",tooltip=("nesprod.net / Romain.Desveaux@nesprod.net"), pad=((0, 0),(0,0)))],
                [sg.Text("vMix IP : ",size=(12, 1)),sg.Input(key='_VMIX_IP_',default_text=vmix_ip,justification="left",size = (15, 1))],
                [sg.Text("vMix Port : ",size=(12, 1)),sg.Input(key='_VMIX_PORT_',default_text=vmix_port,justification="left",size = (15, 1))],
                [sg.Text("vMix Input : ",size=(12, 1)),sg.Input(key='_VMIX_INPUT_',default_text=vmix_input,justification="left",size = (15, 1))],
                [sg.Text("Twitch Channel : ",size=(12, 1)),sg.Input(key='_URL_POLL_',size=(15,1),default_text=poll,)],
                [sg.Button('Start',key='_START_'),
                sg.Button('Stop', key='_STOP_',disabled=True),
                sg.Exit()],
            ]


    window = sg.Window('NES - Twitch Poll to vMix', layout, keep_on_top=True, auto_size_text=True,grab_anywhere = True,finalize=True,element_justification="left")

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
            vmix_ip = values['_VMIX_IP_']
            vmix_port = values['_VMIX_PORT_']
            vmix_input = values['_VMIX_INPUT_']
            vmix_url = "http://"+str(vmix_ip)+":"+str(vmix_port)+"/api/?Function="
            poll = values['_URL_POLL_']
            t = threading.Thread(target=Scan_Loop, args=(poll,))
            t.start()
            thread_stop = False

        if event == '_STOP_':
            window['_START_'].update(disabled=False)
            window['_STOP_'].update(disabled=True)
            thread_stop = True

    window.close()

