from opexCreator import opexCreator
import getpass
username = input("username: ")
prefix = input("prefix: ")
tenancy = input("tenancy: ")
password = getpass.getpass("Enter password: ")
valuables = {'username': username,
             'password': password,
             'tenant': tenancy,
             'prefix': prefix,
             'access_directory': '/media/sf_G_DRIVE/working_electronicRecords/research_3a.001b/opex/video/presentation',
             'preservation_directory': '/media/sf_G_DRIVE/working_electronicRecords/research_3a.001b/opex/video/preservation',
             'asset_title': 'captionTest',
             'asset_tag': 'open',
             'parent_uuid': 'cf771ef6-ccc0-4102-9576-5713decdc35e',
             'export_directory': '/media/sf_G_DRIVE/working_electronicRecords/research_3a.001b/opex/test',
             'asset_description': 'captionTest',
             'ignore': [".metadata", ".db"],
             'special_format': 'film'}

opexCreator.multi_upload_withXIP(valuables)