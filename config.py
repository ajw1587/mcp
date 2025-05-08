import os

from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):

    TAVILY_API_KEY: str ="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"

    class Config:
        env_file = '.env'

env = os.getenv('ENV', 'dev')
config: BaseConfig = BaseConfig()