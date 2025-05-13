import pika
from platform_health import HZCheckBase, HZStatus
from platform_health.utils import ParentStatus
import logging
from typing import Optional, Dict, Any, Tuple

class RabbitMQChecker(HZCheckBase):
    def __init__(
        self,
        app_health_status: ParentStatus,
        module_health_status: ParentStatus,
        checker_name: str,
        module_name: str,
        rabbitmq_config: Dict[str, Any],
        module_description: Optional[str] = None,
        checker_timeout: Optional[int] = 10,
        tags: Optional[list] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(
            app_health_status=app_health_status,
            module_health_status=module_health_status,
            checker_name=checker_name,
            module_name=module_name,
            module_description=module_description,
            checker_timeout=checker_timeout,
            tags=tags,
            logger=logger,
        )
        self.config = rabbitmq_config
        self.status = HZStatus.KO

    async def get_hz_health(self, *args, **kwargs) -> Tuple[HZStatus, str]:
        error_message = ""
        try:
            credentials = pika.PlainCredentials(self.config["username"], self.config["password"])
            parameters = pika.ConnectionParameters(
                host=self.config["host"],
                port=int(self.config.get("port", 5672)),
                credentials=credentials,
                heartbeat=0,
                blocked_connection_timeout=5
            )
            connection = pika.BlockingConnection(parameters)
            if connection.is_open:
                self.status = HZStatus.OK
                connection.close()
            else:
                self.status = HZStatus.KO
                error_message = "Connection to RabbitMQ could not be established."
        except Exception as err:
            self.logger.error(f"RabbitMQ health check error: {err}")
            error_message = str(err)
            self.status = HZStatus.KO
        return self.status, error_message

