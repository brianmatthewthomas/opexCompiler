import datetime
import hashlib
import os
import shutil
import sys
import threading
import time
import uuid
from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

import boto3
import requests
from boto3.s3.transfer import TransferConfig
from botocore.config import Config

import opexCreator.opexCreator

GB = 1024 ** 3
transfer_config = TransferConfig(multipart_threshold=1 * GB)


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write("\r%s %s / %s (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage))
            sys.stdout.flush()


def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparse = minidom.parseString(rough_string)
    return reparse.toprettyxml(indent="    ")


def new_token(username, password, tenant, prefix):
    switch = 0
    success = False
    while switch != 3:
        paydirt = {'username': username, 'password': password, 'tenant': tenant}
        resp = requests.post(f'https://{prefix}.preservica.com/api/accesstoken/login', data=paydirt).json()
        print(resp)
        if resp['success'] is False:
            print(f"new_token failed with error code: {resp['status']}")
            print("retrying...")
            success = False
            switch += 1
        if resp['success'] is True:
            return resp['token']
    if success is False:
        print("max retries reached, stopping program. Wait a bit and try again")
        print(resp.request.url)
        print(resp)
        raise SystemExit


# using a dictionary to pass data to the multipart upload script for simplicity of coding, can also include as
# individual variables
def multi_upload_withXIP(valuables):
    print("to pause process press 'ctrl+c'. If pausing during zip creation process may inadvertently abort")
    finito = 0
    while finito == 0:
        export_dir = valuables['export_directory']
        try:
            to_delete = []
            print(f'starting multi-part upload process at {time.asctime()}')
            # unpack the dictionary to individual variables
            access1_directory = valuables['access1_directory']
            access2_directory = valuables['access2_directory']
            preservation_directory = valuables['preservation_directory']
            asset_title = valuables['asset_title']
            parent_uuid = valuables['parent_uuid']
            asset_tag = valuables['asset_tag']
            # set description, fallback to title if missing from dictionary
            if valuables['asset_description']:
                if valuables['asset_description'] is not None and valuables['asset_description'] != "":
                    asset_description = valuables['asset_description']
                else:
                    asset_description = valuables['asset_title']
            else:
                asset_description = valuables['asset_title']
            # initiate creating xml file
            xip = Element('XIP')
            xip.set('xmlns', 'http://preservica.com/XIP/v6.4')
            io = SubElement(xip, 'InformationObject')
            ref = SubElement(io, 'Ref')
            ref.text = str(uuid.uuid4())
            valuables['asset_id'] = ref.text
            asset_id = valuables['asset_id']
            title = SubElement(io, 'Title')
            title.text = asset_title
            description = SubElement(io, 'Description')
            description.text = asset_description
            security = SubElement(io, 'SecurityTag')
            security.text = asset_tag
            custom_type = SubElement(io, 'CustomType')
            custom_type.text = ""
            parent = SubElement(io, 'Parent')
            parent.text = parent_uuid
            # copy the files to the export area for processing
            access1_representation = os.path.join(export_dir, asset_title, "Representation_Access_1")
            access2_representation = os.path.join(export_dir, asset_title, "Representation_Access_2")
            preservation_representation = os.path.join(export_dir, asset_title, "Representation_Preservation")
            for dirpath, dirnames, filenames in os.walk(access1_directory):
                for filename in filenames:
                    if not filename.endswith(tuple(valuables['ignore'])):
                        filename1 = os.path.join(dirpath, filename)
                        checksum1 = create_sha256(filename1)
                        if filename.split(".")[-1] == "srt":
                            filename2 = os.path.join(access1_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                            filename2 = os.path.join(access1_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                            filename2 = os.path.join(access1_representation, "Spanish", filename)
                        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                            filename2 = os.path.join(access1_representation, "Movie", filename)
                        else:
                            filename2 = os.path.join(access1_representation, filename.split(".")[0], filename)
                        if not os.path.exists(os.path.dirname(filename2)):
                            os.makedirs(os.path.dirname(filename2), exist_ok=True)
                        shutil.copyfile(filename1, filename2)
                        to_delete.append(filename2)
                        checksum2 = create_sha256(filename2)
                        if checksum1 == checksum2:
                            print("copy of", filename, "verified, continuing")
                        else:
                            print("error in copying of", filename, "... exiting, try again")
                            sys.exit()
            for dirpath, dirnames, filenames in os.walk(access2_directory):
                for filename in filenames:
                    if not filename.endswith(tuple(valuables['ignore'])):
                        filename1 = os.path.join(dirpath, filename)
                        checksum1 = create_sha256(filename1)
                        if filename.split(".")[-1] == "srt":
                            filename2 = os.path.join(access2_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                            filename2 = os.path.join(access2_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                            filename2 = os.path.join(access2_representation, "Spanish", filename)
                        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                            filename2 = os.path.join(access2_representation, "Movie", filename)
                        else:
                            filename2 = os.path.join(access2_representation, filename.split(".")[0], filename)
                        if not os.path.exists(os.path.dirname(filename2)):
                            os.makedirs(os.path.dirname(filename2), exist_ok=True)
                        shutil.copyfile(filename1, filename2)
                        to_delete.append(filename2)
                        checksum2 = create_sha256(filename2)
                        if checksum1 == checksum2:
                            print("copy of", filename, "verified, continuing")
                        else:
                            print("error in copying of", filename, "... exiting, try again")
                            sys.exit()
            for dirpath, dirnames, filenames in os.walk(preservation_directory):
                for filename in filenames:
                    if not filename.endswith(tuple(valuables['ignore'])):
                        filename1 = os.path.join(dirpath, filename)
                        checksum1 = create_sha256(filename1)
                        if filename.split(".")[-1] == "srt":
                            filename2 = os.path.join(preservation_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                            filename2 = os.path.join(preservation_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                            filename2 = os.path.join(preservation_representation, "Spanish", filename)
                        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                            filename2 = os.path.join(preservation_representation, "Movie", filename)
                        else:
                            filename2 = os.path.join(preservation_representation, filename.split(".")[0], filename)
                        if not os.path.exists(os.path.dirname(filename2)):
                            os.makedirs(os.path.dirname(filename2), exist_ok=True)
                        shutil.copyfile(filename1, filename2)
                        to_delete.append(filename2)
                        checksum2 = create_sha256(filename2)
                        if checksum1 == checksum2:
                            print("copy of", filename, "verified, continuing")
                        else:
                            print("error in copying of", filename, "... exiting, try again")
                            sys.exit()
            # start creating the representations, content objects and bitstreams
            print(f"starting to compile pax metadata as of {time.asctime()}")
            access1_refs_dict = {}
            if access1_representation:
                access1_refs_dict = make_representation(xip, "Access1", "Access", access1_directory,
                                                        asset_id, valuables)
            access2_refs_dict = {}
            if access2_representation:
                access2_refs_dict = make_representation(xip, "Access2", "Access", access2_directory,
                                                        asset_id, valuables)
            preservation_refs_dict = {}
            if preservation_representation:
                preservation_refs_dict = make_representation(xip, "Preservation", "Preservation",
                                                             preservation_directory, asset_id, valuables)
            print(f"representations created as of {time.asctime()}")
            if access1_refs_dict:
                make_content_objects(xip, access1_refs_dict, asset_id, asset_tag, "", "")
            if access2_refs_dict:
                make_content_objects(xip, access2_refs_dict, asset_id, asset_tag, "", "")
            if preservation_refs_dict:
                make_content_objects(xip, preservation_refs_dict, asset_id, asset_tag, "", "")
            print(f"content objects created as of {time.asctime()}")
            if access1_refs_dict:
                make_generation(xip, access1_refs_dict, "Access_1")
            if access2_refs_dict:
                make_generation(xip, access2_refs_dict, "Access_2")
            if preservation_refs_dict:
                make_generation(xip, preservation_refs_dict, "Preservation")
            print(f"generations created as of {time.asctime()}")
            if access1_refs_dict:
                make_bitstream(xip, access1_refs_dict, access1_directory, "Access_1", access1_representation)
            if access2_refs_dict:
                make_bitstream(xip, access2_refs_dict, access2_directory, "Access_2", access2_representation)
            if preservation_representation:
                make_bitstream(xip, preservation_refs_dict, preservation_directory, "Preservation1",
                               preservation_representation)
            print(f"bitstreams created as of {time.asctime()}")
            pax_folder = export_dir + "/" + asset_title
            # currently unable to get xip to work with preservica ingest, uncomment the 4 lines below
            # if/when it starts working
            pax_file = pax_folder + "/" + asset_title + ".xip"
            metadata = open(pax_file, "wt", encoding='utf-8')
            metadata.write(prettify(xip))
            metadata.close()
            tempy = export_dir + "/temp"
            os.makedirs(tempy, exist_ok=True)
            archive_name = export_dir + "/" + asset_title + ".pax"
            print(f'making preliminary pax file as of {time.asctime()}')
            shutil.make_archive(archive_name, "zip", pax_folder)
            archive_name = archive_name + ".zip"
            archive_name2 = archive_name.replace(export_dir, tempy)
            shutil.move(archive_name, archive_name2)
            print(f"making opex file as of {time.asctime()}")
            make_opex(valuables, archive_name2)
            compiled_opex = export_dir + "/" + asset_id
            print(f'making opex archive as of {time.asctime()}')
            shutil.make_archive(compiled_opex, "zip", tempy)
            compiled_opex = compiled_opex + ".zip"
            valuables['compiled_opex'] = compiled_opex
            print("uploading", asset_title)
            uploader(valuables)
            to_delete.append(compiled_opex)
            to_delete.append(archive_name2)
            to_delete.append(archive_name2 + ".opex")
            # cleanup
            for item in to_delete:
                os.remove(item)
            try:
                os.rmdir(export_dir + "/" + asset_title)
                os.rmdir(tempy)
            except:
                print("\n", "unable to remove staging folder for", asset_title)
            finito = 1
        except KeyboardInterrupt:
            print("process paused, cleaning up current round")
            time.sleep(10)
            for dirpath, dirnames, filenames in os.walk(export_dir):
                for filename in filenames:
                    filename = os.path.join(dirpath, filename)
                    os.remove(filename)
            resume = input("type 'resume' to resume process: ")
            if resume == "resume":
                continue
            else:
                print("you chose to exit")
                sys.exit()


def multi_upload(valuables):
    # a trimmed down version of the version with XIP, because we honestly don't need the fluff
    print("to pause process press ctrl+c. If pausing during zip creation process may abort")
    finito = 0
    while finito == 0:
        export_dir = valuables['export_directory']
        try:
            to_delete = []
            current = time.asctime()
            print(f'starting multi-part upload at {current}')
            # unpack the dictionary to individual variables
            access1_directory = valuables['access1_directory']
            access2_directory = valuables['access2_directory']
            preservation_directory = valuables['preservation_directory']
            asset_title = valuables['asset_title']
            valuables['asset_id'] = str(uuid.uuid4())
            asset_id = valuables['asset_id']
            # copy the files to the export area for processing
            access1_representation = os.path.join(export_dir, asset_title, "Representation_Access_1")
            access2_representation = os.path.join(export_dir, asset_title, "Representation_Access_2")
            preservation_representation = os.path.join(export_dir, asset_title, "Representation_Preservation")
            for dirpath, dirnames, filenames in os.walk(access1_directory):
                for filename in filenames:
                    if not filename.endswith(tuple(valuables['ignore'])):
                        filename1 = os.path.join(dirpath, filename)
                        checksum1 = create_sha256(filename1)
                        if filename.split(".")[-1] == "srt":
                            filename2 = os.path.join(access1_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                            filename2 = os.path.join(access1_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                            filename2 = os.path.join(access1_representation, "Spanish", filename)
                        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                            filename2 = os.path.join(access1_representation, "Movie", filename)
                        else:
                            filename2 = os.path.join(access1_representation, filename.split(".")[0], filename)
                        if not os.path.exists(os.path.dirname(filename2)):
                            os.makedirs(os.path.dirname(filename2), exist_ok=True)
                        shutil.copyfile(filename1, filename2)
                        to_delete.append(filename2)
                        checksum2 = create_sha256(filename2)
                        if checksum1 == checksum2:
                            print("copy of", filename, "verified, continuing")
                        else:
                            print("error in copying of", filename, "... exiting, try again")
                            sys.exit()
            for dirpath, dirnames, filenames in os.walk(access2_directory):
                for filename in filenames:
                    if not filename.endswith(tuple(valuables['ignore'])):
                        filename1 = os.path.join(dirpath, filename)
                        checksum1 = create_sha256(filename1)
                        if filename.split(".")[-1] == "srt":
                            filename2 = os.path.join(access2_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                            filename2 = os.path.join(access2_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                            filename2 = os.path.join(access2_representation, "Spanish", filename)
                        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                            filename2 = os.path.join(access2_representation, "Movie", filename)
                        else:
                            filename2 = os.path.join(access2_representation, filename.split(".")[0], filename)
                        if not os.path.exists(os.path.dirname(filename2)):
                            os.makedirs(os.path.dirname(filename2), exist_ok=True)
                        shutil.copyfile(filename1, filename2)
                        to_delete.append(filename2)
                        checksum2 = create_sha256(filename2)
                        if checksum1 == checksum2:
                            print("copy of", filename, "verified, continuing")
                        else:
                            print("error in copying of", filename, "... exiting, try again")
                            sys.exit()
            for dirpath, dirnames, filenames in os.walk(preservation_directory):
                for filename in filenames:
                    if not filename.endswith(tuple(valuables['ignore'])):
                        filename1 = os.path.join(dirpath, filename)
                        checksum1 = create_sha256(filename1)
                        if filename.split(".")[-1] == "srt":
                            filename2 = os.path.join(preservation_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                            filename2 = os.path.join(preservation_representation, "English", filename)
                        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                            filename2 = os.path.join(preservation_representation, "Spanish", filename)
                        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                            filename2 = os.path.join(preservation_representation, "Movie", filename)
                        else:
                            filename2 = os.path.join(preservation_representation, filename.split(".")[0], filename)
                        if not os.path.exists(os.path.dirname(filename2)):
                            os.makedirs(os.path.dirname(filename2), exist_ok=True)
                        shutil.copyfile(filename1, filename2)
                        to_delete.append(filename2)
                        checksum2 = create_sha256(filename2)
                        if checksum1 == checksum2:
                            print("copy of", filename, "verified, continuing")
                        else:
                            print("error in copying of", filename, "... exiting, try again")
                            sys.exit()
            pax_folder = export_dir + "/" + asset_title
            tempy = export_dir + "/temp"
            os.makedirs(tempy, exist_ok=True)
            archive_name = export_dir + "/" + asset_title + ".pax"
            print(f'making preliminary pax file as of {time.asctime()}')
            shutil.make_archive(archive_name, "zip", pax_folder)
            archive_name = archive_name + ".zip"
            archive_name2 = archive_name.replace(export_dir, tempy)
            shutil.move(archive_name, archive_name2)
            make_opex(valuables, archive_name2)
            compiled_opex = export_dir + "/" + asset_id
            print(f'making opex file as of {time.asctime()}')
            shutil.make_archive(compiled_opex, "zip", tempy)
            compiled_opex = compiled_opex + ".zip"
            valuables['compiled_opex'] = compiled_opex
            print("uploading", asset_title)
            uploader(valuables)
            to_delete.append(compiled_opex)
            to_delete.append(archive_name2)
            to_delete.append(archive_name2 + ".opex")
            # cleanup
            for item in to_delete:
                os.remove(item)
            try:
                os.rmdir(export_dir + "/" + asset_title)
                os.rmdir(tempy)
            except:
                print("\n", "unable to remove staging folder for", asset_title)
            finito = 1
        except KeyboardInterrupt:
            print("process paused, cleaning up current round")
            time.sleep(10)
            for dirpath, dirnames, filenames in os.walk(export_dir):
                for filename in filenames:
                    filename = os.path.join(dirpath, filename)
                    os.remove(filename)
            '''for item in toDelete:
                os.remove(item)'''
            resume = input("type 'resume' to resume processes:")
            if resume == "resume":
                continue
            else:
                print("you chose to exit")
                sys.exit()


def make_opex(valuables, filename2):
    opex = Element('opex:OPEXMetadata', {'xmlns:opex': 'http://www.openpreservationexchange.org/opex/v1.0'})
    opex_transfer = SubElement(opex, "opex:Transfer")
    opex_source = SubElement(opex_transfer, "opex:SourceID")
    opex_source.text = valuables["asset_id"]
    opex_fixities = SubElement(opex_transfer, "opex:Fixities")
    opex_sha256 = create_sha256(filename2)
    opex_fixity = SubElement(opex_fixities, "opex:Fixity")
    opex_fixity.attrib = {'type': 'SHA-256', 'value': opex_sha256}
    opex_properties = SubElement(opex, 'opex:Properties')
    opex_title = SubElement(opex_properties, 'opex:Title')
    opex_title.text = valuables['asset_title']
    opex_description = SubElement(opex_properties, 'opex:Description')
    if valuables['asset_description'] not in valuables.keys():
        valuables['asset_description'] = valuables['asset_title']
    opex_description.text = valuables['asset_description']
    opex_security = SubElement(opex_properties, 'opex:SecurityDescriptor')
    opex_security.text = valuables['asset_tag']
    if 'metadata_file' in valuables.keys():
        opex_metadata = SubElement(opex, 'opex:DescriptiveMetadata')
        opex_metadata.text = "This is where the metadata goes"
    export_file = valuables['export_directory'] + "/temp/" + valuables['asset_title'] + ".pax.zip.opex"
    opex_output = open(export_file, "w", encoding='utf-8')
    opex_output.write(prettify(opex))
    opex_output.close()
    if 'metadata_file' in valuables.keys():
        with open(valuables['metadata_file'], 'r') as f:
            filedata = f.read()
            filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
            filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "")
            with open(export_file, "r") as r:
                fileinfo = r.read()
                fileinfo = fileinfo.replace("This is where the metadata goes", filedata)
                with open(export_file, "w") as w:
                    w.write(fileinfo)
                    w.close()


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


def uploader(valuables):
    filelist = ["/media/sf_transfer_agent/nothing.txt"]
    logger = open("./transfer_agent_list.txt", "a")
    logger.close()
    if valuables['quiet_time'] is True:
        opexCreator.opexCreator.quiet_time(quiet_start=valuables['quiet_start'], quiet_end=valuables['quiet_end'],
                                           interval=valuables['interval'])
    with open("./transfer_agent_list.txt", "r") as r:
        for line in r:
            line = line[:-1]
            filelist.append(line)
    token = new_token(valuables['username'], valuables['password'], valuables['tenant'], valuables['prefix'])
    print(token)
    user_tenant = valuables['tenant']
    user_domain = valuables['prefix']
    bucket = f'{user_tenant.lower()}.package.upload'
    endpoint = f'https://{user_domain}.preservica.com/api/s3/buckets'
    print(f'Uploading to Preservica: using s3 bucket {bucket} at {time.asctime()}')
    client = boto3.client('s3', endpoint_url=endpoint, aws_access_key_id=token, aws_secret_access_key="NOT USED",
                          config=Config(s3={'addressing_style': 'path'}))
    sip_name = valuables['compiled_opex']
    metadata = {'Metadata': {'structuralObjectreference': valuables['parent_uuid']}}
    switch = 0
    copy = True
    while switch != 3:
        try:
            response = client.upload_file(sip_name, bucket, valuables['asset_id'] + ".zip", ExtraArgs=metadata,
                                          Callback=ProgressPercentage(sip_name), Config=transfer_config)
            switch = 3
            current = time.asctime()
            print("\n", f"upload successful at {current}")
            copy = False
        except:
            current = time.asctime()
            print(f"upload failure, trying again at {current}")
            switch += 1
            copy = True
    if copy is True:
        current = time.asctime()
        new_file = sip_name.split("/")[-1]
        new_file = "/media/sf_transfer_agent/" + new_file
        print(f"API uploads failed, copying to transfer agent at {current}")
        print("checking transfer agent for any lingering files first")
        for item in filelist:
            while isfile(item):
                current = time.asctime()
                print(f"waiting on {item} to finish as of {current}", end="\r")
                time.sleep(30)
            print(f"{item} has already cleared transfer agent")
        shutil.copyfile(sip_name, new_file + ".fail")
        os.rename(new_file + ".fail", new_file)
        current = time.asctime()
        print(f"package copied to transfer agent as of {current}, moving on")
        with open("./transfer_agent_list.txt", "a") as w:
            w.write(new_file + "\n")
        w.close()


def make_representation(xip, rep_name, rep_type, path, io_ref, valuables):
    representation = SubElement(xip, 'Representation')
    io_link = SubElement(representation, "InformationObject")
    io_link.text = io_ref
    access_name = SubElement(representation, 'Name')
    access_name.text = rep_name
    access_type = SubElement(representation, 'Type')
    access_type.text = rep_type
    content_objects = SubElement(representation, 'ContentObjects')
    rep_files = [f for f in listdir(path) if isfile(join(path, f))]
    refs_dict = {}
    counter = 0
    for f in rep_files:
        if not f.endswith(tuple(valuables['ignore'])):
            content_object = SubElement(content_objects, 'ContentObject')
            content_object_ref = str(uuid.uuid4())
            content_object.text = content_object_ref
            refs_dict[f] = content_object_ref
            counter += 1
    # repFormat = SubElement(representation, "RepresentationFormats")
    # if valuables['special_format'] == "film":
    #     repFormat1 = SubElement(repFormat, "RepresentationFormat")
    #     repFormat1_uuid = SubElement(repFormat1, "PUID")
    #     repFormat1_uuid.text = "repfmt/7"
    #     repFormat1_FormatName = SubElement(repFormat1, "FormatName")
    #     repFormat1_FormatName.text = "Captioned Video"
    #     repFormat1_priority = SubElement(repFormat1, "Priority")
    #     repFormat1_priority.text = "1"
    #     repFormat1_valid = SubElement(repFormat1, "Valid")
    #     repFormat1_valid.text = "true"
    # if "Preservation" in rep_name and valuables['special_format'] == 'multi-page document':
    #     repProperties = SubElement(representation, "RepresentationProperties")
    #     repProperty1 = SubElement(repProperties, "RepresentationProperty")
    #     repPUID = SubElement(repProperty1, "PUID")
    #     repPUID.text = "prp/17"
    #     repPropName = SubElement(repProperty1, "PropertyName")
    #     repPropName.text = "Number of Pages"
    #     repValue = SubElement(repProperty1, "Value")
    #     repValue.text = str(counter)
    #     repFormat1 = SubElement(repFormat, "RepresentationFormat")
    #     repFormat1_uuid = SubElement(repFormat1, "PUID")
    #     repFormat1_uuid.text = "repfmt/6"
    #     repFormat1_FormatName = SubElement(repFormat1, "FormatName")
    #     repFormat1_FormatName.text = "Renderable Multi Image"
    #     repFormat2 = SubElement(repFormat, "RepresentationFormat")
    #     repFormat2_uuid = SubElement(repFormat2, "PUID")
    #     repFormat2_uuid.text = "repfmt/5"
    #     repFormat2_FormatName = SubElement(repFormat2, "FormatName")
    #     repFormat2_FormatName.text = "Renderable Multi Image"
    #     repFormat2_priority = SubElement(repFormat2, "Priority")
    #     repFormat2_priority.text = "2"
    #     repFormat2_valid = SubElement(repFormat2, "Valid")
    #     repFormat2_valid.text = "false"
    return refs_dict


def make_content_objects(xip, refs_dict, io_ref, tag, content_description, content_type):
    for filename, ref in refs_dict.items():
        content_object = SubElement(xip, 'ContentObject')
        ref_element = SubElement(content_object, 'Ref')
        ref_element.text = ref
        title = SubElement(content_object, 'Title')
        if filename.split(".")[-1] == "srt":
            title.text = "English"
        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
            title.text = "English"
        elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
            title.text = "Spanish"
        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
            title.text = "Movie"
        else:
            title.text = os.path.splitext(filename)[0]
        description = SubElement(content_object, "Description")
        description.text = content_description
        security_tag = SubElement(content_object, "SecurityTag")
        security_tag.text = tag
        custom_type = SubElement(content_object, "CustomType")
        custom_type.text = content_type
        parent = SubElement(content_object, "Parent")
        parent.text = io_ref


def make_generation(xip, refs_dict, generation_label):
    for filename, ref in refs_dict.items():
        generation = SubElement(xip, 'Generation', {"original": "true", "active": "true"})
        content_object = SubElement(generation, "ContentObject")
        content_object.text = ref
        label = SubElement(generation, "Label")
        if generation_label:
            label.text = generation_label
        else:
            label.text = os.path.splitext(filename)[1]
        effective_date = SubElement(generation, "EffectiveDate")
        effective_date.text = datetime.datetime.now().isoformat()[:-7] + "Z"
        bitstreams = SubElement(generation, "Bitstreams")
        bitstream = SubElement(bitstreams, "Bitstream")
        if "Preservation" in generation_label:
            if filename.split(".")[-1] == "srt":
                bitstream.text = "Representation_" + generation_label + "/English/" + filename
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                bitstream.text = "Representation_" + generation_label + "/English/" + filename
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                bitstream.text = "Representation_" + generation_label + "/Spanish/" + filename
            elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                bitstream.text = "Representation_" + generation_label + "/Movie/" + filename
            else:
                bitstream.text = "Representation_" + generation_label + "/" + filename.split(".")[0] + "/" + filename
        else:
            if filename.split(".")[-1] == "srt":
                bitstream.text = "Representation_" + generation_label + "/English/" + filename
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                bitstream.text = "Representation_" + generation_label + "/English/" + filename
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                bitstream.text = "Representation_" + generation_label + "/Spanish/" + filename
            elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                bitstream.text = "Representation_" + generation_label + "/Movie/" + filename
            else:
                bitstream.text = "Representation_" + generation_label + "/" + filename.split(".")[0] + "/" + filename
        SubElement(generation, "Formats")
        SubElement(generation, "Properties")


def make_bitstream(xip, refs_dict, root_path, generation_label, representation_location):
    for filename, ref in refs_dict.items():
        bitstream = SubElement(xip, "Bitstream")
        filename_element = SubElement(bitstream, "Filename")
        filename_element.text = filename
        file_size = SubElement(bitstream, "FileSize")
        full_path = os.path.join(root_path, filename)
        file_stats = os.stat(full_path)
        file_size.text = str(file_stats.st_size)
        physloc = SubElement(bitstream, "PhysicalLocation")
        if "Preservation" in generation_label:
            if filename.split(".")[-1] == "srt":
                physloc.text = "Representation_" + generation_label[:-1] + "/English"
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                physloc.text = "Representation_" + generation_label[:-1] + "/English"
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                physloc.text = "Representation_" + generation_label[:-1] + "/Spanish"
            elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                physloc.text = "Representation_" + generation_label[:-1] + "/Movie"
            else:
                physloc.text = "Representation_" + generation_label[:-1] + "/" + filename.split(".")[0]
        else:
            if filename.split(".")[-1] == "srt":
                physloc.text = "Representation_" + generation_label + "/English"
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "en":
                physloc.text = "Representation_" + generation_label + "/English"
            elif filename.split(".")[-1] == "vtt" and filename.split(".")[-2] == "es":
                physloc.text = "Representation_" + generation_label + "/Spanish"
            elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                physloc.text = "Representation_" + generation_label + "/Movie"
            else:
                physloc.text = "Representation_" + generation_label + "/" + filename.split(".")[0]
        fixities = SubElement(bitstream, "Fixities")
        fixity = SubElement(fixities, "Fixity")
        fixity_algorithm_ref = SubElement(fixity, "FixityAlgorithmRef")
        fixity_algorithm_ref.text = "SHA256"
        fixity_value = SubElement(fixity, "FixityValue")
        fixity_value.text = create_sha256(full_path)
