from configparser import ConfigParser


class Config:
    def __init__(self, configs: ConfigParser) -> None:
        self.server_config: Config.ServerConfig = Config.ServerConfig(configs)
        self.user_config: Config.UserConfig = Config.UserConfig(configs)
        self.validate_config()

    class ServerConfig:
        def __init__(self, configs: ConfigParser) -> None:
            self.service_url: str = configs.get("Server", "SERVICE_URL")
            self.service_port: str = configs.get("Server", "SERVICE_PORT")

    class UserConfig:
        def __init__(self, configs: ConfigParser) -> None:
            self.user_1_email: str = configs.get("Users", "USER_1_EMAIL")
            self.user_1_password: str = configs.get("Users", "USER_1_PASSWORD")
            self.user_2_email: str = configs.get("Users", "USER_2_EMAIL")
            self.user_2_password: str = configs.get("Users", "USER_2_PASSWORD")
            self.user_3_email: str = configs.get("Users", "USER_3_EMAIL")
            self.user_3_password: str = configs.get("Users", "USER_3_PASSWORD")

    def validate_config(self) -> None:
        config_schema = {
            "server_config": ["service_url", "service_port"],
            "user_config": [
                "user_1_email",
                "user_1_password",
                "user_2_email",
                "user_2_password",
                "user_3_email",
                "user_3_password",
            ],
        }

        for config_section, env_keys in config_schema.items():
            if not hasattr(self, config_section):
                raise AttributeError(
                    f"Missing section {config_section} in the config file"
                )

            section_instance = getattr(self, config_section)

            for key in env_keys:
                if not hasattr(section_instance, key):
                    raise AttributeError(
                        f"Missing key {key} under section {config_section} in the config file"
                    )

                value = getattr(section_instance, key)

                if not self.is_valid_config(str(value)):
                    raise ValueError(
                        f"Missing value for {key} under section {config_section} in the config file"  # noqa: E501
                    )

    @staticmethod
    def is_valid_config(config: str) -> bool:
        return (
            config is not None
            and config.strip() != ""
            and config.strip().lower() != "none"
        )
