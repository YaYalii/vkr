import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000',  # если вызывается внутри контейнера
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

def get_call_audio(bell_id):
    filename = f'call_{bell_id}.wav'
    response = s3.get_object(Bucket='call-recordings', Key=filename)
    return response['Body'].read()

