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
                 'metadata_file': '[the metadata full filename]'}
    opexCreator.multi_upload(valuables)

<h2>footnotes</h2>
Note that as of 2021-01-28 at 4:10pm I could not get the system to work with an attached XIP, so the lines to export the XIP into a sidecar file have been commented out. In exchange I inserted validation between the original file and the copy pushed to a staging area. Functionality added to remove staging and upload files after finished but may not be able to remove created folders. Cleanup after processes may be necessary. 

Assets will ingest with designated security tag but individual files will save as the default security tag. To fix this run the graphical permissions change on the asset/folder then if necessary use the update storage to send component files to the correct place.

An updated footnote will be added if I can get the XIP working.