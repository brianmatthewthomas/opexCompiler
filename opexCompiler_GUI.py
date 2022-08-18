import sys

import PySimpleGUI as sg
import os
import lxml.etree as ET
import requests
import getpass
import configparser
import opexCreator.opexCreator
from opexCreator import opexCreator_3versions

def login(url, payload):
    auth = requests.post(url, data=payload).json()
    sessionToken = auth['token']
    headers = {'Preservica-Access-Token': sessionToken}
    headers['Content-Type'] = 'application/xml'
    headers['Accept-Charset'] = 'UTF-8'
    return headers



layout = [
    [
        sg.Radio("2-version crawler","radio1", default=False,key="-TYPE_2v-"),
        sg.Radio("3-version crawler","radio1", default=False,key="-TYPE_3v-"),
        sg.Radio("3-version crawler tree","radio1", default=False,key="-TYPE_3v-tree-")
    ],
    [
      sg.Checkbox("Use config file?", checkbox_color="dark green",key="-CONFIG-",tooltip="to pre-populate the necessary fields", enable_events=True)
    ],
    [
        sg.Push(),
        sg.Text("config file"),
        sg.In(size=(50,1), enable_events=True, key="-CONFIGFILE-"),
        sg.FileBrowse(file_types=(("text files only", "*.txt"),))
    ],
    [
        sg.Push(),
        sg.Button("Load", tooltip="Use this button to load the variables from the configfile"),
        sg.Push()
    ],
    [
        sg.Push(),
        sg.Text("upload staging location"),
        sg.In("", key="-UploadStaging-"),  # sg.In(size=(50, 1), enable_events=True, key="-UploadStaging-"),
        sg.FolderBrowse()
    ],
    [
        sg.Push(),
        sg.Text("root folder to start from", visible=False, key="-ROOT_Text-"),
        sg.Input("", size=(50,1), visible=False, key="-ROOT-"),
    ],
    [
        sg.Push(),
        sg.Text("main preservation folder", visible=False, key="-preservation_folder_Text-"),
        sg.Input("", size=(50, 1), visible=False, key="-preservation_folder-")
    ],
    [
        sg.Push(),
        sg.Text("intermediary folder", visible=False, key="-intermediary_folder_Text-"),
        sg.Input("", size=(50, 1), visible=False, key="-intermediary_folder-")
    ],
    [
        sg.Push(),
        sg.Text("main presentation folder", visible=False, key="-presentation_folder_Text-"),
        sg.Input("", size=(50, 1), visible=False, key="-presentation_folder-")
    ],
    [
        sg.Push(),
        sg.Text("Name of folder holding preservation files", visible=False, key="-preservation1_Text-"),
        sg.Input("", size=(50, 1), visible=False, key="-preservation1-")
    ],
    [
        sg.Push(),
        sg.Text("Name of folder holding intermediary files", visible=False, key="-presentation2_Text-"),
        sg.Input("", size=(50, 1), visible=False, key="-presentation2-")
    ],
    [
        sg.Push(),
        sg.Text("Name of folder holding presentation files", visible=False, key="-presentation3_Text-"),
        sg.Input("", size=(50, 1), visible=False, key="-presentation3-")
    ],
    [
        sg.Text("General variables", text_color="orchid1", font=("Calibri", "12", "underline"))
    ],
    [
        sg.Push(),
        sg.Text("Preservica Version:", key="-PreservicaVersion_TEXT-"),
        sg.Input("", size=(50, 1), key="-PreservicaVersion-")
    ],
    [
        sg.Push(),
        sg.Text("UUID to upload to", visible=True, key="-UUID_Text-"),
        sg.Input("", size=(50, 1), visible=True, key='-UUID-')
    ],
    [
        sg.Push(),
        sg.Text("Object type", visible=True, key="-TYPE_Text-"),
        sg.Input("", size=(50, 1), visible=True, key="-TYPE-")
    ],
    [
        sg.Push(),
        sg.Text("Delay in seconds", visible=True, key="-DELAY_Text-"),
        sg.Input("", size=(50, 1), visible=True, key="-DELAY-")
    ],
    [
        sg.Push(),
        sg.Text("When to start quiet time, leave blank if n/a", visible=True, key="-QUIET_Start_Text-"),
        sg.Input("", size=(50, 1), visible=True, key="-QUIET_Start-")
    ],
    [
        sg.Push(),
        sg.Text("When to end quiet time, leave blank if N/A", visible=True, key="-QUIET_End_Text-"),
        sg.Input("", size=(50, 1), visible=True, key="-QUIET_End-")
    ],
    [
        sg.Push(),
        sg.Text("Time to pause between uploads", visible=True, key="-INTERVAL_Text-"),
        sg.Input("", size=(50, 1), visible=True, key="-INTERVAL-")
    ],
    [
      sg.Checkbox("Implement Quiet time?", checkbox_color="dark green",key="-QuietTime-",tooltip="uploads from crawlers will pause during specified quiet time")
    ],
    [
        sg.Text("Upload variables", text_color="orchid1", font=("Calibri", "12", "underline"))
    ],
    [
        sg.Push(),
        sg.Text("Username:", key="-USERNAME_TEXT-"),
        sg.Input("", size=(50, 1), key="-USERNAME-")
    ],
    [
        sg.Push(),
        sg.Text("Password:", key="-PASSWORD_TEXT-"),
        sg.Input("", size=(50, 1), password_char="#", key="-PASSWORD-")
    ],
    [
        sg.Push(),
        sg.Text("Domain Prefix:", key="-PREFIX_TEXT-"),
        sg.Input("", size=(50, 1), key="-PREFIX-")
    ],
    [
        sg.Push(),
        sg.Text("Tenancy abbreviation:", key="-TENANCY_TEXT-"),
        sg.Input("", size=(50, 1), key="-TENANCY-")
    ],
    [
        sg.Text("Select execute to start processing")
    ],
    [
        sg.Push(),
        sg.Button("Execute", tooltip="This will start the program running."),
        sg.Push()
    ],
    [
        sg.Text("Select Close to close the window.")
    ],
    [sg.Button("Close",
               tooltip="Close this window. Other processes you started must be finished before this button will do anything.",
               bind_return_key=True)],
    [
        sg.ProgressBar(1, orientation="h", size=(50, 20), bar_color="dark green", key="-Progress-", border_width=5,
                       relief="RELIEF_SUNKEN")
    ],
    [
        sg.Text("", key="-STATUS-")
    ],
    [
        sg.Multiline(default_text="Click execute to show progress\n------------------------------", size=(70, 5),
                     auto_refresh=True, reroute_stdout=False, key="-OUTPUT-", autoscroll=True, border_width=5),
    ],
    ''''''
]

window = sg.Window(
    "Opex Compiler Graphical interface",
    layout,
    icon="opex_icon.png",
    button_color="dark green",

)

event, values = window.read()
while True:
    event, values = window.read()
    use_config = values["-CONFIG-"]
    configfile = values['-CONFIGFILE-']
    if values['-TYPE_2v-'] is True:
        opex_type = "2versions_crawler"
        window['-ROOT_Text-'].update(visible=False)
        window['-ROOT-'].update(visible=False)
        window['-preservation1_Text-'].update(visible=False)
        window['-preservation1-'].update(visible=False)
        window['-presentation2_Text-'].update(visible=False)
        window['-presentation2-'].update(visible=False)
        window['-presentation3_Text-'].update(visible=False)
        window['-presentation3-'].update(visible=False)
        window['-preservation_folder_Text-'].update(visible=True)
        window['-preservation_folder-'].update(visible=True)
        window['-intermediary_folder-'].update(visible=False)
        window['-intermediary_folder_Text-'].update(visible=False)
        window['-presentation_folder_Text-'].update(visible=True)
        window['-presentation_folder-'].update(visible=True)
    if values['-TYPE_3v-'] is True:
        opex_type = "3versions_crawler"
        window['-ROOT_Text-'].update(visible=False)
        window['-ROOT-'].update(visible=False)
        window['-preservation1_Text-'].update(visible=False)
        window['-preservation1-'].update(visible=False)
        window['-presentation2_Text-'].update(visible=False)
        window['-presentation2-'].update(visible=False)
        window['-presentation3_Text-'].update(visible=False)
        window['-presentation3-'].update(visible=False)
        window['-preservation_folder_Text-'].update(visible=True)
        window['-preservation_folder-'].update(visible=True)
        window['-intermediary_folder_Text-'].update(visible=True)
        window['-intermediary_folder-'].update(visible=True)
        window['-presentation_folder_Text-'].update(visible=True)
        window['-presentation_folder-'].update(visible=True)
    if values['-TYPE_3v-tree-'] is True:
        opex_type = "3versions_crawler_tree"
        window['-ROOT_Text-'].update(visible=True)
        window['-ROOT-'].update(visible=True)
        window['-preservation1_Text-'].update(visible=True)
        window['-preservation1-'].update(visible=True)
        window['-presentation2_Text-'].update(visible=True)
        window['-presentation2-'].update(visible=True)
        window['-presentation3_Text-'].update(visible=True)
        window['-presentation3-'].update(visible=True)
        window['-preservation_folder_Text-'].update(visible=False)
        window['-preservation_folder-'].update(visible=False)
        window['-intermediary_folder_Text-'].update(visible=False)
        window['-intermediary_folder-'].update(visible=False)
        window['-presentation_folder_Text-'].update(visible=False)
        window['-presentation_folder-'].update(visible=False)
    username = values['-USERNAME-']
    password = values['-PASSWORD-']
    tenancy = values['-TENANCY-']
    prefix = values['-PREFIX-']
    payload = {'username': username, 'password': password, 'tenant': tenancy}
    url = f"https://{prefix}.preservica.com/api/accesstoken/login"
    version = values['-PreservicaVersion-']
    namespaces = {'xip': f'http://preservica.com/XIP/v{version}',
                  'EntityResponse': f'http://preservica.com/EntityAPI/v{version}',
                  'ChildrenResponse': f'http://preservica.com/EntityAPI/v{version}',
                  'MetadataResponse': f'http://preservica.com/EntityAPI/v{version}',
                  'dcterms': 'http://dublincore.org/documents/dcmi-terms',
                  'tslac': 'https://www.tsl.texas.gov/'}
    object_type = values['--']
    if event == "Load":
        if use_config is True and configfile != "":
            config = configparser.ConfigParser()
            config.read(configfile)
            if opex_type == "3versions_crawler_tree":
                var = config.get('3_version_crawler_tree','root_folder')
                window['-ROOT-'].update(var)
                var = config.get('3_version_crawler_tree','preservation_folder')
                window['-preservation1-'].update(var)
                var = config.get('3_version_crawler_tree','intermediary_folder')
                window['-presentation2-'].update(var)
                var = config.get('3_version_crawler_tree','presentation_folder')
                window['-presentation3-'].update(var)
            if opex_type == "2versions_crawler":
                var = config.get('2_version_crawler','preservation_folder')
                window['-preservation_folder-'].update(var)
                var = config.get('2_version_crawler','presentation_folder')
                window['-presentation_folder-'].update(var)
            if opex_type == "3versions_crawler":
                var = config.get('3_version_crawler','preservation_folder')
                window['-preservation_folder-'].update(var)
                var = config.get('3_version_crawler','intermediary_folder')
                window['-intermediary_folder-'].update(var)
                var = config.get('3_version_crawler','presentation_folder')
                window['-presentation_folder-'].update(var)
            var = config.get('general','preservica_version')
            window['-PreservicaVersion-'].update(var)
            var = config.get('general','standard_directory_uuid')
            window['-UUID-'].update(var)
            var = config.get('general','object_type')
            window['-TYPE-'].update(var)
            var = config.get('general','delay')
            window['-DELAY-'].update(var)
            var = config.get('general','quiet_start')
            window['-QUIET_Start-'].update(var)
            var = config.get('general','quiet_end')
            window['-QUIET_End-'].update(var)
            var = config.get('general','interval')
            window['-INTERVAL-'].update(var)
            print("config file loaded")
            window['-OUTPUT-'].update("\nConfiguration loaded", append=True)
    if event == "Execute":
        if opex_type == "2versions_crawler":
            window['-OUTPUT-'].update("\nprocessing a 2 version opex directory", append=True)
            dirpath1 = values['-preservation_folder-']
            dirpath2 = values['-presentation_folder-']
        if opex_type == "3versions_crawler":
            window['-OUTPUT-'].update("\nprocessing a 3 version opex directory setup", append=True)
            dirpath1 = values['-preservation_folder-']
            dirpath2 = values['-presentation_folder-']
            dirpathA = values['-intermediary_folder-']
        if opex_type == "3versions_crawler_tree":
            window['-OUTPUT-'].update("\nprocessing a 3 version opex directory in a tree configuration", append=True)
            rooty = values['-ROOT-']
            dirpath1 = values['-preservation1-']
            dirpath2 = values['-presentation3-']
            dirpathA = values['-presentation2-']
    if event == "Close" or event == sg.WIN_CLOSED:
        break
window.close()
