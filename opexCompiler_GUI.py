import configparser
import os

import PySimpleGUI as Sg
import lxml.etree as ET
import requests
from pydub import AudioSegment
from pydub.playback import play

import opexCreator.opexCreator
from opexCreator import opexCreator_3versions



def login(login_url, login_payload):
    auth = requests.post(login_url, data=login_payload).json()
    session_token = auth['token']
    login_headers = {'Preservica-Access-Token': session_token, 'Content-Type': 'application/xml',
                     'Accept-Charset': 'UTF-8'}
    return login_headers

def finished(myAudio):
    sound = AudioSegment.from_file(myAudio, type="wav")
    play(sound)


# set some variables as a sacrifice to the best practices gods
opex_type = ""
quiet_start = ""
quiet_end = ""
interval = ""
config = ""

# the real code
my_icon = b'iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAMAAAAOusbgAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdT' \
          b'AAAOpgAAA6mAAAF3CculE8AAACi1BMVEUAAABVqlU8pUtEnkRDoUhDoUhHnEdCoEZEn0dEoEhDoEhDoEdDoEdDoEdCoUdAqkBEoUdE' \
          b'n0dEoEdDoEdDoEhDoEhCn0hHo0dDoUhDoEdDoEdEn0dEoEZAn0pAn0BCn0ZEoUdDoEdEoEdGokZDoEdDoEdDoEdCnEpDoEZDoEZDoE' \
          b'dEoUdAo0dApElDoEdDoUdFnUVAv0BDoUdDoEdEn0hEokhDoEZDoEdBoEVNmU1DoEdDoEc5qlVGn0ZDoEdGokZJkklDn0hEoEhDoUhJ' \
          b'pElDoUNDoEZGokZAn0hGokZDoEdDoEZJnklDoUdDoEdDm0M7nU5DoEhDoEZCoEdBoEdDoEdEokRDoUdCoEdCoUdCoEdDoEdDoEdDoE' \
          b'dCn0hBn0hEn0lCoUZDoUZDoEhDoEdDoEdEoEdFoEhDoUdDn0dDoUdBoEhVqlWAgIBEoEdDn0dDn0ZGnkYzmTNDoEdCn0dDoUZDoEdC' \
          b'oEhDn0ZEoEdDoEdDn0dApk1DoUdDoEdDoEdDoEdCoElCoEhDoEdDoUdFn0VDoEdCoEZDoEdCoUdDoEdDn0dDoEhEmURDoEZDoEdDn0' \
          b'ZFoklCoEdDoEdCoUdCn0dDn0dBnUdDoEdEoEcA/wBCnkZDoEdEn0ZCoEdCoEdCoUhDoEdDoEdDn0dEn0dDoEdEoEZDoUpDoEZEokRE' \
          b'n0pEoEdCnkZCn0ZCoEhDoEdCoUZDnklEokhDoUZDoEdDoEZDn0ZEoEdDn0dDoEdEn0hDoUhDoEdDoUZDn0dCoEZCoUdCnkdEoEhDoE' \
          b'dDoEdDoEdDoEdEoEdDn0ZDoEZCoUhCoEVDoEdCoUdDoUhDn0dDoEdDoEdBnUhBoEZEoEZAn0BDoEdDoEf///9cfCvaAAAA13RSTlMA' \
          b'BhEiLjkSPmWLstr62WQMRIjM/d2ZVRlyyfzIcRgITaq7XguM8fAfkfb5oiQcn50aBG/0gDzS0TsKm/4JKNYsB6C5vQ4TxxYgIeXkFd' \
          b'jcFw3LnGEr9SnQ05qWc85+YEo4SV9u8uGPQ0GN4E4DAktIRR0F911XiVlQVreFFIKz+8IjxPPFJb90rK34kGMPhnaVP9fNd2h9L+fb' \
          b'AULvYryph+zVsFqBaSajHi2eOsCOlH8qR0zmp5hTPeN1at+KqIOlMnzBw8+2l1hbUUbibFy4xsonM2YQr1TiNPUAAAABYktHRNgADU' \
          b'euAAAAB3RJTUUH5gMSCgkxPPKJXgAABj1JREFUaN7tW/tfVFUQvywuzxUWVlBRQHnJQ1zegqCCaECCIPFQDMg0yARCKDJfq4CFQKVY' \
          b'moZaWFmIYlr0tKeU9rDsdf6d+vCJ3dm7986Zu3tuH39wftz7PfPdPTtnZs7MXEl6IPe5eBm85xiNc7wNXv8Xo4+vn39AoInZxTQ3wD' \
          b'/I16ArabA5JNTClGVeWLhO5PMXLIxgqEQsWhwpmjUqeomJEcSyNCZW5I+Ni2dkSfAX9bOXJSYxTZKcslwAbeoKE9MsJmuah7TpGfHM' \
          b'LcnM8uiAZ+cwt2Vlrtu0eavymQeSH1bgHu/qHOahrFnrDm9MJvNYkvw00xYWMSFi1WhjweuYICler4V3w0NMmISW0HlL5zKBMo/sx8' \
          b'oeZkJlYymNt7yCCZZNlRTeqlAmXDZXEZKpdUwHKS7kEhcxXaSax/sI00licN6aWr2IM+sw3oJ6pptsyUOItzIdpQGJ+/l6EucbVfOc' \
          b'eqar5KSrEG8j53KPWhubms3Gx8zbH2+sDk2mrtuhkk/uJK1+oqVV5g28ntz1FGlp/HxF4hUkF7S7TWlte8dSyupVirGQkD+veVrdMj' \
          b'u3EFL9PQoLGwhpI3YUpa4sC1dFosL9qJtrUs/w/O2zXDNLcg2Q/rw13R380GbmetweF2fJu6okd1CCeSdv3xLkSf5zvIvvXlr6Es37' \
          b'n5+XLdjHwe935Tjg7V3u+ulBjqJDMtOy4fDDMm93pLF3xt309WcddX7S9gKuyeac7b7IQTtfgo4OgGiSf8yZevkgrivDCb0QBw85gf' \
          b'1ktls77PR4F66rH2Jfwus5mT4Q/LIr4CB8bsBvezaYce7WEMJf4e7fcVxbM4C24K6yBkBPKG6ODQb5OjyfiAPQlfi1CzoalQA4As0e' \
          b'vxKcBJdD/NQ3Ap2vqoFeA6BTuC9ylB598T/lNLivv64GOtPuQJ3G9WU7zgfuXs86VIarw95woM6OogrP2YFxKO482MQLNNMvJkaoQy' \
          b'juTfBT3lKHjQHiEFThRTsuEMU1ORSuxYrGedQb2Igdh3vXVofCtzEcOMqteEphN1XcCEEMeAfDvevAXcI1ds0GVhxWRXSGWaCqgGuc' \
          b'df2lOAwk0u9huBYQlHGN7/8HG8eTLWCtARjwMgDiOfqs75/A/QfQdwUDHgPABEYxQ0HEA5qJBW21VfNWCzKuq5qNawMOA+XXSQx3zY' \
          b'FbTztOHAdSRwy0wIF8QHMgHJd53aHwBtFlXsdvbnYcXiUOcihMw4IE6O0FEYMEHhaBR5I+pIXFIWJYxBOBXqDxI3XYFID1ExMBPPWp' \
          b'BQnkx+owMzhNmcTU5xPcCEHLrOtTSrKXjeubcLTf8fTWH2ziZ2qgzwGoh5reSnhJLxB2sL9QxlR0AVAFNaGXrpL3WvJVvMJYTgAIHn' \
          b'TYTVhAwKEXJN5dYhtEfIlr2w6vqXhBwLYM6t3vCvgKPt+DhyaTU2NkEf4lv3a6eQfJTkttkNPjFEZ2C5K0gFPTy3augCwBxyB/wLmT' \
          b'9o1FSwk3klN8yZGVp8q+/W4myYi/deqIbHBjmlMflLUav+dUiX5wLSwZvL19XD+d5CgKkOFv82qBTbQC2x2eHnmBrSCBs8D2I4W3g1' \
          b'd7Ho2SL7nJ+6qDNwilTO6oSojLmkhu2dgW43nZuFahr3qcX2BPQQvlhSH8QvmQ0kgPoTUw0qzO+xOhNTCYqrTSSmlnXNmr3AyJLqas' \
          b'nlL8ymm09s/PiZ0ybxLV2kJr/4yqdM4XUxtXtvqirOFo84TRHH3u2uVp8vjTL2otvmmmq5xsU7OPXF2bmhajumVO6Uk8ic0E1uvHm4' \
          b'MOWV3aqRdv32rc693Wi/guz99a9eEN4waYrl/14D1PGOvK+008771gSjA/MCKa9wxxpKt0o1he6ljVv8xCB6s2aRiI9RH4P28u1zK0' \
          b'F7tPmD1XSZrEq1rQ+e3SPJl5t0+An7zjzijq7x5HjLEa94ZvCxo8is+WySi3543/uOc+77TRkwHr9j8T3KNNyGjzdHB/a7J22uQpEQ' \
          b'P8lSEaB/kGw1IFvTdQ2aNhw0dDSiRxUkh8QSNC7AsaM1KS0cupV9hu7SiXdJFY9ZdwLGNh4X9Jeoohe7jnYgWo6XeP/N0znKsvKbzu' \
          b'GMrGjcbxMkO69EDuc/kH6DhA657cRLAAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjItMDMtMThUMTA6MDk6NDkrMDA6MDAF5/xCAAAAJX' \
          b'RFWHRkYXRlOm1vZGlmeQAyMDIyLTAzLTE4VDEwOjA5OjQ5KzAwOjAwdLpE/gAAAABJRU5ErkJggg=='
# config file template
config_template = '''#NOTE: folders need to be relative to where you start the program or absolute! NOT NOT NOT based on where this config file lives\n#NOTE: you will need to enter the config file relative filepath when accessing it.\n[general]\npreservica_version = \nstandard_directory_uuid = \nsuffix_count = 3\nobject_type = multi-page document\ndelay = 300\nquiet_start = 08:00:00\nquiet_end = 08:00:01\ninterval = 300\nsound = \nexport_location = \n[2_version_crawler]\npreservation_folder = \npresentation_folder = \n[3_version_crawler]\npreservation_folder = \nintermediary_folder = \npresentation_folder = \n[3_version_crawler_tree]\nroot_folder = \npreservation_folder = preservation1\nintermediary_folder = presentation2\npresentation_folder = presentation3'''
Sg.theme('DarkGreen5')
layout = [
    [
        Sg.Radio("2-version crawler", "radio1", default=False, key="-TYPE_2v-"),
        Sg.Radio("3-version crawler", "radio1", default=False, key="-TYPE_3v-"),
        Sg.Radio("3-version crawler tree", "radio1", default=False, key="-TYPE_3v-tree-"),
        Sg.Button("Push to Update")
    ],
    [
        Sg.Checkbox("Use config file?", checkbox_color="dark green", key="-CONFIG-",
            tooltip="to pre-populate the necessary fields", enable_events=True),
        Sg.Push(),
        Sg.Text("Generate config file template?"),
        Sg.Button("Generate",tooltip="Click to generate a blank configfile you can fill in")
    ],
    [
        Sg.Push(),
        Sg.Text("config file"),
        Sg.In(size=(50, 1), enable_events=True, key="-CONFIGFILE-"),
        Sg.FileBrowse(file_types=(("text files only", "*.txt"),))
    ],
    [
        Sg.Push(),
        Sg.Button("Load", tooltip="Use this button to load the variables from the configfile"),
        Sg.Push()
    ],
    [
        Sg.HorizontalSeparator(),
    ],
    [
        Sg.Push(),
        Sg.Text("upload staging location"),
        Sg.In("", key="-UploadStaging-"),  # Sg.In(size=(50, 1), enable_events=True, key="-UploadStaging-"),
        Sg.FolderBrowse()
    ],
    [
        Sg.Push(),
        Sg.Text("root folder to start from", visible=False, key="-ROOT_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-ROOT-"),
    ],
    [
        Sg.Push(),
        Sg.Text("main preservation folder", visible=False, key="-preservation_folder_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-preservation_folder-")
    ],
    [
        Sg.Push(),
        Sg.Text("intermediary folder", visible=False, key="-intermediary_folder_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-intermediary_folder-")
    ],
    [
        Sg.Push(),
        Sg.Text("main presentation folder", visible=False, key="-presentation_folder_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-presentation_folder-")
    ],
    [
        Sg.Push(),
        Sg.Text("Name of folder holding preservation files", visible=False, key="-preservation1_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-preservation1-")
    ],
    [
        Sg.Push(),
        Sg.Text("Name of folder holding intermediary files", visible=False, key="-presentation2_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-presentation2-")
    ],
    [
        Sg.Push(),
        Sg.Text("Name of folder holding presentation files", visible=False, key="-presentation3_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-presentation3-")
    ],
    [
        Sg.HorizontalSeparator(),
    ],
    [
        Sg.Text("General variables", text_color="orchid1", font=("Calibri", "12", "underline"))
    ],
    [
        Sg.Push(),
        Sg.Text("Preservica Version:", key="-PreservicaVersion_TEXT-"),
        Sg.Input("", size=(50, 1), key="-PreservicaVersion-")
    ],
    [
        Sg.Push(),
        Sg.Text("UUID to upload to", visible=True, key="-UUID_Text-"),
        Sg.Input("", size=(50, 1), visible=True, key='-UUID-')
    ],
    [
        Sg.Push(),
        Sg.Text("Object type", visible=True, key="-TYPE_Text-"),
        Sg.Input("", size=(50, 1), visible=True, key="-TYPE-")
    ],
    [
        Sg.Push(),
        Sg.Text("Delay in seconds", visible=True, key="-DELAY_Text-"),
        Sg.Input("", size=(50, 1), visible=True, key="-DELAY-")
    ],
    [
        Sg.Push(),
        Sg.Text("When to start quiet time, leave blank if n/a", visible=True, key="-QUIET_Start_Text-"),
        Sg.Input("", size=(50, 1), visible=True, key="-QUIET_Start-")
    ],
    [
        Sg.Push(),
        Sg.Text("When to end quiet time, leave blank if N/A", visible=True, key="-QUIET_End_Text-"),
        Sg.Input("", size=(50, 1), visible=True, key="-QUIET_End-")
    ],
    [
        Sg.Push(),
        Sg.Text("Time to pause between uploads", visible=True, key="-INTERVAL_Text-"),
        Sg.Input("", size=(50, 1), visible=True, key="-INTERVAL-")
    ],
    [
      Sg.Checkbox("Implement Quiet time?", checkbox_color="dark green", key="-QuietTime-",
                  tooltip="uploads from crawlers will pause during specified quiet time")
    ],
    [
        Sg.Checkbox("Play sound when complete?", checkbox_color="dark green", key="-NOTIFICATION-",
                    tooltip="will play audio notification when full upload run is complete, for passive monitoring")
    ],
    [
        Sg.Push(),
        Sg.Text("wav file to play", visible=False, key="-SOUND_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-SOUND-"),
        Sg.FileBrowse(file_types=(("wav files only", "*.wav"),), visible=False, key="-SOUND_Browse-")
    ],
    [
        Sg.HorizontalSeparator(),
    ],
    [
        Sg.Text("Upload variables", text_color="orchid1", font=("Calibri", "12", "underline"))
    ],
    [
        Sg.Push(),
        Sg.Text("Username:", key="-USERNAME_TEXT-"),
        Sg.Input("", size=(50, 1), key="-USERNAME-")
    ],
    [
        Sg.Push(),
        Sg.Text("Password:", key="-PASSWORD_TEXT-"),
        Sg.Input("", size=(50, 1), password_char="#", key="-PASSWORD-")
    ],
    [
        Sg.Push(),
        Sg.Text("Domain Prefix:", key="-PREFIX_TEXT-"),
        Sg.Input("", size=(50, 1), key="-PREFIX-")
    ],
    [
        Sg.Push(),
        Sg.Text("Tenancy abbreviation:", key="-TENANCY_TEXT-"),
        Sg.Input("", size=(50, 1), key="-TENANCY-")
    ],
    [
        Sg.Text("Select execute to start processing")
    ],
    [
        Sg.Push(),
        Sg.Button("Execute", tooltip="This will start the program running."),
        Sg.Push()
    ],
    [
        Sg.Text("Select Close to close the window.")
    ],
    [Sg.Button("Close",
               tooltip="Close this window. Other processes you started must be finished before this button will "
                       "do anything.",
               bind_return_key=True)],
    [
        Sg.ProgressBar(1, orientation="h", size=(50, 20), bar_color="dark green", key="-Progress-", border_width=5,
                       relief="RELIEF_SUNKEN")
    ],
    [
        Sg.Text("", key="-STATUS-")
    ],
    [
        Sg.Multiline(default_text="Click execute to show progress\n------------------------------", size=(70, 5),
                     auto_refresh=True, reroute_stdout=False, key="-OUTPUT-", autoscroll=True, border_width=5),
    ],
    ''''''
]

window = Sg.Window(
    "Opex Compiler Graphical interface",
    layout,
    icon=my_icon,
    button_color="dark green",

)

event, values = window.read()
while True:
    event, values = window.read()
    use_config = values["-CONFIG-"]
    configfile = values['-CONFIGFILE-']
    notification = values['-NOTIFICATION-']
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
    if values['-NOTIFICATION-'] is True:
        window['-SOUND_Text-'].update(visible=True)
        window['-SOUND-'].update(visible=True)
        window['-SOUND_Browse-'].update(visible=True)
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
    object_type = values['-TYPE-']
    delay = values['-DELAY-']
    if values['-DELAY-'] != "":
        delay = int(delay)
    standardDir = values['-UUID-']
    quiet_time = values['-QuietTime-']
    if quiet_time is True:
        quiet_start = values['-QUIET_Start-']
        quiet_start = quiet_start.split(":")
        quiet_start = [int(quiet_start[0]), int(quiet_start[1]), int(quiet_start[2])]
        quiet_end = values['-QUIET_End-']
        quiet_end = quiet_end.split(":")
        quiet_end = [int(quiet_end[0]), int(quiet_end[1]), int(quiet_end[2])]
        interval = int(values['-INTERVAL-'])
    staging = values['-UploadStaging-']
    base_url = f"https://{prefix}.preservica.com/api/entity/structural-objects/"
    baseline_valuables = {'username': username,
                          'password': password,
                          'tenant': tenancy,
                          'prefix': prefix,
                          'asset_title': '',
                          'asset_tag': 'open',
                          'parent_uuid': standardDir,
                          'export_directory': staging,
                          'asset_description': '',
                          'ignore': ['.metadata', '.db'],
                          'special_format': object_type,
                          'quiet_time': False}
    secondaryDir = ""
    secondaryTitle = ""
    log = open("log_multipathAssets.txt", "a")
    helperFile = "helperFile.txt"
    counter1 = 0
    counter2 = 0
    setup = ""
    if event == "Generate":
        if not os.path.isfile("configfile.txt"):
            with open("configfile.txt", "w") as w:
                w.write(config_template)
            w.close()
            window['-OUTPUT-'].update("\nconfigfile.txt generated", append=True)
        else:
            window['-OUTPUT-'].update("\nconfigfile.txt already exists", append=True)
    if event == "Load":
        if use_config is True and configfile != "":
            config = configparser.ConfigParser()
            config.read(configfile)
            if opex_type == "3versions_crawler_tree":
                var = config.get('3_version_crawler_tree', 'root_folder')
                window['-ROOT-'].update(var)
                var = config.get('3_version_crawler_tree', 'preservation_folder')
                window['-preservation1-'].update(var)
                var = config.get('3_version_crawler_tree', 'intermediary_folder')
                window['-presentation2-'].update(var)
                var = config.get('3_version_crawler_tree', 'presentation_folder')
                window['-presentation3-'].update(var)
            if opex_type == "2versions_crawler":
                var = config.get('2_version_crawler', 'preservation_folder')
                window['-preservation_folder-'].update(var)
                var = config.get('2_version_crawler', 'presentation_folder')
                window['-presentation_folder-'].update(var)
            if opex_type == "3versions_crawler":
                var = config.get('3_version_crawler', 'preservation_folder')
                window['-preservation_folder-'].update(var)
                var = config.get('3_version_crawler', 'intermediary_folder')
                window['-intermediary_folder-'].update(var)
                var = config.get('3_version_crawler', 'presentation_folder')
                window['-presentation_folder-'].update(var)
            var = config.get('general', 'preservica_version')
            window['-PreservicaVersion-'].update(var)
            var = config.get('general', 'standard_directory_uuid')
            window['-UUID-'].update(var)
            var = config.get('general', 'object_type')
            window['-TYPE-'].update(var)
            var = config.get('general', 'delay')
            window['-DELAY-'].update(var)
            var = config.get('general', 'quiet_start')
            window['-QUIET_Start-'].update(var)
            var = config.get('general', 'quiet_end')
            window['-QUIET_End-'].update(var)
            var = config.get('general', 'interval')
            window['-INTERVAL-'].update(var)
            var = config.get('general', 'export_location')
            window['-UploadStaging-'].update(var)
            var = config.get('general','sound')
            window['-SOUND-'].update(var)
            print("config file loaded")
            window['-OUTPUT-'].update("\nConfiguration loaded", append=True)
    if event == "Execute":
        if opex_type == "2versions_crawler":
            window['-OUTPUT-'].update("\nprocessing a 2 version opex directory", append=True)
            dirpath2 = values['-preservation_folder-']
            dirpath1 = values['-presentation_folder-']
            dirLength = len(dirpath1) + 1
            window['-OUTPUT-'].update("\nBuilding information for progress bar", append=True)
            for dirpath, dirnames, filenames in os.walk(dirpath1):
                for filename in filenames:
                    if filename.endswith(".pdf"):
                        counter2 += 1
            for dirpath, dirnames, filenames in os.walk(dirpath1):
                for filename in filenames:
                    valuables = baseline_valuables
                    valuables['quiet_time'] = quiet_time
                    if not filename.endswith(".metadata"):
                        if dirpath != setup:
                            if quiet_time is True:
                                valuables['quiet_start'] = quiet_start
                                valuables['quiet_end'] = quiet_end
                                valuables['interval'] = interval
                            setup = dirpath
                            valuables['asset_title'] = dirpath.split("/")[-1]
                            print(valuables['asset_title'])
                            valuables['asset_description'] = valuables['asset_title']
                            fileLength = len(filename)
                            filename = os.path.join(dirpath, filename)
                            metadata_file = os.path.join(dirpath, valuables['asset_title'] + ".metadata")
                            if os.path.isfile(metadata_file):
                                valuables['metadata_file'] = metadata_file
                            # musical chairs with directory paths so we don't mess up the original variable values
                            dirpath3 = dirpath
                            dirpath5 = dirpath.replace(dirpath1, dirpath2)
                            dirpath4 = dirpath1 + "/" + valuables['asset_title']
                            math = len(valuables['asset_title']) + 1
                            valuables['access_directory'] = dirpath3
                            valuables['preservation_directory'] = dirpath5
                            if dirpath4 != dirpath3:
                                print("not a root asset, sending to subfolder")
                                dirTitle = dirpath3.split("/")[-2]
                                print("directory title:", dirTitle)
                                if dirTitle == secondaryTitle:
                                    valuables['parent_uuid'] = secondaryDir
                                    opexCreator.opexCreator.multi_upload_withXIP(valuables)
                                if dirTitle != secondaryTitle:
                                    print("directory doesn't exist yet, creating it")
                                    headers = login(url, payload)
                                    data = f'<StructuralObject xmlns="http://preservica.com/XIP/v{version}"><Title>' + \
                                           dirTitle + '</Title><Description>' + dirTitle + \
                                           '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir + \
                                           '</Parent></StructuralObject>'
                                    response = requests.post(base_url, headers=headers, data=data)
                                    status = response.status_code
                                    print(status)
                                    with open(helperFile, 'wb') as fd:
                                        for chunk in response.iter_content(chunk_size=128):
                                            fd.write(chunk)
                                    fd.close()
                                    dom = ET.parse(helperFile)
                                    purl = dom.find(".//xip:Ref", namespaces=namespaces).text
                                    secondaryDir = purl
                                    valuables['parent_uuid'] = purl
                                    posty = dom.find(".//EntityResponse:Self", namespaces=namespaces).text
                                    posty = posty + "/metadata"
                                    dirMD = dirpath[:-math] + "/" + dirTitle + ".metadata"
                                    if os.path.isfile(dirMD):
                                        response = requests.post(posty, headers=headers, data=open(dirMD, 'rb'))
                                        print("adding metadata to the directory")
                                    else:
                                        print("no metadata file for the directory")
                                    secondaryTitle = dirTitle
                                    opexCreator.opexCreator.multi_upload_withXIP(valuables)
                            else:
                                opexCreator.opexCreator.multi_upload_withXIP(valuables)
                            counter1 += 1
                            print(counter1, "units uploaded thus far")
                            window['-OUTPUT-'].update(f"\n{counter1} of {counter2} uploaded thus far", append=True)
                            window['-Progress-'].update_bar(counter1, counter2)
                            if delay > 0:
                                opexCreator.opexCreator.countdown(delay)
                            log.write(valuables['asset_title'] + " upload complete" + "\n")
                        else:
                            continue
            if os.path.isfile("./transfer_agent_list.txt"):
                try:
                    os.remove("./transfer_agent_list.txt")
                except:
                    print("unable to remove ./transfer_agent_list.txt, please delete manually")
            log.close()
            print("all done")
            print(counter1, "successes")
        if opex_type == "3versions_crawler":
            window['-OUTPUT-'].update("\nprocessing a 3 version opex directory setup", append=True)
            dirpath2 = values['-preservation_folder-']
            dirpath1 = values['-presentation_folder-']
            dirpathA = values['-intermediary_folder-']
            dirLength = len(dirpath1) + 1
            for dirpath, dirnames, filenames in os.walk(dirpath1):
                for filename in filenames:
                    valuables = baseline_valuables
                    valuables['quiet_time'] = quiet_time
                    if not filename.endswith(".metadata"):
                        if dirpath != setup:
                            if quiet_time is True:
                                if use_config is True and configfile != "":
                                    # reload configfile on iteration so can change stuff on the fly
                                    config.read(configfile)
                                    quiet_start = config.get('general', 'quiet_start')
                                    quiet_start = quiet_start.split(":")
                                    quiet_start = [int(quiet_start[0]), int(quiet_start[1]), int(quiet_start[2])]
                                    quiet_end = config.get('general', 'quiet_end')
                                    quiet_end = quiet_end.split(":")
                                    quiet_end = [int(quiet_end[0]), int(quiet_end[1]), int(quiet_end[2])]
                                    interval = config.get('general', 'interval')
                                    valuables['quiet_start'] = quiet_start
                                    valuables['quiet_end'] = quiet_end
                                    valuables['interval'] = interval
                                valuables['quiet_start'] = quiet_start
                                valuables['quiet_end'] = quiet_end
                                valuables['interval'] = interval
                            setup = dirpath
                            valuables['asset_title'] = dirpath.split("/")[-1]
                            print(valuables['asset_title'])
                            valuables['asset_description'] = valuables['asset_title']
                            fileLength = len(filename)
                            filename = os.path.join(dirpath, filename)
                            metadata_file = os.path.join(dirpath, valuables['asset_title'] + ".metadata")
                            if os.path.isfile(metadata_file):
                                valuables['metadata_file'] = metadata_file
                            # musical chairs with directory paths so we don't mess up the original variable values
                            dirpath3 = dirpath
                            dirpath5 = dirpath.replace(dirpath1, dirpath2)
                            dirpathB = dirpath.replace(dirpath1, dirpathA)
                            dirpath4 = dirpath1 + "/" + valuables['asset_title']
                            math = len(valuables['asset_title']) + 1
                            valuables['access2_directory'] = dirpath3
                            valuables['access1_directory'] = dirpathB
                            valuables['preservation_directory'] = dirpath5
                            if dirpath4 != dirpath3:
                                print("not a root asset, sending to subfolder")
                                dirTitle = dirpath3.split("/")[-2]
                                print("directory title:", dirTitle)
                                if dirTitle == secondaryTitle:
                                    valuables['parent_uuid'] = secondaryDir
                                    opexCreator_3versions.multi_upload_withXIP(valuables)
                                if dirTitle != secondaryTitle:
                                    print("directory doesn't exist yet, creating it")
                                    headers = login(url, payload)
                                    data = f'<StructuralObject xmlns="http://preservica.com/XIP/v{version}"><Title>' \
                                           + dirTitle + '</Title><Description>' + dirTitle + \
                                           '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir + \
                                           '</Parent></StructuralObject>'
                                    response = requests.post(base_url, headers=headers, data=data)
                                    status = response.status_code
                                    print(status)
                                    with open(helperFile, 'wb') as fd:
                                        for chunk in response.iter_content(chunk_size=128):
                                            fd.write(chunk)
                                    fd.close()
                                    dom = ET.parse(helperFile)
                                    purl = dom.find(".//xip:Ref", namespaces=namespaces).text
                                    secondaryDir = purl
                                    valuables['parent_uuid'] = purl
                                    posty = dom.find(".//EntityResponse:Self", namespaces=namespaces).text
                                    posty = posty + "/metadata"
                                    dirMD = dirpath[:-math] + "/" + dirTitle + ".metadata"
                                    if os.path.isfile(dirMD):
                                        response = requests.post(posty, headers=headers, data=open(dirMD, 'rb'))
                                        print("adding metadata to the directory")
                                    else:
                                        print("no metadata file for the directory")
                                    secondaryTitle = dirTitle
                                    opexCreator_3versions.multi_upload_withXIP(valuables)
                            else:
                                opexCreator_3versions.multi_upload_withXIP(valuables)
                            counter1 += 1
                            log.write(valuables['asset_title'] + " upload complete" + "\n")
                        else:
                            continue
            if os.path.isfile("./transfer_agent_list.txt"):
                try:
                    os.remove("./transfer_agent_list.txt")
                except:
                    print("unable to remove ./transfer_agent_list.txt, please delete manually")
            log.close()
            print("all done")
            print(counter1, "successes")
        if opex_type == "3versions_crawler_tree":
            window['-OUTPUT-'].update("\nprocessing a 3 version opex directory in a tree configuration", append=True)
            rooty = values['-ROOT-']
            dirpath2 = values['-preservation1-']
            dirpath1 = values['-presentation3-']
            dirpathA = values['-presentation2-']
            dirLength = len(dirpath1) + 1
            window['-OUTPUT-'].update("\nBuilding information for progress bar", append=True)
            for dirpath, dirnames, filenames in os.walk(rooty):
                for filename in filenames:
                    if filename.endswith(".pdf"):
                        counter2 += 1
            window['-OUTPUT-'].update("\nProgress information compiled, starting", append=True)
            for dirpath, dirnames, filenames in os.walk(rooty):
                for filename in filenames:
                    valuables = baseline_valuables
                    valuables['quiet_time'] = quiet_time
                    if dirpath1 in str(dirpath):
                        if not filename.endswith(".metadata"):
                            if dirpath != setup:
                                if quiet_time is True:
                                    if use_config is True and configfile != "":
                                        # reload configfile on iteration so can change stuff on the fly
                                        config.read(configfile)
                                        quiet_start = config.get('general', 'quiet_start')
                                        quiet_start = quiet_start.split(":")
                                        quiet_start = [int(quiet_start[0]), int(quiet_start[1]), int(quiet_start[2])]
                                        quiet_end = config.get('general', 'quiet_end')
                                        quiet_end = quiet_end.split(":")
                                        quiet_end = [int(quiet_end[0]), int(quiet_end[1]), int(quiet_end[2])]
                                        interval = config.get('general', 'interval')
                                        valuables['quiet_start'] = quiet_start
                                        valuables['quiet_end'] = quiet_end
                                        valuables['interval'] = interval
                                    valuables['quiet_start'] = quiet_start
                                    valuables['quiet_end'] = quiet_end
                                    valuables['interval'] = interval
                                setup = dirpath
                                valuables['asset_title'] = dirpath.split("/")[-2]
                                print(valuables['asset_title'])
                                valuables['asset_description'] = valuables['asset_title']
                                fileLength = len(filename)
                                filename = os.path.join(dirpath, filename)
                                metadata_file = os.path.join(dirpath, valuables['asset_title'] + ".metadata")
                                metadata_file2 = metadata_file.replace(dirpath1, dirpath2)
                                metadata_file3 = metadata_file.replace(dirpath1, dirpathA)
                                if os.path.isfile(metadata_file):
                                    valuables['metadata_file'] = metadata_file
                                elif os.path.isfile(metadata_file2):
                                    valuables['metadata_file'] = metadata_file2
                                elif os.path.isfile(metadata_file3):
                                    valuables['metadata_file'] = metadata_file3
                                # musical chairs with directory paths so we don't mess up the original variable values
                                dirpath3 = dirpath
                                dirpath5 = dirpath.replace(dirpath1, dirpath2)
                                dirpathB = dirpath.replace(dirpath1, dirpathA)
                                dirpath4 = valuables['asset_title'] + "/" + dirpath1
                                math = len(valuables['asset_title']) + 1
                                valuables['access2_directory'] = dirpath3
                                valuables['access1_directory'] = dirpathB
                                valuables['preservation_directory'] = dirpath5
                                if dirpath4 != dirpath3:
                                    print("not a root asset, sending to subfolder")
                                    dirTitle = dirpath3.split("/")[-3]
                                    print("directory title:", dirTitle)
                                    if dirTitle == secondaryTitle:
                                        valuables['parent_uuid'] = secondaryDir
                                        opexCreator_3versions.multi_upload_withXIP(valuables)
                                    if dirTitle != secondaryTitle:
                                        print("directory doesn't exist yet, creating it")
                                        headers = login(url, payload)
                                        data = f'<StructuralObject xmlns="http://preservica.com/XIP/v{version}' \
                                               f'"><Title>' + dirTitle + '</Title><Description>' + dirTitle + \
                                               '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir \
                                               + '</Parent></StructuralObject>'
                                        response = requests.post(base_url, headers=headers, data=data)
                                        status = response.status_code
                                        print(status)
                                        with open(helperFile, 'wb') as fd:
                                            for chunk in response.iter_content(chunk_size=128):
                                                fd.write(chunk)
                                        fd.close()
                                        dom = ET.parse(helperFile)
                                        purl = dom.find(".//xip:Ref", namespaces=namespaces).text
                                        secondaryDir = purl
                                        valuables['parent_uuid'] = purl
                                        posty = dom.find(".//EntityResponse:Self", namespaces=namespaces).text
                                        posty = posty + "/metadata"
                                        dirMD = dirpath[:-math] + "/" + dirTitle + ".metadata"
                                        if os.path.isfile(dirMD):
                                            response = requests.post(posty, headers=headers, data=open(dirMD, 'rb'))
                                            print("adding metadata to the directory")
                                        else:
                                            print("no metadata file for the directory")
                                        secondaryTitle = dirTitle
                                        window['-OUTPUT-'].update(
                                            f"{opexCreator_3versions.multi_upload_withXIP(valuables)}\n", append=True)
                                else:
                                    window['-OUTPUT-'].update(
                                        f"{opexCreator_3versions.multi_upload_withXIP(valuables)}\n", append=True)
                                counter1 += 1
                                print(counter1, "units uploaded thus far")
                                window['-OUTPUT-'].update(f"\n{counter1} of {counter2} uploaded thus far", append=True)
                                window['-Progress-'].update_bar(counter1, counter2)
                                if delay > 0:
                                    if use_config is True:
                                        config.read(configfile)
                                        delay = int(config.get('general', 'delay'))
                                    opexCreator.opexCreator.countdown(delay)
                                log.write(valuables['asset_title'] + " upload complete" + "\n")
                            else:
                                continue
            if os.path.isfile("./transfer_agent_list.txt"):
                try:
                    os.remove("./transfer_agent_list.txt")
                except:
                    print("unable to remove ./transfer_agent_list.txt, please delete manually")
            log.close()
            print("all done")
            print(counter1, "successes")
            window['-OUTPUT-'].update("\nAll Done, okay to close the tool", append=True)
        if notification is True:
            finished(values['-SOUND-'])
    if event == "Close" or event == Sg.WIN_CLOSED:
        break
window.close()
