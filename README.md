<h1>OPEX Package Creator</h1>
This iteratively updated graphical tool compiles OPEX packages using a graphical interface so it is easier to find errors and fix them when you are about to run it. It is meant to be compiled as an executable in windows (use Wine to compile via a Linux box), it may work without that on Windows by initiating at the command line but it will likely work faster standalong. The following variables apply when trying to run program:
<ul>
    <li>Validate xml: used to run across all XML and verify it parses</li>
    <li>Type of packages: Radio buttons to choose the type of package involved</li>
    <li>Push to Update: The interface is written with pysimplegui, which doesn't automatically update the interface when you do something. Push to update lets you refresh the screen</li>
    <li>Use config file: checkbox to load variables from a config file</li>
    <li>Generate config file template: use to generate a blank config file is you need one</li>
    <li>Browse to config file: file picker for the config file, picking a non-config file is possible but when trying to load it will crash the program</li>
    <li>Load: reads selected config file. You <strong>MUST</strong> load a config file, it is not enough to browse to it</li>
    <li>Item-level security tag: this new option gets around auto-preservation messing up multi-part packages. My use-case centers on that so digitized is the default. The other option is "open", you'll need ot change the underlying code if you want other options</li>
    <li>Incremental clean-up: this tool creates a second copy of stuff for packaging and is set to delete the temporary files after everything is packaged. If you are concerned about space, incremental clean-up will delete files as packages get completed. Not this makes time in process incredibly longer.</li>
    <li>Object type: This is for compound objects in case special handling is needed. Object type will be listed in the item description.</li>
    <li>The bottom part: this is where the various data variables go. Each field is unique so filling something in for 2-versions-flat and switching to 2-versions-atomic will mean you have to enter data again</li>
</ul>

<h1>OPEX Package Creator for Linux</h1>
This variant of the opex package creator was spun off by changing one line of code (ironically it is all developed in a Linux environment) so that it works on Linux, for the purposed of getting around character limits in directory paths. It must be initiated at the command line and then a graphical interface will pop up. No idea why but it won't compile into a Linux executable correctly.
<h1>OPEX compiler</h1>

This is a set of scripts and accompanying module to compile an OPEX file that can be ingested into Preservica.

The code is partially adapted based on a script made available by James Carr of Preservica in 2020 to help users cope with the Preservica v6.0 data model being released and its negative affects on the ability to ingest multipart items.

You will need the following to use this tool:

`tenancy name`, `preservica domain name`, `username`, `password`

User will also need to know: 
<ul>
<li>the UUID of the parent directory they want to ingest into,</li>
<li>the security tag they wish to use</li>
<li>how many manifestations are involved</li>
</ul>

Bear in mind that I am not a trained programmer so this might not be the most efficient way of doing things, and this is tailored to my use case not yours. If you have a problem you can let me know because it is probably a problem for me too. If you use this for your repository, you will owe me a cup of coffee or a beer at least once if we ever cross paths at a conference event.
<h2>Intended usage</h2>
This operates off of a dictionary that should contain everything you need to get the job done. The dictionary gets passed from one function to the next as-needed until the process is finished.

There are 2 variations:
`multi_upload` creates an opex without the fuss of the 

    import opexCreator
    
    valuables = {'username': '[username/email goes here]',
                 'password': '[password goes here]',
                 'tenent': '[your tenancy, most likely the same as your UA address]',
                 'prefix': '[that part that references your server]',
                 'access_directory': '[absolute or relative path to your access files]',
                 'preservation_directory': '[absolute or relative path to your preservation files]',
                 'asset_title': '[title of the thing]',
                 'asset_tag': '[security tag]',
                 'parent_uuid': '[UUID for parent folder]',
                 'export_directory': '[absolute or relative path to export to, is a working directory]',
                 'asset_description': '[description of stuff]',
                 'metadata_file': '[the metadata full filename]',
                 'ignore': [file extension to ignore as comma list like a csv],
                 'special_format': '[choose between film and multi-page document]'}
    opexCreator.multi_upload(valuables)

<h2>footnotes</h2>
The security tag for the xip/opex must match the default security tag for the system. A mismatch will cause a failure of the ingest and probably some tears.

If you use a different security tag for different types of files, such as `Digitized` for digitized material you will need to use graphical tools to change the security tag and update storage if that is appropriate.

`basicExample.py` is a straight example invocation of the process.
`complexExample.py` is a complicated example of how you can leverage this tool to create an iterator that will crawl a directory to create assets as appropriate. The basic assumption of this script/program is that you put all the files for one manifestation of the object in a single folder and that if you have metadata files you use the convention of .metadata for the file.

The opexCreator is set to dump a failed api upload to a transfer agent for other upload. For this to work you need to designate the folder in the `opexCreator.py` around line 353 and the `opexCreator_3versions.py` around line 411. It is default set to "/media/sf_transfer_agent" because that is how the author designated the link to the location of the transfer agent in his virtual machine.

# pdfCompiler_gui
The PDF Compiler GUI addresses a problem of needing to compiled large sets of files into PDF files, and in some cases to add OCR to the output. It is meant is written for both linux and windows, with the intent to run on Windows after the executable is compiled. To get OCR functionality it is necessary to get a copy of the latest version of tesseract installed on your machine. The below directions for installation are assuming creation of the tool using a linux virtual environment. Without authority to install software on the Windows computer. Presumable, some of these directions can be adapted if you are able to install software on your computer so adapt as needed.

## Steps to Generate the Executable
1. Install wine on your computer
2. Install python in your wine folder. Executable to do that can be found at `python.org`. You should be able to copy the executable download into the wine folder and double-click to run it.
3. Install the necessary dependencies within the pythong environment by using a Terminal command of `wine ./Scripts/pip3.exe install [module name]`
   * It is possible you will need to install pip3 before running step 3.
   * It will be useful to install the dependencies in the order they exist in the compiler script
4. Install Tesseract into the wine folder.
   * Go to `https://github.com/UB-Mannheim/tesseract/wiki` for download
   * Push the downloaded executable to your wine folder
   * Double click and follow the installation tool directions. Make sure to install into the wine folder
5. Compile the executable by running in the terminal: `wine ./Scripts/pytinstaller -wF [path to script/scriptname]`
   * If error messages crop up follow through any steps to remediate the errors until it can run successfully
   * The executable components are staged in the 'build' folder and the exe file if located in the 'dist' folder.
   * If you have to resolve errors it is important to delete the components folder from the 'build' directory otherwise pyinstaller will just assume everything is there and do nothing useful
6. Copy the executable into the Tesseract-OCR folder created by installing tesseract into wine
7. Copy this completed package to where you want. Double-click the output executable from within the Tesseract folder to run.
   * Why run in the Tesseract folder? It is necessary to have tesseract in the system path in windows or immediately accessible to the tool. The best way to do that is to have the executable in the same folder as Tesseract.

## Running the tool
The tool supports OCR, non-OCR and Auto-selection of OCR. These are options based on radio buttons.
Note: When running the Auto option, the tool will select what to OCR based on whether 'ocr' is in the path to the folders to work on. Don't use 'OCR' use 'ocr' or it won't work.

Note as well: This tool operates on a crawler method so you can target a root folder and run it against the whole file set to generate multiple PDFs.

The following variables need to be in place:
1. Source folder: Use the browse button to locate the parent/root folder for everything. It will go down recursively so you can target a parent folder for a massive number of files but be cognizant that it has to compile some data before starting so selecting something with 100,000 files may take a minute to begin.
2. Output Folder name: this is the folder that will be generated in parallel to the structure for the images used to compile the PDF.
3. Preservation Folder name: this is the sibling folder for the Output folder where the preservation files are located. This is where the sidecar metadata used to generate the PDF metadata is sources from.
4. Presentation Folder name: This is the sibling folder for the output folder where the jpgs being compiled into a PDF lives.

Click on Execute to get the process going, it may take two clicks.
### How it works
The tool goes through several steps.
1. Crawl the directory structure based on the source folder designated and compile a list of locations where the presentation Folder name exists.
2. Generate primary status bar data based on the number of items in the list
3. Go through the items in the list and
   * If there is a PDF of the correct name in the output directory, skip to the bottom and move to the next item on the list
   * Create a page range for the items to be compiled into a PDF
   * Get a sorted listing of the files in the directory jpg
   * Get the size of the listing
   * Generate a space in memory for a compiled PDF
   * For each file
     * if OCR is not applicable, save a temp PDF and append that the compiled PDF
     * if OCR is applicable, pass the image through Tesseract with output as binary PDF format and append this to the compiled PDF
     * update the status second status bare to show progress
   * Once all images have been processed, save the compiled PDF to the output sibling folder
   * Gather metadata for the compiled PDF by
     * reading the first metadata file as the baseline
     * updating part of the title to reflect the numeric sequence (pages 1-233 for example) for the compilation
   * advance the master bar to reflect processing is completed

### Assumptions and caveats
This tool was developed to specifically address mass PDF generation and OCR for files received by Ancestry.com that had been organized into volumes as a natural organizational unit. As such a few circumstances apply
1. The directory immediately preceding the preservation/presentation/output folder is the desired name of the PDF to be put into the output folder
2. For each preservation file there is a sidecar metadata file in existence with core metadata about the volume as a whole
3. The page numbers are reflected in the jpg naming convention where the pre-extension filename ends with a `-####` or a `_####`
4. The title row of the metadata ends with `microfilm image [number goes here]`. This is the value replaces by the gathered page range data
   * lines 219ish thru 234ish deal with this issue if you want it changed. future iterations may allow for metadata generation to be optional
5. The script **will** crash if there is no .metadata sidecar file associated with the first item in the Preservation folder
6. Files will be organized as an atomic unit as indicated generally below. The creator uses Preservica and this generally patches their paradigm for handling files. Organization into parallel structures where master and presentation files for multiple volumes are stored into separate root directory structures will cause a crash
```commandline
Some master folder
    *myPDF file1
        *Presentation2
            *File1.jpg
            *file2.jpg
            *file3.jpg
        *Preservation1
            *File1.tif
            *File2.tif
            *File3.tif
    *myPDF file2
        *etc
```