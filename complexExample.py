import os
import lxml.etree as ET
import requests
import getpass
import opexCreator

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

print("warning: the directory structure of the preservation and access files must match exactly once you pass the root level")
#inputs
dirpath1 = input("root filepath to access files: ")
dirpath2 = input("root filepath to preservation files: ")
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
             'access_directory': dirpath1,
             'preservation_directory': dirpath2,
             'asset_title': '',
             'asset_tag': 'open',
             'parent_uuid': standardDir,
             'export_directory': './test',
             'asset_description': '',
             'ignore': [".metadata", ".db"],
             'special_format': object_type}
#start
setup = ""
for dirpath, dirnames, filenames in os.walk(dirpath1):
    for filename in filenames:
        valuables = baseline_valuables
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
                        opexCreator.multi_upload_withXIP(valuables)
                else:
                    opexCreator.multi_upload_withXIP(valuables)
                counter1 += 1
                log.write(valuables['asset_title'] + " upload complete" + "\n")
            else:
                continue
log.close()
print("all done")
print(counter1, "successes")