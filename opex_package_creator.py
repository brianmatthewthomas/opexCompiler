import configparser
import os
import hashlib
import shutil
import sys
import uuid
import errno

import PySimpleGUI as Sg
import lxml.etree as ET
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

def progressCounty(directory):
    counter = 0
    window['-OUTPUT-'].update(f"\nGathering progress bar information", append=True)
    exclusions = ['metadata', 'db']
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filename_end = filename.split(".")[-1]
            if filename_end not in exclusions:
                counter += 1
    return counter

def cleanup(directory):
    for x, y, z in os.walk(directory):
        for a in z:
            try:
                a = os.path.join(x, a)
                window['-OUTPUT-'].update(f"\nattempting to remove {a}", append=True)
                os.remove(a)
            except Exception as error:
                window['-OUTPUT-'].update(f"\nException deleting {a}: {error}", append=True)
def create_directory(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

def create_sha256(filename):
    sha256 = hashlib.sha256()
    blocksize = 65536
    with open(filename, 'rb') as f:
        buffer = f.read(blocksize)
        while len(buffer) > 0:
            sha256.update(buffer)
            buffer = f.read(blocksize)
    fixity = sha256.hexdigest()
    return fixity

def film_check(my_target_dir, filename):
    if filename.split(".")[-1] == "srt" and filename.split(".")[-2] == "en":
        filename2 = f"{my_target_dir}/English/{filename}"
    elif filename.split(".")[-1] == "srt" and filename.split(".")[-2] == "es":
        filename2 = f"{my_target_dir}/Spanish/{filename}"
    elif filename.split(".")[-1] == "srt" and filename.split(".")[-2] == "jp":
        filename2 = f"{my_target_dir}/Japanese/{filename}"
    elif filename.split(".")[-1] == "srt":
        filename2 = f"{my_target_dir}/English/{filename}"
    elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
        filename2 = f"{my_target_dir}/English/{filename}"
    elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
        filename2 = f"{my_target_dir}/Spanish/{filename}"
    elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "jp":
        filename2 = f"{my_target_dir}/Japanese/{filename}"
    elif filename.endswith(tuple(['mp4', 'm4v', 'mov'])):
        filename2 = f"{my_target_dir}/Movie/{filename}"
    else:
        filename2 = f"{my_target_dir}/{filename.split('.')[0]}/{filename}"
    return filename2

def make_opex(valuables, filename2):
    opex = Element('opex:OPEXMetadata', {'xmlns:opex': 'http://www.openpreservationexchange.org/opex/v1.1'})
    opex_transfer = SubElement(opex, 'opex:Transfer')
    #opex_source = SubElement(opex_transfer, "opex:SourceID")
    #opex_source.text = valuables['asset_id']
    opex_fixities = SubElement(opex_transfer, "opex:Fixities")
    opex_sha256 = create_sha256(filename2)
    opex_fixity = SubElement(opex_fixities, 'opex:Fixity')
    opex_fixity.attrib = {'type': 'SHA-256', 'value': opex_sha256}
    opex_properties = SubElement(opex, 'opex:Properties')
    opex_title = SubElement(opex_properties, "opex:Title")
    opex_title.text = valuables['asset_title']
    opex_description = SubElement(opex_properties, 'opex:Description')
    opex_description.text = valuables['asset_description']
    opex_security = SubElement(opex_properties, 'opex:SecurityDescriptor')
    opex_security.text = valuables['asset_tag']
    if "metadata_file" in valuables.keys():
        if valuables['metadata_file'] != "":
            opex_metadata = SubElement(opex, 'opex:DescriptiveMetadata')
            opex_metadata.text = "This is where the metadata goes"
    export_file = f"{filename2}.opex"
    try:
        with open(export_file, "w", encoding='utf-8') as w:
            w.write(prettify(opex))
        w.close()
    except:
        try:
            with open(export_file, 'wb') as w:
                w.write(ElementTree.tostring(opex, encoding='utf-8', method='xml'))
            w.close()
        except:
            raise
    if 'metadata_file' in valuables.keys():
        if valuables['metadata_file'] != "":
            with open(valuables['metadata_file'], "r", encoding='utf-8') as r:
                filedata = r.read()
                filedata = filedata.replace('<?xml version="1.0" ?>', '')
                filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '')
                with open(export_file, "r", encoding='utf-8') as r:
                    fileinfo = r.read()
                    fileinfo = fileinfo.replace("This is where the metadata goes", filedata)
                    with open(export_file, "w", encoding='utf-8') as w:
                        w.write(fileinfo)
                    w.close()
    window['-OUTPUT-'].update(f"\nopex file for {filename2.split('/')[-1]} generated", append=True)

def make_folder_opex(source_dir, export_dir, package_UUID, metadata):
    for dirpath, dirnames, filenames in os.walk(f"{export_dir}/{package_UUID}"):
        target_metadata = dirpath.replace(f"{export_dir}/{package_UUID}", source_dir)
        target_metadata = target_metadata.replace(f"{source_dir.split('/')[-1]}\\{source_dir.split('/')[-1]}", source_dir.split('/')[-1])
        target2 = target_metadata.split("/")[-1].split("\\")[-1]
        target_metadata2 = f"{target_metadata}/{target2}.metadata"
        target_metadata = f"{target_metadata}.metadata"
        metadata = metadata
        if os.path.isfile(target_metadata):
            metadata = target_metadata
        if os.path.isfile(target_metadata2):
            metadata = target_metadata2
        opex = Element('opex:OPEXMetadata', {'xmlns:opex': 'http://www.openpreservationexchange.org/opex/v1.1'})
        opex_transfer = SubElement(opex, 'opex:Transfer')
        #opex_source = SubElement(opex_transfer, "opex:SourceID")
        #opex_source.text = dirpath.split("/")[-1]
        opex_manifest = SubElement(opex_transfer, "opex:Manifest")
        files = [q for q in os.listdir(dirpath) if os.path.isfile(f"{dirpath}/{q}")]
        window['-OUTPUT-'].update(f"\nlist of files in {dirpath}: {files}", append=True)
        files.sort()
        if files != []:
            opex_files = SubElement(opex_manifest, 'opex:Files')
            for x in files:
                opex_file = SubElement(opex_files, "opex:File")
                opex_file.text = x
                if x.endswith(".opex"):
                    opex_file.attrib = {'type': "metadata"}
                else:
                    opex_file.attrib = {'type': 'content'}
        directories = [q for q in os.listdir(dirpath) if os.path.isdir(f"{dirpath}/{q}")]
        window['-OUTPUT-'].update(f"\nlist of directories in {dirpath}: {directories}", append=True)
        directories.sort()
        if directories != []:
            opex_directories = SubElement(opex_manifest, 'opex:Folders')
            for x in directories:
                opex_directory = SubElement(opex_directories, "opex:Folder")
                opex_directory.text = x
        opex_properties = SubElement(opex, 'opex:Properties')
        opex_title = SubElement(opex_properties, "opex:Title")
        opex_title.text = dirpath.split("/")[-1].split("\\")[-1]
        opex_description = SubElement(opex_properties, 'opex:Description')
        opex_description.text = dirpath.split("/")[-1].split("\\")[-1]
        opex_security = SubElement(opex_properties, 'opex:SecurityDescriptor')
        opex_security.text = "open"
        if metadata != "":
            opex_metadata = SubElement(opex, "opex:DescriptiveMetadata")
            opex_metadata.text = "This is where the metadata goes"
        new_dirpath = dirpath.replace('\\', '/')
        export_file = f"{dirpath}/{new_dirpath.split('/')[-1]}.opex"
        with open(export_file, "w", encoding='utf-8') as w:
            w.write(prettify(opex))
        w.close()
        if metadata != "":
            with open(metadata, "r") as r:
                filedata = r.read()
                filedata = filedata.replace('<?xml version="1.0" ?>', '')
                filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '')
                with open(export_file, "r") as r:
                    fileinfo = r.read()
                    fileinfo = fileinfo.replace("This is where the metadata goes", filedata)
                    fileinfo = fileinfo.replace("\n\n", "\n")
                    with open(export_file, "w") as w:
                        w.write(fileinfo)
                    w.close()
    window['-OUTPUT-'].update("\nFolder inventories generated", append=True)

def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    try:
        reparse = minidom.parseString(rough_string)
        return reparse.toprettyxml(indent="    ")
    except:
        return rough_string


my_icon = b'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'

config_template = '''#NOTE: folders need to be relative to where you start the program or absolute! NOT NOT NOT based on where this config file lives\n#NOTE: you will need to enter the config file relative filepath when accessing it.\n[general]\npreservica_version = \nstandard_directory_uuid = \nsuffix_count = 3\nobject_type = multi-page document\ndelay = 300\nquiet_start = 08:00:00\nquiet_end = 08:00:01\ninterval = 300\nsound = \nexport_location = \npax_staging = \ndefault_metadata = \ntransfer_agent = \n[1_version_flat]\nroot_folder = \n[2_version_flat]\nroot_folder = \npreservation_folder = \npresentation_folder = \n[2_version_crawler]\nroot_folder = \npreservation_folder = \npresentation_folder = \n[3_version_flat]\npreservation_folder = \nintermediary_folder = \npresentation_folder = \n[3_version_crawler_tree]\nroot_folder = \npreservation_folder = preservation1\nintermediary_folder = presentation2\npresentation_folder = presentation3'''

Sg.theme('DarkTeal1')
left_layout = [[
        Sg.Checkbox(text="Validate xml", default=False, key="-VALIDATE-",
                 tooltip="Select this to validate sidecar metadata files before they are inserted into opex files, "
                         "uncheck to run tool against file set")
    ],
    [
        Sg.Radio("Simple structure", "radio1", default=False, key="-TYPE_1v-",
                 tooltip="Single representation"),
    ],
    [
        Sg.Radio("2 versions flat structure", "radio1", default=False, key="-TYPE_2v-",
                 tooltip="multiple manifestations structured roughly like:\nFolder\n   presentation2\n   "
                         "   file1.jpg\n      file2.jpg\n   preservation1\n      file1.tif\n      file2.tif"),
    ],
    [
        Sg.Radio("2 version atomic structure", "radio1", default=False, key="-TYPE_2v-tree-",
                 tooltip="multiple manifestations structured around items roughly like: \nFolder\n   File1\n      "
                         "presentation2\n         file1.pdf\n      preservation1\n         file1.tif\n         "
                         "file2.tif\nMostly use for many-to-one"),
    ],
    [
        Sg.Radio(text="3 version flat structure", group_id="radio1", default=False, key="-TYPE_3v-",
                 tooltip="multiple manifestations structured roughly like:\nFolder\n   presentation2\n   "
                         "   file1.jpg\n      file2.jpg\n   presentation3\n      file1.jpg\n      file2.jpg\n"
                         "   preservation1\n      file1.tif\n      file2.tif"),
    ],
    [
        Sg.Radio(text="3 version atomic structure", group_id="radio1", default=False, key="-TYPE_3v-tree-",
                 tooltip="multiple manifestations structure around items roughly like: \nFolder\n   File1\n      "
                         "presentation3\n         file1.pdf\n      presentation2\n         file1a.jpg\n         file1b"
                         ".jpg\n      preservation1\n         file1a.tif\n         file1b.tif\nThis is the ONLY option "
                         "for 3 version types"),
    ],
    [
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
        Sg.Text("Default metadata file if none present"),
        Sg.In(default_text="", key="-default_metadata-"),
        Sg.FileBrowse()
    ],
    [
        Sg.Push(),
        Sg.Text("root folder to start from", visible=True, key="-ROOT_Text-"),
        Sg.In("", size=(50, 1), visible=True, key="-ROOT-"),
        Sg.FolderBrowse()
    ],
    [
        Sg.Text("")
    ],
    [
        Sg.Text("")
    ],
]
right_layout = [
    [
        Sg.Text("General variables", text_color="orchid1", font=("Calibri", "12", "underline"))
    ],
    [
        Sg.Text("Item-Level Security Tag:", key="-SecurityTag_Text-"),
    ],
    [
        Sg.Radio(text="Digitized", group_id="security", default=True, key="-SECURITY_DIGITIZED-", tooltip="default option, all selected all folders will have the 'open' security tag \nto prevent immediate public access from browsing but all items will have the 'Digitized' security tag")
    ],
    [
        Sg.Radio(text="open", group_id="security", default=False, key="-SECURITY_OPEN-", tooltip="all folders will automatically have this security tag, selecting this \noption means the individual files will also have the 'open' security tag")
    ],
    [
        Sg.Radio(text="other", group_id="security", default=False, key='-SECURITY_OTHER-'),
        Sg.Input(default_text="", size=(25, 1), key='-SECURITY_OTHER_TEXT-', tooltip="Enter tag EXACTLY as it is in your system, folders will be \n'open' tag to shield from immediate public access and items will be this security tag")
    ],
    [
        Sg.Checkbox(text="incremental clean-up?", default=False, key="-CLEANUP-",
                    tooltip="Select this to remove pax staging files immediately after pax package is created\n"
                            "otherwise will only be deleted after full package compilation. Saves temporary storage use"
                            "at the expense of speed. Speed is proportional to file counts")
    ],
    [
        Sg.Text("Object type", visible=True, key="-TYPE_Text-"),
    ],
    [
        Sg.Radio("no special type", "radio2", default=False, key="-OBJECT_TYPE_normal-"),
    ],
    [
        Sg.Radio(text="Multi-page document", group_id="radio2", default=False, key="-OBJECT_TYPE_multipagedocument-")
    ],
    [
        Sg.Radio(text="Film", group_id="radio2", default=False, key="-OBJECT_TYPE_film-")
    ],
    [
        Sg.HorizontalSeparator()
    ],
    [
        Sg.Push(),
        Sg.Text(text="pax staging area", key="-temp_staging_text-"),
        Sg.Input(default_text="", size=(50, 1), key="-temp_staging-")
    ],
    [
        Sg.Push(),
        Sg.Text("top folder", visible=False, key="-1vFlat_preservation_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-1vFlat_preservation-"),
    ],
    [
        Sg.Push(),
        Sg.Text("preservation folder name", visible=False, key="-2vFlat_preservation_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-2vFlat_preservation-")
    ],
    [
        Sg.Push(),
        Sg.Text("presentation folder name", visible=False, key="-2vFlat_presentation_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-2vFlat_presentation-")
    ],
    [
        Sg.Push(),
        Sg.Text("preservation folder name", visible=False, key="-2vTree_preservation_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-2vTree_preservation-")
    ],
    [
        Sg.Push(),
        Sg.Text("presentation folder name", visible=False, key="-2vTree_presentation_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-2vTree_presentation-")
    ],
    [
        Sg.Push(),
        Sg.Text("rendered presentation folder name", visible=False, key="-3vTree_presentation3_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-3vTree_presentation3-")
    ],
    [
        Sg.Push(),
        Sg.Text("intermediary folder name", visible=False, key="-3vTree_presentation2_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-3vTree_presentation2-")
    ],
    [
        Sg.Push(),
        Sg.Text("preservation folder name", visible=False, key="-3vTree_preservation1_Text-"),
        Sg.Input("", size=(50, 1), visible=False, key="-3vTree_preservation1-")
    ],
]
bottom_layout = [

]
layout = [
    [
      Sg.Pane([Sg.Column(left_layout),Sg.Column(right_layout)], orientation='h', expand_x=True, expand_y=True)
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
        Sg.Push(),
        Sg.ProgressBar(1, orientation="h", size=(100, 20), bar_color="dark green", key="-Progress-", border_width=5,
                       relief="RELIEF_SUNKEN"),
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
        Sg.Push(),
        Sg.Image(source=my_icon),
        Sg.Multiline(default_text="Click execute to show progress\n------------------------------\nWritten for Windows with corresponding filepath length limitations\nUse Linux version in a Linux environment to circumvent this limitation", size=(100, 10),
                     auto_refresh=True, reroute_stdout=False, key="-OUTPUT-", autoscroll=True, border_width=5),
        Sg.Image(source=my_icon),
        Sg.Push(),
    ],
    ''''''
]

window = Sg.Window(
    "Opex Package Creator Graphical interface",
    layout,
    icon=my_icon,
    button_color="dark green",

)

event, values = window.read()
while True:
    event, values = window.read()
    use_config = values["-CONFIG-"]
    configfile = values['-CONFIGFILE-']
    if values['-TYPE_1v-'] is True:
        opex_type = "1versions_flat"
        window['-ROOT_Text-'].update(visible=True)
        window['-ROOT-'].update(visible=True)
        window['-temp_staging_text-'].update(visible=False)
        window['-temp_staging-'].update(visible=False)
        window['-3vTree_preservation1_Text-'].update(visible=False)
        window['-3vTree_preservation1-'].update(visible=False)
        window['-3vTree_presentation2_Text-'].update(visible=False)
        window['-3vTree_presentation2-'].update(visible=False)
        window['-3vTree_presentation3_Text-'].update(visible=False)
        window['-3vTree_presentation3-'].update(visible=False)
        window['-3vTree_preservation1_Text-'].update(visible=False)
        window['-3vTree_preservation1-'].update(visible=False)
        window['-3vTree_presentation2_Text-'].update(visible=False)
        window['-3vTree_presentation2-'].update(visible=False)
        window['-3vTree_presentation3_Text-'].update(visible=False)
        window['-3vTree_presentation3-'].update(visible=False)
        window['-2vFlat_preservation_Text-'].update(visible=False)
        window['-2vFlat_preservation-'].update(visible=False)
        window['-2vFlat_presentation_Text-'].update(visible=False)
        window['-2vFlat_presentation-'].update(visible=False)
        window['-2vTree_preservation_Text-'].update(visible=False)
        window['-2vTree_preservation-'].update(visible=False)
        window['-2vTree_presentation_Text-'].update(visible=False)
        window['-2vTree_presentation-'].update(visible=False)
    if values['-TYPE_2v-'] is True:
        opex_type = "2versions_flat"
        window['-ROOT_Text-'].update(visible=True)
        window['-ROOT-'].update(visible=True)
        window['-temp_staging_text-'].update(visible=True)
        window['-temp_staging-'].update(visible=True)
        window['-1vFlat_preservation_Text-'].update(visible=False)
        window['-1vFlat_preservation-'].update(visible=False)
        window['-3vTree_preservation1_Text-'].update(visible=False)
        window['-3vTree_preservation1-'].update(visible=False)
        window['-3vTree_presentation2_Text-'].update(visible=False)
        window['-3vTree_presentation2-'].update(visible=False)
        window['-3vTree_presentation3_Text-'].update(visible=False)
        window['-3vTree_presentation3-'].update(visible=False)
        window['-2vFlat_preservation_Text-'].update(visible=True)
        window['-2vFlat_preservation-'].update(visible=True)
        window['-2vFlat_presentation_Text-'].update(visible=True)
        window['-2vFlat_presentation-'].update(visible=True)
        window['-2vTree_preservation_Text-'].update(visible=False)
        window['-2vTree_preservation-'].update(visible=False)
        window['-2vTree_presentation_Text-'].update(visible=False)
        window['-2vTree_presentation-'].update(visible=False)
    if values['-TYPE_2v-tree-'] is True:
        opex_type = "2versions_crawler"
        window['-ROOT_Text-'].update(visible=True)
        window['-ROOT-'].update(visible=True)
        window['-temp_staging_text-'].update(visible=True)
        window['-temp_staging-'].update(visible=True)
        window['-1vFlat_preservation_Text-'].update(visible=False)
        window['-1vFlat_preservation-'].update(visible=False)
        window['-3vTree_preservation1_Text-'].update(visible=False)
        window['-3vTree_preservation1-'].update(visible=False)
        window['-3vTree_presentation2_Text-'].update(visible=False)
        window['-3vTree_presentation2-'].update(visible=False)
        window['-3vTree_presentation3_Text-'].update(visible=False)
        window['-3vTree_presentation3-'].update(visible=False)
        window['-2vFlat_preservation_Text-'].update(visible=False)
        window['-2vFlat_preservation-'].update(visible=False)
        window['-2vFlat_presentation_Text-'].update(visible=False)
        window['-2vFlat_presentation-'].update(visible=False)
        window['-2vTree_preservation_Text-'].update(visible=True)
        window['-2vTree_preservation-'].update(visible=True)
        window['-2vTree_presentation_Text-'].update(visible=True)
        window['-2vTree_presentation-'].update(visible=True)
    if values['-TYPE_3v-tree-'] is True or values['-TYPE_3v-'] is True:
        if values['-TYPE_3v-tree-'] is True:
            opex_type = "3versions_crawler_tree"
        if values['-TYPE_3v-'] is True:
            opex_type = "3versions_flat"
        window['-ROOT_Text-'].update(visible=True)
        window['-ROOT-'].update(visible=True)
        window['-temp_staging_text-'].update(visible=True)
        window['-temp_staging-'].update(visible=True)
        window['-1vFlat_preservation_Text-'].update(visible=False)
        window['-1vFlat_preservation-'].update(visible=False)
        window['-3vTree_preservation1_Text-'].update(visible=True)
        window['-3vTree_preservation1-'].update(visible=True)
        window['-3vTree_presentation2_Text-'].update(visible=True)
        window['-3vTree_presentation2-'].update(visible=True)
        window['-3vTree_presentation3_Text-'].update(visible=True)
        window['-3vTree_presentation3-'].update(visible=True)
        window['-2vFlat_preservation_Text-'].update(visible=False)
        window['-2vFlat_preservation-'].update(visible=False)
        window['-2vFlat_presentation_Text-'].update(visible=False)
        window['-2vFlat_presentation-'].update(visible=False)
        window['-2vTree_preservation_Text-'].update(visible=False)
        window['-2vTree_preservation-'].update(visible=False)
        window['-2vTree_presentation_Text-'].update(visible=False)
        window['-2vTree_presentation-'].update(visible=False)
    # assign variables based on inputs
    object_type = ""
    if values['-OBJECT_TYPE_normal-'] is True:
        object_type = ""
    if values['-OBJECT_TYPE_multipagedocument-'] is True:
        object_type = "multi-page document"
    if values['-OBJECT_TYPE_film-'] is True:
        object_type = "film"
    staging = values['-UploadStaging-']
    asset_tag = "open"
    if values["-SECURITY_DIGITIZED-"] is True:
        asset_tag = "Digitized"
    if values['-SECURITY_OPEN-'] is True:
        asset_tag = "open"
    if values['-SECURITY_OTHER-'] is True:
        asset_tag = values['-SECURITY_OTHER_Text-']
    log = open("opex_generator_log.txt", "a")
    helperFile = "helper.txt"
    counter1 = 0
    counter2 = 0
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
            if opex_type == "1versions_flat":
                var = config.get('1_version_flat', 'root_folder')
                window['-ROOT-'].update(var)
                print("something")
            if opex_type == "2versions_flat":
                var = config.get('2_version_flat', 'root_folder')
                window['-ROOT-'].update(var)
                var = config.get("general", "pax_staging")
                window['-temp_staging-'].update(var)
                var = config.get('2_version_flat', 'preservation_folder')
                window['-2vFlat_preservation-'].update(var)
                var = config.get('2_version_flat', 'presentation_folder')
                window['-2vFlat_presentation-'].update(var)
                print("something else")
            if opex_type == "2versions_crawler":
                var = config.get('2_version_crawler', 'root_folder')
                window['-ROOT-'].update(var)
                var = config.get("general", "pax_staging")
                window['-temp_staging-'].update(var)
                var = config.get('2_version_crawler', 'preservation_folder')
                window['-2vTree_preservation-'].update(var)
                var = config.get('2_version_crawler', 'presentation_folder')
                window['-2vTree_presentation-'].update(var)
                print("something more")
            if opex_type == "3versions_flat":
                var = config.get('3_version_flat', 'root_folder')
                window['-ROOT-'].update(var)
                var = config.get("general", "pax_staging")
                window['-temp_staging-'].update(var)
                var = config.get('3_version_flat', 'preservation_folder')
                window['-3vTree_preservation1-'].update(var)
                var = config.get('3_version_flat', 'intermediary_folder')
                window['-3vTree_presentation2-'].update(var)
                var = config.get('3_version_flat', 'presentation_folder')
                window['-3vTree_presentation3-'].update(var)
                print("something else")
            if opex_type == "3versions_crawler_tree":
                var = config.get('3_version_crawler_tree', 'root_folder')
                window['-ROOT-'].update(var)
                var = config.get("general", "pax_staging")
                window['-temp_staging-'].update(var)
                var = config.get('3_version_crawler_tree', 'preservation_folder')
                window['-3vTree_preservation1-'].update(var)
                var = config.get('3_version_crawler_tree', 'intermediary_folder')
                window['-3vTree_presentation2-'].update(var)
                var = config.get('3_version_crawler_tree', 'presentation_folder')
                window['-3vTree_presentation3-'].update(var)
                print("something even more")
            var = config.get('general', 'default_metadata')
            window['-default_metadata-'].update(var)
            var = config.get('general', 'export_location')
            window['-UploadStaging-'].update(var)
            window['-OUTPUT-'].update("\nConfiguration loaded", append=True)
    # here we go again
    exclude_list = ['.metadata', 'Thumbs.db']
    if event == "Execute":
        export_dir = values['-UploadStaging-']
        walker = values['-ROOT-']
        my_container = walker.split("/")[-1]
        package_identifier = str(uuid.uuid4())
        package_name = package_identifier
        if values['-VALIDATE-'] is True:
            flag = False
            baddie_list = []
            window['-OUTPUT-'].update("\nstarting xml validation routine, remember to uncheck validation to run opex packaging", append=True)
            master_counter = 0
            for dirpath, dirnames, filenames in os.walk(walker):
                for filename in filenames:
                    if filename.endswith(".xml") or filename.endswith(".metadata"):
                        master_counter += 1
            window['-OUTPUT-'].update("\ngathered progress bar information", append=True)
            xml_count = 0
            for dirpath, dirnames, filenames in os.walk(walker):
                for filename in filenames:
                    if filename.endswith(".xml") or filename.endswith(".metadata"):
                        filename = os.path.join(dirpath, filename)
                        try:
                            ET.parse(filename)
                        except:
                            window['-OUTPUT-'].update(f"\nparsing error with {filename}", append=True)
                            flag = True
                            baddie_list.append(filename)
                        xml_count += 1
                        window['-Progress-'].update_bar(xml_count, master_counter)
            if flag is False:
                window['-OUTPUT-'].update("\nNo xml errors found, good job, okay to continue. Uncheck validation box", append=True)
            if flag is True:
                for item in baddie_list:
                    window['-OUTPUT-'].update(f"\nXML error in {item}", append=True)
                window['-OUTPUT-'].update("\nXML errors found, scroll through dialog box to see where", append=True)
        if opex_type == "1versions_flat" and values['-VALIDATE-'] is False:
            default_metadata = values['-default_metadata-']
            progress = progressCounty(walker)
            counter = 0
            for dirpath, dirnames, filenames in os.walk(walker):
                for filename in filenames:
                    valuables = ""
                    valuables = dict()
                    if not filename.endswith(tuple(exclude_list)):
                        filename1 = os.path.join(dirpath, filename)
                        filename2 = filename1.replace(walker, f"{export_dir}/{package_name}/{my_container}")
                        item_metadata = default_metadata
                        if os.path.isfile(f"{filename1}.metadata"):
                            item_metadata = f"{filename1}.metadata"
                        valuables['asset_id'] = filename.replace(f'.{filename.split(".")[-1]}',"")
                        valuables['asset_title'] = valuables['asset_id']
                        valuables['asset_description'] = valuables['asset_id']
                        valuables['asset_tag'] = asset_tag
                        valuables['metadata_file'] = item_metadata
                        create_directory(filename2)
                        shutil.copy2(filename1, filename2)
                        shutil.copystat(filename1, filename2)
                        source_checksum = create_sha256(filename1)
                        target_checksum = create_sha256(filename2)
                        if source_checksum != target_checksum:
                            print(f"something went wrong with processing {filename}")
                            sys.exit()
                        else:
                            window['-OUTPUT-'].update(f"\n{filename} verified", append=True)
                        counter += 1
                        window['-Progress-'].update_bar(counter, progress)
                        make_opex(valuables, filename2)
            make_folder_opex(walker, export_dir, package_name, default_metadata)
            window['-OUTPUT-'].update(f"\nall done!", append=True)
        if opex_type == "2versions_flat" and values['-VALIDATE-'] is False:
            pax_staging = values['-temp_staging-']
            preservation1 = values['-2vFlat_preservation-']
            presentation2 = values['-2vFlat_presentation-']
            default_metadata = values['-default_metadata-']
            progress = progressCounty(walker)
            counter = 0
            for dirpath, dirnames, filenames in os.walk(walker):
                for filename in filenames:
                    valuables = ""
                    valuables = dict()
                    if not filename.endswith(tuple(exclude_list)):
                        if dirpath.endswith(preservation1):
                            valuables = ""
                            valuables = dict()
                            filename1 = os.path.join(dirpath, filename)
                            container = filename.replace(f'.{filename.split(".")[-1]}',"")
                            temp_dir = os.path.join(pax_staging, container)
                            temp_file = f"{temp_dir}.pax"
                            opex_target_dir = dirpath.replace(walker, f"{export_dir}/{package_name}/{my_container}").replace(preservation1, "")
                            target_pax = f"{opex_target_dir}/{container}.pax.zip"
                            target_metadata = f"{target_pax}.opex"
                            preservation_representation = f"{temp_dir}/Representation_Preservation/{container}/{filename}"
                            create_directory(preservation_representation)
                            shutil.copy2(filename1, preservation_representation)
                            shutil.copystat(filename1, preservation_representation)
                            source_checksum = create_sha256(filename1)
                            target_checksum = create_sha256(preservation_representation)
                            if source_checksum != target_checksum:
                                print(f"something went wrong with processing {filename}")
                                sys.exit()
                            else:
                                window['-OUTPUT-'].update(f"\n{filename} verified", append=True)
                            counter += 1
                            window['-Progress-'].update_bar(counter, progress)
                            access_directory = dirpath.replace(preservation1, presentation2)
                            access_file_root = filename1.replace(dirpath, access_directory)
                            files_list = [q for q in os.listdir(access_directory) if os.path.isfile(f"{access_directory}/{q}")]
                            for possibility in files_list:
                                if not possibility.endswith(".metadata"):
                                    real_possibility = possibility.replace(f".{possibility.split('.')[-1]}", "")
                                    if container == real_possibility:
                                        filename2 = os.path.join(access_directory, possibility)
                                        presentation_representation = f"{temp_dir}/Representation_Access/{container}/{possibility}"
                                        create_directory(presentation_representation)
                                        shutil.copy2(filename2, presentation_representation)
                                        shutil.copystat(filename2, presentation_representation)
                                        source_checksum = create_sha256(filename2)
                                        target_checksum = create_sha256(presentation_representation)
                                        if source_checksum != target_checksum:
                                            print(f"something went wrong with processing {possibility}")
                                            sys.exit()
                                        else:
                                            window['-OUTPUT-'].update(f"\n{possibility} verified", append=True)
                                        counter += 1
                                        window['-Progress-'].update_bar(counter, progress)
                            item_metadata = default_metadata
                            if os.path.isfile(f"{filename1}.metadata"):
                                item_metadata = f"{filename1}.metadata"
                            elif os.path.isfile(f"{filename2}.metadata"):
                                item_metadata = f"{filename2}.metadata"
                            shutil.make_archive(f"{temp_file}", "zip", temp_dir)
                            create_directory(target_pax)
                            shutil.move(f"{temp_file}.zip", target_pax)
                            valuables['asset_id'] = container
                            valuables['asset_title'] = valuables['asset_id']
                            valuables['asset_description'] = valuables['asset_id']
                            valuables['asset_tag'] = asset_tag
                            valuables['metadata_file'] = item_metadata
                            make_opex(valuables, target_pax)
                if window['-CLEANUP-'] is True:
                    cleanup(pax_staging)
            cleanup(pax_staging)
            make_folder_opex(walker, export_dir, package_name, default_metadata)
            window['-OUTPUT-'].update(f"\nall done! Don't forget to remove any lingering staging files at {temp_dir}", append=True)
        if opex_type == "2versions_crawler" and values['-VALIDATE-'] is False:
            pax_staging = values['-temp_staging-']
            preservation1 = values['-2vTree_preservation-']
            presentation2 = values['-2vTree_presentation-']
            default_metadata = values['-default_metadata-']
            progress = progressCounty(walker)
            counter = 0
            for dirpath, dirnames, filenames in os.walk(walker):
                if dirpath.endswith(preservation1):
                    container = dirpath.split('/')[-1].split('\\')[-2]
                    temp_dir = os.path.join(pax_staging, container)
                    temp_file = f"{temp_dir}.pax"
                    opex_target_dir = dirpath.replace(walker, f"{export_dir}/{package_name}/{my_container}").replace(preservation1, "")
                    target_pax = f"{opex_target_dir[:-1]}.pax.zip"
                    flag = False
                    flag_check = []
                    for filename in filenames:
                        if object_type != "film":
                            if not filename.endswith(".metadata"):
                                root_name = filename.split(".")[0]
                                if root_name in flag_check:
                                    flag = True
                                else:
                                    flag_check.append(root_name)
                    for filename in filenames:
                        valuables = ""
                        valuables = dict()
                        if not filename.endswith(tuple(exclude_list)):
                            valuables = ""
                            valuables = dict()
                            filename1 = os.path.join(dirpath, filename)
                            preservation_representation = os.path.join(temp_dir, "Representation_Preservation")
                            if object_type == "film":
                                filename2 = film_check(preservation_representation, filename)
                            elif flag is True:
                                filename2 = f"{preservation_representation}/{filename.replace('.', '_')}/{filename}"
                            else:
                                filename2 = f"{preservation_representation}/{filename.split('.')[0]}/{filename}"
                            create_directory(filename2)
                            shutil.copy2(filename1, filename2)
                            shutil.copystat(filename1, filename2)
                            source_checksum = create_sha256(filename1)
                            target_checksum = create_sha256(filename2)
                            if source_checksum != target_checksum:
                                print(f"something went wrong with process {filename}")
                                sys.exit()
                            else:
                                window['-OUTPUT-'].update(f"\n{filename} verified", append=True)
                            counter += 1
                            window['-Progress-'].update_bar(counter, progress)
                    access_directory = dirpath.replace(preservation1, presentation2)
                    files_list = [q for q in os.listdir(access_directory) if os.path.isfile(f"{access_directory}/{q}")]
                    flag = False
                    flag_check = []
                    presentation_representation = os.path.join(temp_dir, "Representation_Access")
                    for possibility in files_list:
                        if object_type != "film":
                            if not possibility.endswith(".metadata"):
                                root_name = possibility.split(".")[0]
                                if root_name in flag_check:
                                    flag = True
                                else:
                                    flag_check.append(root_name)
                    for possibility in files_list:
                        if not possibility.endswith(tuple(exclude_list)):
                            source = os.path.join(access_directory, possibility)
                            if object_type == "film":
                                target = film_check(presentation_representation, possibility)
                            elif flag is True:
                                target = f"{presentation_representation}/{possibility.replace('.', '_')}/{possibility}"
                            else:
                                target = f"{presentation_representation}/{possibility.split('.')[0]}/{possibility}"
                            create_directory(target)
                            shutil.copy2(source, target)
                            shutil.copystat(source, target)
                            source_checksum = create_sha256(source)
                            target_checksum = create_sha256(target)
                            if source_checksum != target_checksum:
                                print(f"something went wrong with process {possibility}")
                                sys.exit()
                            else:
                                window['-OUTPUT-'].update(f"\n{possibility} verified", append=True)
                            counter += 1
                            window['-Progress-'].update_bar(counter, progress)
                    item_metadata = default_metadata
                    if os.path.isfile(f"{dirpath.replace(preservation1, '')}.metadata"):
                        item_metadata = f"{dirpath.replace(preservation1, '').metadata}"
                    elif os.path.isfile(f"{dirpath}/{container}.metadata"):
                        item_metadata = f"{dirpath}/{container}.metadata"
                    elif os.path.isfile(f"{dirpath.replace(preservation1, presentation2)}/{container}.metadata"):
                        item_metadata = f"{dirpath.replace(preservation1, presentation2)}/{container}.metadata"
                    shutil.make_archive(temp_file, "zip", temp_dir)
                    create_directory(target_pax)
                    shutil.move(f"{temp_file}.zip", target_pax)
                    window['-OUTPUT-'].update(f"\n{container} packaged", append=True)
                    valuables = ""
                    valuables = dict()
                    valuables['asset_id'] = container
                    valuables['asset_title'] = valuables['asset_id']
                    if object_type != "":
                        valuables['asset_description'] = object_type
                    else:
                        valuables['asset_description'] = valuables['asset_id']
                    valuables['asset_tag'] = asset_tag
                    valuables['metadata_file'] = item_metadata
                    make_opex(valuables, target_pax)
                if window['-CLEANUP-'] is True:
                    cleanup(pax_staging)
            cleanup(pax_staging)
            make_folder_opex(walker, export_dir, package_name, default_metadata)
            window['-OUTPUT-'].update(f"\nall done! Don't forget to remove any lingering staging files at {pax_staging}", append=True)
            window['-OUTPUT-'].update("\nAll done", append=True)
        if opex_type == "3versions_flat" and values['-VALIDATE-'] is False:
            pax_staging = values['-temp_staging-']
            preservation1 = values['-3vTree_preservation1-']
            presentation2 = values['-3vTree_presentation2-']
            presentation3 = values['-3vTree_presentation3-']
            default_metadata = values['-default_metadata-']
            progress = progressCounty(walker)
            counter = 0
            for dirpath, dirnames, filenames in os.walk(walker):
                for filename in filenames:
                    valuables = ""
                    valuables = dict()
                    if not filename.endswith(tuple(exclude_list)):
                        if dirpath.endswith(preservation1):
                            valuables = ""
                            valuables = dict()
                            filename1 = os.path.join(dirpath, filename)
                            container = filename.replace(f'.{filename.split(".")[-1]}',"")
                            temp_dir = os.path.join(pax_staging, container)
                            temp_file = f"{temp_dir}.pax"
                            opex_target_dir = dirpath.replace(walker, f"{export_dir}/{package_name}/{my_container}").replace(preservation1, "")
                            target_pax = f"{opex_target_dir}/{container}.pax.zip"
                            target_metadata = f"{target_pax}.opex"
                            preservation_representation = f"{temp_dir}/Representation_Preservation/{container}/{filename}"
                            create_directory(preservation_representation)
                            shutil.copy2(filename1, preservation_representation)
                            shutil.copystat(filename1, preservation_representation)
                            source_checksum = create_sha256(filename1)
                            target_checksum = create_sha256(preservation_representation)
                            if source_checksum != target_checksum:
                                print(f"something went wrong with processing {filename}")
                                sys.exit()
                            else:
                                window['-OUTPUT-'].update(f"\n{filename} verified", append=True)
                            counter += 1
                            window['-Progress-'].update_bar(counter, progress)
                            access_directory = dirpath.replace(preservation1, presentation2)
                            access_file_root = filename1.replace(dirpath, access_directory)
                            files_list = [q for q in os.listdir(access_directory) if os.path.isfile(f"{access_directory}/{q}")]
                            for possibility in files_list:
                                if not possibility.endswith(".metadata"):
                                    real_possibility = possibility.replace(f".{possibility.split('.')[-1]}", "")
                                    if container == real_possibility:
                                        filename2 = os.path.join(access_directory, possibility)
                                        presentation_representation = f"{temp_dir}/Representation_Access_1/{container}/{possibility}"
                                        create_directory(presentation_representation)
                                        shutil.copy2(filename2, presentation_representation)
                                        shutil.copystat(filename2, presentation_representation)
                                        source_checksum = create_sha256(filename2)
                                        target_checksum = create_sha256(presentation_representation)
                                        if source_checksum != target_checksum:
                                            print(f"something went wrong with processing {possibility}")
                                            sys.exit()
                                        else:
                                            window['-OUTPUT-'].update(f"\n{possibility} verified", append=True)
                                        counter += 1
                                        window['-Progress-'].update_bar(counter, progress)
                            access_directory = dirpath.replace(preservation1, presentation3)
                            access_file_root = filename1.replace(dirpath, access_directory)
                            files_list = [q for q in os.listdir(access_directory) if os.path.isfile(f"{access_directory}/{q}")]
                            for possibility in files_list:
                                if not possibility.endswith(".metadata"):
                                    real_possibility = possibility.replace(f".{possibility.split('.')[-1]}", "")
                                    if container == real_possibility:
                                        filename2 = os.path.join(access_directory, possibility)
                                        presentation_representation = f"{temp_dir}/Representation_Access_2/{container}/{possibility}"
                                        create_directory(presentation_representation)
                                        shutil.copy2(filename2, presentation_representation)
                                        shutil.copystat(filename2, presentation_representation)
                                        source_checksum = create_sha256(filename2)
                                        target_checksum = create_sha256(presentation_representation)
                                        if source_checksum != target_checksum:
                                            print(f"something went wrong with processing {possibility}")
                                            sys.exit()
                                        else:
                                            window['-OUTPUT-'].update(f"\n{possibility} verified", append=True)
                                        counter += 1
                                        window['-Progress-'].update_bar(counter, progress)
                            item_metadata = default_metadata
                            if os.path.isfile(f"{filename1}.metadata"):
                                item_metadata = f"{filename1}.metadata"
                            elif os.path.isfile(f"{filename2}.metadata"):
                                item_metadata = f"{filename2}.metadata"
                            shutil.make_archive(f"{temp_file}", "zip", temp_dir)
                            create_directory(target_pax)
                            shutil.move(f"{temp_file}.zip", target_pax)
                            valuables['asset_id'] = container
                            valuables['asset_title'] = valuables['asset_id']
                            valuables['asset_description'] = valuables['asset_id']
                            valuables['asset_tag'] = asset_tag
                            valuables['metadata_file'] = item_metadata
                            make_opex(valuables, target_pax)
                if window['-CLEANUP-'] is True:
                    cleanup(pax_staging)
            cleanup(pax_staging)
            make_folder_opex(walker, export_dir, package_name, default_metadata)
            window['-OUTPUT-'].update(f"\nall done! Don't forget to remove any lingering staging files at {temp_dir}", append=True)
        if opex_type == "3versions_crawler_tree" and values['-VALIDATE-'] is False:
            pax_staging = values['-temp_staging-']
            preservation1 = values['-3vTree_preservation1-']
            presentation2 = values['-3vTree_presentation2-']
            presentation3 = values['-3vTree_presentation3-']
            default_metadata = values['-default_metadata-']
            progress = progressCounty(walker)
            counter = 0
            for dirpath, dirnames, filenames in os.walk(walker):
                if dirpath.endswith(preservation1):
                    container = dirpath.split('/')[-1].split('\\')[-2]
                    temp_dir = os.path.join(pax_staging, container)
                    temp_file = f"{temp_dir}.pax"
                    opex_target_dir = dirpath.replace(walker, f"{export_dir}/{package_name}/{my_container}").replace(preservation1, "")
                    target_pax = f"{opex_target_dir[:-1]}.pax.zip"
                    flag = False
                    flag_check = []
                    for filename in filenames:
                        if object_type != "film":
                            if not filename.endswith(".metadata"):
                                root_name = filename.split(".")[0]
                                if root_name in flag_check:
                                    flag = True
                                else:
                                    flag_check.append(root_name)
                    for filename in filenames:
                        valuables = ""
                        valuables = dict()
                        if not filename.endswith(tuple(exclude_list)):
                            valuables = ""
                            valuables = dict()
                            filename1 = os.path.join(dirpath, filename)
                            presentation_representation_1 = os.path.join(temp_dir, "Representation_Access_1")
                            presentation_representation_2 = os.path.join(temp_dir, "Representation_Access_2")
                            preservation_representation = os.path.join(temp_dir, "Representation_Preservation")
                            if object_type == "film":
                                filename2 = film_check(preservation_representation, filename)
                            elif flag is True:
                                filename2 = f"{preservation_representation}/{filename.replace('.', '_')}/{filename}"
                            else:
                                filename2 = f"{preservation_representation}/{filename.split('.')[0]}/{filename}"
                            create_directory(filename2)
                            shutil.copy2(filename1, filename2)
                            shutil.copystat(filename1, filename2)
                            source_checksum = create_sha256(filename1)
                            target_checksum = create_sha256(filename2)
                            if source_checksum != target_checksum:
                                print(f"something went wrong with process {filename}")
                                sys.exit()
                            else:
                                window['-OUTPUT-'].update(f"\n{filename} verified", append=True)
                            counter += 1
                            window['-Progress-'].update_bar(counter, progress)
                    access_directory = dirpath.replace(preservation1, presentation2)
                    files_list = [q for q in os.listdir(access_directory) if os.path.isfile(f"{access_directory}/{q}")]
                    flag = False
                    flag_check = []
                    for possibility in files_list:
                        if object_type != "film":
                            root_name = possibility.split(".")[0]
                            if not possibility.endswith(".metadata"):
                                if root_name in flag_check:
                                    flag = True
                                else:
                                    flag_check.append(root_name)
                    for possibility in files_list:
                        if not possibility.endswith(tuple(exclude_list)):
                            source = os.path.join(access_directory, possibility)
                            if object_type == "film":
                                target = film_check(presentation_representation_1, possibility)
                            elif flag is True:
                                target = f"{presentation_representation_1}/{possibility.replace('.', '_')}/{possibility}"
                            else:
                                target = f"{presentation_representation_1}/{possibility.split('.')[0]}/{possibility}"
                            create_directory(target)
                            shutil.copy2(source, target)
                            shutil.copystat(source, target)
                            source_checksum = create_sha256(source)
                            target_checksum = create_sha256(target)
                            if source_checksum != target_checksum:
                                print(f"something went wrong with process {possibility}")
                                sys.exit()
                            else:
                                window['-OUTPUT-'].update(f"\n{possibility} verified", append=True)
                            counter += 1
                            window['-Progress-'].update_bar(counter, progress)
                    access_directory = dirpath.replace(preservation1, presentation3)
                    files_list = [q for q in os.listdir(access_directory) if os.path.isfile(f"{access_directory}/{q}")]
                    flag = False
                    flag_check = []
                    for possibility in files_list:
                        if object_type != "film":
                            root_name = possibility.split(".")[0]
                            if not possibility.endswith(".metadata"):
                                if root_name in flag_check:
                                    flag = True
                                else:
                                    flag_check.append(root_name)
                    for possibility in files_list:
                        if not possibility.endswith(tuple(exclude_list)):
                            source = os.path.join(access_directory, possibility)
                            if object_type == "film":
                                target = film_check(presentation_representation_2, possibility)
                            elif flag is True:
                                target = f"{presentation_representation_2}/{possibility.replace('.', '_')}/{possibility}"
                            else:
                                target = f"{presentation_representation_2}/{possibility.split('.')[0]}/{possibility}"
                            create_directory(target)
                            shutil.copy2(source, target)
                            shutil.copystat(source, target)
                            source_checksum = create_sha256(source)
                            target_checksum = create_sha256(target)
                            if source_checksum != target_checksum:
                                print(f"something went wrong with process {possibility}")
                                sys.exit()
                            else:
                                window['-OUTPUT-'].update(f"\n{possibility} verified", append=True)
                            counter += 1
                            window['-Progress-'].update_bar(counter, progress)
                    item_metadata = default_metadata
                    if os.path.isfile(f"{dirpath.replace(preservation1, '')}.metadata"):
                        item_metadata = f"{dirpath.replace(preservation1, '').metadata}"
                    elif os.path.isfile(f"{dirpath}/{container}.metadata"):
                        item_metadata = f"{dirpath}/{container}.metadata"
                    elif os.path.isfile(f"{dirpath.replace(preservation1, presentation2)}/{container}.metadata"):
                        item_metadata = f"{dirpath.replace(preservation1, presentation2)}/{container}.metadata"
                    elif os.path.isfile(f"{dirpath.replace(preservation1, presentation3)}/{container}.metadata"):
                        item_metadata = f"{dirpath.replace(preservation1, presentation3)}/{container}.metadata"
                    shutil.make_archive(temp_file, "zip", temp_dir)
                    create_directory(target_pax)
                    shutil.move(f"{temp_file}.zip", target_pax)
                    window['-OUTPUT-'].update(f"\n{container} packaged", append=True)
                    valuables['asset_id'] = container
                    valuables['asset_title'] = valuables['asset_id']
                    if object_type != "":
                        valuables['asset_description'] = object_type
                    else:
                        valuables['asset_description'] = valuables['asset_id']
                    valuables['asset_tag'] = asset_tag
                    valuables['metadata_file'] = item_metadata
                    make_opex(valuables, target_pax)
                if window['-CLEANUP-'] is True:
                    cleanup(pax_staging)
            cleanup(pax_staging)
            make_folder_opex(walker, export_dir, package_name, default_metadata)
            window['-OUTPUT-'].update(f"\nall done! Don't forget to remove any lingering staging files at {pax_staging}", append=True)
            window['-OUTPUT-'].update("\nAll done", append=True)
    if event == "Close" or event == Sg.WIN_CLOSED:
        break
window.close()