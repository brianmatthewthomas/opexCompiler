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
        sg.Radio("3-version crawler tree","radio1", default=False,key="-TYPE_3v-tree-"),
        sg.Button("Push to Update")
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
    object_type = values['-TYPE-']
    delay = values['-DELAY-']
    if values['-DELAY-'] != "":
        delay = int(delay)
    standardDir = values['-UUID-']
    quiet_time = values['-QuietTime-']
    if quiet_time is True:
        quiet_start = values['-QUIET_Start-']
        quiet_start = quiet_start.split(":")
        quiet_start = [int(quiet_start[0]),int(quiet_start[1]),int(quiet_start[2])]
        quiet_end = values['-QUIET_End-']
        quiet_end = quiet_end.split(":")
        quiet_end = [int(quiet_end[0]),int(quiet_end[1]),int(quiet_end[2])]
        interval = int(values['-INTERVAL-'])
    staging = values['-UploadStaging-']
    base_url = f"https://{prefix}.preservica.com/api/entity/structural-objects/"
    baseline_valuables = {'username':username,
                          'password':password,
                          'tenent':tenancy,
                          'prefix':prefix,
                          'asset_title':'',
                          'asset_tag':'open',
                          'parent_uuid':standardDir,
                          'export_directory':staging,
                          'asset_description':'',
                          'ignore':['.metadata','.db'],
                          'special_format':object_type,
                          'quiet_time':False}
    secondaryDir = ""
    secondaryTitle = ""
    log = open("log_multipathAssets.txt","a")
    helperFile = "helperFile.txt"
    counter1 = 0
    counter2 = 0
    setup = ""
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
            var = config.get('general','export_location')
            window['-UploadStaging-'].update(var)
            print("config file loaded")
            window['-OUTPUT-'].update("\nConfiguration loaded", append=True)
    if event == "Execute":
        if opex_type == "2versions_crawler":
            window['-OUTPUT-'].update("\nprocessing a 2 version opex directory", append=True)
            dirpath1 = values['-preservation_folder-']
            dirpath2 = values['-presentation_folder-']
            dirLength = len(dirpath1) + 1
            for dirpath, dirnames, filenames in os.walk(dirpath1):
                for filename in filenames:
                    valuables = baseline_valuables
                    valuables['quiet_time'] = quiet_time
                    if not filename.endswith((".metadata")):
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
                                print("drectory title:", dirTitle)
                                if dirTitle == secondaryTitle:
                                    valuables['parent_uuid'] = secondaryDir
                                    opexCreator.multi_upload_withXIP(valuables)
                                if dirTitle != secondaryTitle:
                                    print("directory doesn't exist yet, creating it")
                                    headers = login(url, payload)
                                    data = f'<StructuralObject xmlns="http://preservica.com/XIP/v{version}"><Title>' + dirTitle + '</Title><Description>' + dirTitle + '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir + '</Parent></StructuralObject>'
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
                                    opexCreator.multi_upload_withXIP(valuables)
                            else:
                                opexCreator.multi_upload_withXIP(valuables)
                            counter1 += 1
                            print(counter1,"units uploaded thus far")
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
            dirpath1 = values['-preservation_folder-']
            dirpath2 = values['-presentation_folder-']
            dirpathA = values['-intermediary_folder-']
            dirLength = len(dirpath1) + 1
            for dirpath, dirnames, filenames in os.walk(dirpath1):
                for filename in filenames:
                    valuables = baseline_valuables
                    valuables['quiet_time'] = quiet_time
                    if not filename.endswith((".metadata")):
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
                            dirpathB = dirpath.replace(dirpath1, dirpathA)
                            dirpath4 = dirpath1 + "/" + valuables['asset_title']
                            math = len(valuables['asset_title']) + 1
                            valuables['access2_directory'] = dirpath3
                            valuables['access1_directory'] = dirpathB
                            valuables['preservation_directory'] = dirpath5
                            if dirpath4 != dirpath3:
                                print("not a root asset, sending to subfolder")
                                dirTitle = dirpath3.split("/")[-2]
                                print("drectory title:", dirTitle)
                                if dirTitle == secondaryTitle:
                                    valuables['parent_uuid'] = secondaryDir
                                    opexCreator_3versions.multi_upload_withXIP(valuables)
                                if dirTitle != secondaryTitle:
                                    print("directory doesn't exist yet, creating it")
                                    headers = login(url, payload)
                                    data = f'<StructuralObject xmlns="http://preservica.com/XIP/v{version}"><Title>' + dirTitle + '</Title><Description>' + dirTitle + '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir + '</Parent></StructuralObject>'
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
            for dirpath, dirnames, filenames in os.walk(rooty):
                for filename in filenames:
                    if filename.endswith(".pdf"):
                        counter2 += 1
            for dirpath, dirnames, filenames in os.walk(rooty):
                for filename in filenames:
                    valuables = baseline_valuables
                    valuables['quiet_time'] = quiet_time
                    if dirpath1 in str(dirpath):
                        if not filename.endswith((".metadata")):
                            if dirpath != setup:
                                if quiet_time is True:
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
                                    print("drectory title:", dirTitle)
                                    if dirTitle == secondaryTitle:
                                        valuables['parent_uuid'] = secondaryDir
                                        opexCreator_3versions.multi_upload_withXIP(valuables)
                                    if dirTitle != secondaryTitle:
                                        print("directory doesn't exist yet, creating it")
                                        headers = login(url, payload)
                                        data = f'<StructuralObject xmlns="http://preservica.com/XIP/v{version}"><Title>' + dirTitle + '</Title><Description>' + dirTitle + '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir + '</Parent></StructuralObject>'
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
            window['-OUTPUT-'].update("\nAll Done, okay to close the tool",append=True)
    if event == "Close" or event == sg.WIN_CLOSED:
        break
window.close()
