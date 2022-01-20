import boto3
import sys
import os
import pandas as pd
import csv
import io
import time
import json
import argparse    
from enum import Enum

DEFAULT_DURATION = 20

cli_arguments: object = None

class UploadServices(Enum):
    AWS = 'aws'
    # Aquí se pueden definir tipos de servicio parala subida del archivo

class CLIArguments(argparse.ArgumentParser):
    """
    @version 1.0.0

    Class to register and manage the CLI arguments.
    """
    def __init__(self):
        """Initializes the parser."""
        super().__init__()

    def initialize(self):
        """Method to add all the CLI arguments"""
        self.__add_rstp_arguments()
        self.__add_output_file_arguments()
        self.__add_upload_server_arguments()
        self.__add_transcription_arguments()
        self.arguments = self.parse_args() 

    def __add_rstp_arguments(self):
        """Method to register the RSTP CLI arguments"""
        self.add_argument('-u', '--camera-user', help = 'Camera user', default = 'admin')
        self.add_argument('-i', '--camera-ip', help = 'Camera IP', default = '0.0.0.0')
        self.add_argument('-p', '--camera-password', help = 'Camera password', default = 'admin')

    def __add_output_file_arguments(self):
        """Method to register the CLI output file arguments"""
        self.add_argument('-P', '--path-to-file', help = 'System path to the output file', default = 'C:/') # Si es Linux, cambiar el default a /home
        self.add_argument('-o', '--output', help = 'Output file name (without extension)', default = 'output')
        self.add_argument('-d', '--duration', help = 'Duration of the recording (in seconds).', default = '10')

    def __add_upload_server_arguments(self):
        """Method to register the CLI upload server arguments"""
        self.add_argument('-s', '--service', help = 'Service to use to upload the file', default = UploadServices.AWS.value)
        self.add_argument('-r', '--remote', help = 'URI of the remote files repository', default = '/')

    def __add_transcription_arguments(self):
        """Method to register the CLI arguments for the transcription service"""
        self.add_argument('-l', '--language', help = 'Language of the transcription', default = 'es-ES')

def get_rtsp_source() -> str:
    global cli_arguments
    user = cli_arguments.camera_user
    password = cli_arguments.camera_password
    ip_address = cli_arguments.camera_ip
    rtsp_string = f'rtsp://{ user }:{ password }@{ ip_address }:9000/live'
    print(rtsp_string)
    return rtsp_string

def get_path_to_output() -> str:
    return cli_arguments.path_to_file

def get_output_file_name() -> str:
    output_file_name = cli_arguments.output
    return f'{ output_file_name }.mp4', f'{ output_file_name }.mp3', output_file_name

def get_video_duration() -> str:
    duration = cli_arguments.duration
    return duration if len(duration) > 0 else DEFAULT_DURATION

def record_video(output_file) -> str:
    rstp_source = get_rtsp_source()
    duration = get_video_duration()
    ffmpeg_command = f'''
    ffmpeg -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i { rstp_source } -c copy -bsf:a aac_adtstoasc -t 0:0:{ duration } { output_file }
    '''
    print(ffmpeg_command)
    os.system(ffmpeg_command)

def extract_audio(output_video, output_mp3) -> str:
    os.system(f'''
    ffmpeg -i { output_video } { output_mp3 }
    ''')

def record_audio() -> str:
    output_path = get_path_to_output()
    output_file_names = get_output_file_name()

    video_file_name = output_file_names[0]
    audio_file_name = output_file_names[1]
    file_without_extension = output_file_names[2]
    path_to_video = f'{ output_path }/{ video_file_name }'
    path_to_audio = f'{ output_path }/{ audio_file_name }'
    record_video(path_to_video)
    extract_audio(path_to_video, path_to_audio)
    return path_to_audio, file_without_extension

# Aqui empieza lo de AWS

class AWSService:

    def __init__(
        self,
        bucket,
        path_to_file: str
    ):
        self.bucket = bucket
        self.s3_path = f's3://{ self.bucket }'
        self.object_name = os.path.basename(path_to_file)
        self.path_to_file = path_to_file

    def upload_audio_file(self):
        os.system(f'aws s3 cp --acl public-read { self.path_to_file } { self.s3_path }/{ self.object_name }')

    def execute_transcription(self, transcription_name: str, language: str):
        os.system(f'''
            aws transcribe start-transcription-job --language-code "{ language }" --media-format mp3 --transcription-job-name "{ transcription_name }" --media "MediaFileUri={ self.s3_path }/{ self.object_name }" --output-bucket-name "{ self.bucket }"
        ''')



def upload_file(path_to_file, audio_file_name: str) -> str:
    bucket_name = cli_arguments.remote
    language = cli_arguments.language
    transcription_name = audio_file_name
    
    aws_service = AWSService(bucket = bucket_name, path_to_file = path_to_file)
    aws_service.upload_audio_file()
    aws_service.execute_transcription(transcription_name, language)
    return f'{ transcription_name }.json', bucket_name


def fetch_transcript_file(transcript_file_name: str, bucket_name: str):
    print('Esperando a que se genere la transcripción...')
    time.sleep(50)
    os.system(f'''aws s3api get-object --bucket "{ bucket_name }" --key { transcript_file_name } { transcript_file_name }''')
    
    name_components = transcript_file_name.split('.')
    file_name = name_components.pop(0)
    return file_name, transcript_file_name

# Aqui termina lo de AWS

def retrieve_file_content(transcript_file_name: str):
    with open(transcript_file_name, 'r') as file:
        output = json.load(file)

    first_result = output['results']['transcripts'].pop(0)
    return first_result['transcript']

def write_transcript_file(transcript_result: str, file_name_without_extension: str):
    output_file_name = f'{ file_name_without_extension }.txt'
    with open(output_file_name, 'w+') as file:
        file.write(transcript_result)
    return output_file_name

def move_to_frontend_project(transcript_output_file: str, audio_file: str):
    # Comentario de 1 linea
    '''
    Linea 1
    Linea 2
    '''
    audio_file_name =  os.path.basename(audio_file)
    #Pueden poner la ruta a otro front end o eliminarlo (pueden enviar el archivo de salida por medio de una petición HTTP POST a su API)
    frontend_path = input('Introduzca la ruta del frontend (C:/Users.../NazTest): ')
    path_to_texts = f'{ frontend_path }/textos/{ transcript_output_file }'
    path_to_audios = f'{ frontend_path }/audios/{ audio_file_name }'
    os.rename(transcript_output_file, path_to_texts)
    os.rename(audio_file, path_to_audios)


def load_cli_arguments():
    global cli_arguments
    arguments_manager = CLIArguments()
    arguments_manager.initialize()
    cli_arguments = arguments_manager.arguments


def main():
    load_cli_arguments()
    path_to_audio, audio_name_without_extensions = record_audio()
    transcript_file_name, bucket_name = upload_file(path_to_audio, audio_name_without_extensions)
    file_name_without_extension, json_file_name = fetch_transcript_file(transcript_file_name, bucket_name)
    transcript_result = retrieve_file_content(json_file_name)
    transcript_output_file = write_transcript_file(transcript_result, file_name_without_extension)
    move_to_frontend_project(transcript_output_file, path_to_audio)


if __name__ == '__main__':
    main()



"""
s3_client =boto3.client('s3')
s3_Meraki=input('Introduzca el nombre del archivo: ')
s3 = boto3.resource('s3',
                    aws_access_key_id= 'aperezcr@cisco.com',
                    aws_secret_access_key='Ap17WXq15')
					

my_bucket=s3.Bucket(s3_Meraki)
"""

