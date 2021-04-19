from opexCreator import opexCreator_3versions
import getpass
username = input("username: ")
prefix = input("prefix: ")
tenancy = input("tenancy: ")
password = getpass.getpass("Enter password: ")
valuables = {'username': username,
             'password': password,
             'tenent': tenancy,
             'prefix': prefix,
             'access1_directory': '/media/sf_G_DRIVE/working_electronicRecords/ancestry/1677/tester/32241_1220701439_2131/presentation2',
             'access2_directory': '/media/sf_G_DRIVE/working_electronicRecords/ancestry/1677/tester/32241_1220701439_2131/presentation3',
             'preservation_directory': '/media/sf_G_DRIVE/working_electronicRecords/ancestry/1677/tester/32241_1220701439_2131/preservation1',
             'asset_title': '3star_test',
             'asset_tag': 'open',
             'parent_uuid': 'cf771ef6-ccc0-4102-9576-5713decdc35e',
             'export_directory': '/media/sf_G_DRIVE/working_electronicRecords/research_3a.001b/opex/export',
             'asset_description': '3star_test',
             'ignore': [".metadata", ".db"],
             'special_format': 'multi-part document'}

opexCreator_3versions.multi_upload_withXIP(valuables)