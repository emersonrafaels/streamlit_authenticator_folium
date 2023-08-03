from dynaconf import settings

from page_authentication import main_authenticator
from configure_logging import configure_logging

# INICIANDO O LOGGER
logger = configure_logging(
    APP_NAME=settings.get("APPNAME_LOG", "FOOTPRINT_PLANEJAMENTO_ESTRATEGICO.log")
)

logger.info("INICIANDO O APP - PLANEJAMENTO ESTRATÉGICO")

# REALIZANDO A AUTENTICAÇÃO NO APP
main_authenticator()
