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
