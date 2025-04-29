import os

from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):


    class Config:
        env_file = '.env'

env = os.getenv('ENV', 'dev')
config: BaseConfig = BaseConfig()