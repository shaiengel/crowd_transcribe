import boto3
from dependency_injector import containers, providers

from crowd_transcribe.config import Config
from crowd_transcribe.infrastructure.s3_client import S3Client
from crowd_transcribe.services.audio_service import AudioService
from crowd_transcribe.services.media_sync import MediaSyncService
from crowd_transcribe.services.tasks_service import TasksService


def _create_session(config: Config) -> boto3.Session:
    return boto3.Session(profile_name=config.aws_profile, region_name=config.aws_region)


class DependenciesContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config)

    session = providers.Singleton(_create_session, config=config)

    s3_boto_client = providers.Singleton(
        lambda sess: sess.client("s3"),
        sess=session,
    )

    s3_client = providers.Singleton(S3Client, client=s3_boto_client)

    media_sync = providers.Singleton(MediaSyncService, file_manager=s3_client, config=config)

    audio_service = providers.Singleton(AudioService, config=config)

    tasks_service = providers.Singleton(TasksService, config=config, s3_client=s3_client)
