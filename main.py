from pathlib import Path

from menus.menu_principal import menu_principal
from services.repositorio_json import RepositorioJSON
from services.sistema_almoxarifado import SistemaAlmoxarifado


if __name__ == "__main__":
    pasta_projeto = Path(__file__).resolve().parent
    repositorio = RepositorioJSON(pasta_projeto / "dados")
    sistema = SistemaAlmoxarifado(repositorio)
    menu_principal(sistema)
