import os
import lxml.etree as ET
import requests
import getpass
import configparser
from opexCreator import opexCreator_3versions

def login(url, payload):
    auth = requests.post(url, data=payload).json()
    sessionToken = auth['token']
    headers = {'Preservica-Access-Token': sessionToken}
    headers['Content-Type'] = 'application/xml'
    headers['Accept-Charset'] = 'UTF-8'
    return headers

username = input("Enter your username: ")
password = getpass.getpass("Enter password: ")
tenancy = input("Enter your tenancy name: ")
prefix = input("Server prefix: ")
payload = {'username': username, 'password': password, 'tenant': tenancy}
url = f"https://{prefix}.preservica.com/api/accesstoken/login"
print("testing login...")
headers = login(url, payload)
print(headers)
version = input("preservica version in play?: ")

# namespaces to parse xml
namespaces = {'xip': f'http://preservica.com/XIP/v{version}',
              'EntityResponse': f'http://preservica.com/EntityAPI/v{version}',
              'ChildrenResponse': f'http://preservica.com/EntityAPI/v{version}',
              'MetadataResponse': f'http://preservica.com/EntityAPI/v{version}',
              'dcterms': 'http://dublincore.org/documents/dcmi-terms',
              'tslac': 'https://www.tsl.texas.gov/'}

print("warning: the directory structure of the preservation and access files must match exactly once you pass the root level")
#inputs
quiet_time = input("implement quiet time? use yes/no: ")
if quiet_time == "no":
    quiet_time = ""
quiet_time = bool(quiet_time)
configuration = input("use config file? yes/no: ")
if configuration == "yes":
    config = configparser.ConfigParser()
    configfile = input("name of config file using relative filepath: ")
    config.read(configfile)
    dirpath1 = config.get('3_version_crawler','presentation_folder')
    dirpath2 = config.get('3_version_crawler','preservation_folder')
    dirpathA = config.get('3_version_crawler','intermediary_folder')
    standardDir = config.get('general','standard_directory_uuid')
    suffixCount = int(config.get('general','suffix_count'))
    object_type = config.get('general','object_type')
    delay = int(config.get('general','delay'))
    if quiet_time is True:
        quiet_start = config.get('general','quiet_start')
        quiet_start = quiet_start.split(":")
        quiet_start = [int(quiet_start[0]),int(quiet_start[1]),int(quiet_start[2])]
        quiet_end = config.get('general','quiet_end')
        quiet_end = quiet_end.split(":")
        quiet_end = [int(quiet_end[0]),int(quiet_end[1]),int(quiet_end[2])]
        interval = int(config.get('general','interval'))
if configuration == "no":
    dirpath1 = input("root filepath to access files: ")
    dirpath2 = input("root filepath to preservation files: ")
    dirpathA = input("root filepath to secondary NOT rendered access files: ")
    standardDir = input("baseline UUID to put the files: ")
    suffixCount = int(input("Number of characters for subfiles: "))
    object_type = input("type of thing, choose between 'film' and 'multi-page document': ")
    delay = input("delay between uploads in number of seconds: ")
    while isinstance(delay, int) is False:
        try:
            delay = int(delay)
        except:
            print("the delay must be an integer, try again. if no delay input zero")
            delay = input("delay between uploads in number of seconds: ")
    if quiet_time is True:
        quiet_start = input("input quiet time start as hh:mm:ss:")
        quiet_start = quiet_start.split(":")
        quiet_start = [int(quiet_start[0]),int(quiet_start[1]),int(quiet_start[2])]
        quiet_end = input("input quiet time end as hh:mm:ss: ")
        quiet_end = quiet_end.split(":")
        quiet_end = [int(quiet_end[0]),int(quiet_end[1]),int(quiet_end[2])]
        interval = int(input("time in seconds between checking if sleep timer condition has been met: "))
# computer section
base_url = f"https://{prefix}.preservica.com/api/entity/structural-objects/"
dirLength = len(dirpath1) + 1
secondaryDir = ""
secondaryTitle = ""
log = open("log_multipathAssets.txt", "a")
helperFile = "helperFile.txt"
counter1 = 0
counter2 = 0
baseline_valuables = {'username': username,
             'password': password,
             'tenant': tenancy,
             'prefix': prefix,
             'access1_directory': dirpathA,
             'access2_directory': dirpath1,
             'preservation_directory': dirpath2,
             'asset_title': '',
             'asset_tag': 'open',
             'parent_uuid': standardDir,
             'export_directory': './export',
             'asset_description': '',
             'ignore': [".metadata", ".db"],
             'special_format': object_type,
                      'quiet_time': quiet_time}
#start
setup = ""
for dirpath, dirnames, filenames in os.walk(dirpath1):
    for filename in filenames:
        valuables = baseline_valuables
        valuables['quiet_time'] = quiet_time
        if not filename.endswith((".metadata")):
            if dirpath != setup:
                if quiet_time is True:
                    if configuration == "yes":
                        config.read(configfile)
                        quiet_start = config.get('general','quiet_start')
                        quiet_start = quiet_start.split(":")
                        valuables['quiet_start'] = [int(quiet_start[0]),int(quiet_start[1]),int(quiet_start[2])]
                        quiet_end = config.get('general','quiet_end')
                        quiet_end = quiet_end.split(":")
                        valuables['quiet_end'] = [int(quiet_end[0]),int(quiet_end[1]),int(quiet_end[2])]
                        valuables['interval'] = int(config.get('general','interval'))
                    else:
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
                dirpathB = dirpath.replace(dirpath1,dirpathA)
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