import os
import time
from PIL import Image
import PySimpleGUI as SG
import errno


def create_directory(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


def multipleImages(filepath=str, extension=str, intermediary=str, resolution=str):
    counter = 0
    for dirpath, dirnames, filenames in os.walk(filepath):
        for filename in filenames:
            if filename.endswith(extension):
                counter += 1
    window['-OUTPUT-'].update(f"\n{filepath} has {counter} {extension} files, starting processing", append=True)
    counter1 = 0
    for dirpath, dirnames, filenames in os.walk(filepath):
        for filename in filenames:
            if filename.endswith(extension):
                filename1 = os.path.join(dirpath, filename)
                filename2 = f"{intermediary}/{filename[:-len(extension)]}.jpg"
                create_directory(filename2)
                resolution = int(resolution)
                counter1 += 1
                if not os.path.isfile(filename2):
                    Image.MAX_IMAGE_PIXELS = None
                    size = 10000, 2059
                    im = Image.open(filename1)
                    rgb_im = im.convert('RGB')
                    rgb_im.thumbnail(size, Image.LANCZOS)
                    temp = rgb_im.save(filename2, format='JPEG', dpi=(resolution, resolution), optimize=True)
                    now = time.asctime()
                    window['-OUTPUT-'].update(f"\n{filename2} generated at {now}", append=True)
                quick_math = str((counter1/counter)*100)[:5]
                window["-progress_percent2-"].update(f"{quick_math}%")
                window["-Progress2-"].update_bar(counter1, counter)


def singleImage(file_to_convert=str, extension=str, intermediary=str, resolution=str):
    filename1 = file_to_convert
    filename2 = filename.split("/")[-1].split("\\")[-1][:-len(extension)]
    filename2 = f"{intermediary}/{filename2}.jpg"
    create_directory(filename2)
    if not os.path.isfile(filename2):
        Image.MAX_IMAGE_PIXELS = None
        size = 10000, 2059
        im = Image.open(filename1)
        rgb_im = im.convert('RGB')
        rgb_im.thumbnail(size, Image.LANCZOS)
        temp = rgb_im.save(filename2, format='JPEG', dpi=(resolution, resolution), optimize=True)
        now = time.asctime()
        window['-OUTPUT-'].update(f"\n{filename2} processed at {now}", append=True)
        print(f"{filename2} processed at {now}")


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

SG.theme("LightBlue2")
layout = [
    [
        SG.Push(),
        SG.Text("This small app will generate jpegs off of a master file keyed on the file type \ndesignated by the extension. Resolution is defaulted to 150dpi"),
        SG.Push()
    ],
    [
        SG.Text("Type of JPEG generation"),
        SG.Radio(text="Directory crawl", group_id="function1", default=True, key="-crawl-"),
        SG.Radio(text="Single image", group_id="function1", default=False, key="-single-")
    ],
    [
        SG.Push(),
        SG.Text("output image resolution", key="-Resolution_Text-"),
        SG.In(default_text="150", key="-RESOLUTION-"),
    ],
    [
        SG.Push(),
        SG.Text("File extension for the files to be converted to jpeg, must be EXACT"),
        SG.In(default_text="tif", key="-EXTENSION-")
    ],
    [
        SG.HorizontalSeparator()
    ],
    [
        SG.Push(),
        SG.Text("For single image input"),
        SG.In(size=(50, 1), enable_events=True, key='-SingleImage-'),
        SG.FileBrowse()
    ],
    [
        SG.Push(),
        SG.Text("Single Image Output Folder"),
        SG.In(default_text="", key="-SingleImageOutput-"),
        SG.FolderBrowse()
    ],
    [
        SG.HorizontalSeparator(),
    ],
    [
        SG.Push(),
        SG.Text("Will crawl an entire folder structure and check for folders of master image folder name, \nthen output a companion folder with the output folder name")
    ],
    [
        SG.Push(),
        SG.Text("Root folder to Start from", key="-Source_Text-"),
        SG.In(default_text="", size=(50, 1), key="-SOURCE-"),
        SG.FolderBrowse()
    ],
    [
        SG.Push(),
        SG.Text("Master images folders name", key="-Preservation_Text-"),
        SG.In(default_text="preservation1", size=(50, 1), key="-PRESERVATION-")
    ],
    [
        SG.Push(),
        SG.Text("Derivative JPEG output folder name", key="-Presentation_Text-"),
        SG.In(default_text="presentation2", size=(50, 1), key="-PRESENTATION-")
    ],
    [
        SG.Push(),
        SG.Button(button_text="Execute", bind_return_key=True),
        SG.Push()
    ],
    [
        SG.Text("Select Close to close the window")
    ],
    [
        SG.Button(button_text="Close")
    ],
    [
        SG.Push(),
        SG.Text("Overall progress"),
        SG.Push()
    ],
    [
        SG.Push(),
        SG.T("00.00%", key="-progress_percent-"),
        SG.ProgressBar(max_value=1, orientation="h", size=(50, 20), bar_color="dark green", key="-Progress1-", border_width=5, relief="RELIEF_SUNKEN"),
        SG.Push()
    ],
    [
        SG.Push(),
        SG.Text("Current folder progress"),
        SG.Push()
    ],
    [
        SG.Push(),
        SG.T("00.00%", key="-progress_percent2-"),
        SG.ProgressBar(max_value=1, orientation="h", size=(50, 20), bar_color="dark green", key="-Progress2-", border_width=5, relief="RELIEF_SUNKEN"),
        SG.Push()
    ],
    [
        SG.Push(),
        SG.Text("Status  "),
        SG.Multiline(default_text="", auto_refresh=True, reroute_stdout=False, key="-OUTPUT-", autoscroll=True, border_width=5, size=(70, 15)),
        SG.Push()
    ]
]

window = SG.Window("JPEG Generator Utility", layout, icon=my_icon, button_color="dark green")

event, values = window.read()

while True:
    event, values = window.read()
    source_single = values['-SingleImage-']
    output_single = values["-SingleImageOutput-"]
    source_crawl = values["-SOURCE-"]
    source_preservation = values["-PRESERVATION-"]
    output_presentation = values["-PRESENTATION-"]
    input_extension = values["-EXTENSION-"]
    if values["-crawl-"] is True:
        directory_crawl = True
    if values["-single-"] is True:
        directory_crawl = False
    resolution = values["-RESOLUTION-"]
    if event == "Execute":
        if directory_crawl is False:
            singleImage(source_single, input_extension, output_single, resolution)
        if directory_crawl is True:
            window['-OUTPUT-'].update("\ngathering file count", append=True)
            set_list = set()
            for dirpath, dirnames, filenames in os.walk(source_crawl):
                for filename in filenames:
                    if source_preservation in dirpath and filename.endswith(input_extension):
                        set_list.add(dirpath)
            set_list = list(set_list)
            set_list.sort()
            master = len(set_list)
            counter1 = 0
            for item in set_list:
                intermediary = item.replace(source_preservation, output_presentation)
                multipleImages(item, input_extension, intermediary, resolution)
                counter1 += 1
                quick_math = str((counter1/master)*100)[:5]
                window["-progress_percent-"].update(f"{quick_math}%")
                window["-Progress1-"].update_bar(counter1, master)
                window["-OUTPUT-"].update(f"\nfinished processing {item}", append=True)
            window['-OUTPUT-'].update(f"\nall done", append=True)
    if event == "Close" or event == SG.WIN_CLOSED:
        break