#OPEX compiler

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
