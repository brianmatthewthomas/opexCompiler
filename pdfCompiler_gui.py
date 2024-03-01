import os
import PySimpleGUI as SG
import pytesseract
import io
import PyPDF2
import pdf2image
import PIL
import img2pdf
import time
import lxml.etree as ET
import errno

def create_directory(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

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

namespaces = {'tslac': "https://www.tsl.texas.gov/", 'dcterms': "http://dublincore.org/documents/dcmi-terms/"}


SG.theme("DarkGreen5")
layout = [
    [
        SG.Text("Type of OCR aggregation"),
        SG.Radio(text="OCR", group_id="function1", default=False, key="-OCR-"),
        SG.Radio(text="No OCR", group_id="function1", default=False, key="-NOCR-"),
        SG.Radio(text="Auto", group_id="function1", default=True, key="-AUTO-")
    ],
    [
        SG.Push(),
        SG.Text("Source folder", visible=True, key='-Source_Text-'),
        SG.In("", size=(50, 1), visible=True, key='-SOURCE-'),
        SG.FolderBrowse()
    ],
    [
        SG.Push(),
        SG.Text(text="Output Folder name", visible=True, key="-OUTPUT_Folder_Text"),
        SG.In(default_text="preservica_presentation3_lnk", size=(50, 1), visible=True, key='-OUTPUT_Folder-')
    ],
    [
        SG.Push(),
        SG.Text(text='Preservation Folder name', visible=True, key='-PRESERVATION_Folder_Text-'),
        SG.In(default_text="preservica_preservation1_lnk", size=(50, 1), visible=True, key='-PRESERVATION_Folder-')
    ],
    [
        SG.Push(),
        SG.Text(text="Presentation Folder name", visible=True, key="-PRESENTATION_Folder_Text-"),
        SG.In(default_text="preservica_presentation2_lnk", size=(50, 1), visible=True, key="-PRESENTATION_Folder-")
    ],
    [
        SG.Text("Select execute to start processing")
    ],
    [
        SG.Push(),
        SG.Button("Execute", tooltip="This will start the PDF aggregation running", bind_return_key=True),
        SG.Push()
    ],
    [
        SG.Text("Select Close to close the window")
    ],
    [
        SG.Button("Close", tooltip="Close this window, if mid-process you may need to hit the X to close the window")
    ],
    [
        SG.Text("Overall progress")
    ],
    [
        SG.ProgressBar(1, orientation="h", size=(50, 20), bar_color="dark green", key="-Progress-", border_width=5, relief="RELIEF_SUNKEN")
    ],
    [
      SG.Text("Current PDF progress")
    ],
    [
        SG.ProgressBar(1, orientation="h", size=(50, 20), bar_color="dark green", key="-PDF_Progress-", border_width=5, relief="RELIEF_SUNKEN")
    ],
    [
        SG.Text("", key="-STATUS-")
    ],
    [
        SG.Multiline(default_text="Click execute to start PDF aggregation, if using auto all content to be OCR'd MUST be in a folder with 'ocr' in the filepath",
                     auto_refresh=True, reroute_stdout=False, key="-OUTPUT-", autoscroll=True, border_width=5, size=(70, 15))
    ]
]

window = SG.Window("PDF OCR utility", layout, icon=my_icon, button_color="dark green")

event, values = window.read()

while True:
    event, values = window.read()
    source = values['-SOURCE-']
    output = values['-OUTPUT_Folder-']
    preservation = values['-PRESERVATION_Folder-']
    presentation = values['-PRESENTATION_Folder-']
    if values["-OCR-"] is True:
        pdfOCR = "y"
    if values["-NOCR-"] is True:
        pdfOCR = "n"
    if values["-AUTO-"] is True:
        pdfOCR = "auto"
    if event == "Execute":
        window['-OUTPUT-'].update("\nGathering data for folders to be handled", append=True)
        set_list = set()
        for dirpath, dirnames, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith("jpg"):
                    if presentation in dirpath:
                        set_list.add(dirpath)
        window['-OUTPUT-'].update("\ndirectory list generated", append=True)
        set_list = list(set_list)
        set_list.sort()
        master = len(set_list)
        counter1 = 0
        for item in set_list:
            files = [q for q in os.listdir(item) if os.path.isfile(f"{item}/{q}")]
            for file in files:
                if not file.endswith("jpg"):
                    files.remove(file)
            files.sort()
            pdf_master = len(files)
            pdf_counter = 0
            greatest = ""
            smallest = ""
            for file in files:
                if "-" in file:
                    numberology = file.split(".")[0].split("-")[-1]
                    numberology = int(numberology)
                if "-" not in file:
                    numberology = file.split(".")[0].split("_")[-1]
                    numberology = int(numberology)
                if greatest == "":
                    greatest = numberology
                    smallest = numberology
                if greatest < numberology:
                    greatest = numberology
                if smallest > numberology:
                    smallest = numberology
            my_pdf = item.split("\\")[-2]
            my_pdf = f"{my_pdf}.pdf"
            my_pdf = os.path.join(item, my_pdf)
            my_pdf = my_pdf.replace(presentation, output)
            my_metadata = f"{my_pdf[:-4]}.metadata"
            create_directory(my_pdf)
            if not os.path.isfile(my_pdf):
                merger = PyPDF2.PdfMerger()
                for file in files:
                    filename = f"{item}/{file}"
                    current = time.asctime()
                    window['-OUTPUT-'].update(f"\nworking {file}", append=True)
                    if pdfOCR == "y":
                        pdf = pytesseract.image_to_pdf_or_hocr(filename, extension="pdf")
                        pdf_file_in_memory = io.BytesIO(pdf)
                        merger.append(pdf_file_in_memory)
                        extra = ", OCR attempted using automated means and has not been checked for accuracy"
                    if pdfOCR == "n":
                        filenamer = [filename]
                        with open("temp.pdf", 'wb') as f:
                            f.write(img2pdf.convert(filenamer))
                        f.close()
                        merger.append(fileobj=open('temp.pdf', 'rb'))
                        extra = ""
                    if pdfOCR == 'auto':
                        if "ocr" in item:
                            pdf = pytesseract.image_to_pdf_or_hocr(filename, extension="pdf")
                            pdf_file_in_memory = io.BytesIO(pdf)
                            merger.append(pdf_file_in_memory)
                            extra = ", OCR attempted using automated means and has not been checked for accuracy"
                        if "ocr" not in item:
                            filenamer = [filename]
                            with open("temp.pdf", 'wb') as f:
                                f.write(img2pdf.convert(filenamer))
                            f.close()
                            merger.append(fileobj=open('temp.pdf', 'rb'))
                            extra = ""
                    pdf_counter += 1
                    window['-PDF_Progress-'].update_bar(pdf_counter, pdf_master)
                merger.write(my_pdf)
                merger.close()
            if not os.path.isfile(my_metadata):
                source = f"{item}/{files[0]}.metadata"
                source = source.replace(presentation, preservation).replace("jpg", "j2k")
                dom = ET.parse(source)
                root = dom.getroot()
                old_title = root.find(".//dcterms:title", namespaces=namespaces).text
                old_number = old_title.split("microfilm image ")[-1]
                greatest = str(greatest)
                smallest = str(smallest)
                with open(source, "r") as r:
                    filedata = r.read()
                    filedata = filedata.replace(f"mage {old_number}", f"mages {smallest}-{greatest}")
                    filedata = filedata.replace("</dcterms:dcterms>", f"<tslac:note>Volume compiled into aggregated PDF for researcher convenience{extra}.</tslac:note></dcterms:dcterms>")
                    with open(my_metadata, "w") as w:
                        w.write(filedata)
                    w.close()
            window['-OUTPUT-'].update(f"\n{item.split('/')[-1]} has been handled", append=True)
            counter1 += 1
            window['-Progress-'].update_bar(counter1, master)
            pdf_counter = 0
        window['-OUTPUT-'].update(f"\nAll done!", append=True)
    if event == "Close" or event == SG.WIN_CLOSED:
        break