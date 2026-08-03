"""
乐云泰App自动化测试 - pytest fixtures
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyt.common.device_manager import DeviceManager
from lyt.common.app_helper import AppHelper
from lyt.pages.login_page import LoginPage
from lyt.pages.home_page import HomePage
from lyt.pages.orders_page import OrdersPage
from lyt.pages.goods_page import GoodsPage
from lyt.pages.mine_page import MinePage


PACKAGE = "com.grl.leyuntai"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


@pytest.fixture(scope="session")
def dm():
    dm = DeviceManager(PACKAGE)
    dm.connect()
    yield dm
    dm.cleanup()


@pytest.fixture(scope="session")
def app(dm):
    return AppHelper(dm)


@pytest.fixture(scope="session")
def login(dm):
    return LoginPage(dm.d)


@pytest.fixture(scope="session")
def home(dm):
    return HomePage(dm.d)


@pytest.fixture(scope="session")
def orders(dm):
    return OrdersPage(dm.d)


@pytest.fixture(scope="session")
def goods(dm):
    return GoodsPage(dm.d)


@pytest.fixture(scope="session")
def mine(dm):
    return MinePage(dm.d)
