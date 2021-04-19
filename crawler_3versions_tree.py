import os
import lxml.etree as ET
import requests
import getpass
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

# namespaces to parse xml
namespaces = {'xip': 'http://preservica.com/XIP/v6.2',
              'EntityResponse': 'http://preservica.com/EntityAPI/v6.2',
              'ChildrenResponse': 'http://preservica.com/EntityAPI/v6.2',
              'MetadataResponse': 'http://preservica.com/EntityAPI/v6.2',
              'dcterms': 'http://dublincore.org/documents/dcmi-terms',
              'tslac': 'https://www.tsl.texas.gov/'}

print("warning: this crawler is meant to take care of 3 version assets where the versions are children of the parent asset folder, like so:")
print("asset name: myDocument")
print("main presentation: myDocument/presentation2/myDocument.pdf")
print("intermediary presentation: myDocument/presentation1/myDocument1.jpg myDocument2.jpg, etc.")
print("preservation master: myDocument/preservation1/myDocument1.tif myDocument2.tif, etc.")
#inputs
rooty = input("root filepath to crawl: ")
dirpath1 = input("subfolder for primary access files: ")
dirpath2 = input("subfolder for preservation files: ")
dirpathA = input("subfolder for secondary access files: ")
standardDir = input("baseline UUID to put the files: ")
suffixCount = int(input("Number of characters for subfiles: "))
object_type = input("type of thing, choose between 'film' and 'multi-page document': ")
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
             'tenent': tenancy,
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
             'special_format': object_type}
#start
setup = ""
for dirpath, dirnames, filenames in os.walk(rooty):
    for filename in filenames:
        valuables = baseline_valuables
        print(dirpath)
        if dirpath1 in str(dirpath):
            if not filename.endswith((".metadata")):
                if dirpath != setup:
                    setup = dirpath
                    valuables['asset_title'] = dirpath.split("/")[-2]
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
                            data = '<StructuralObject xmlns="http://preservica.com/XIP/v6.2"><Title>' + dirTitle + '</Title><Description>' + dirTitle + '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir + '</Parent></StructuralObject>'
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
log.close()
print("all done")
print(counter1, "successes")