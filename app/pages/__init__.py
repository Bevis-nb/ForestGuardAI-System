"""各业务页面：指挥总览、火情地图、自主导航、多机协作、火情分析、人机交互、装备管理、系统设置。"""
from __future__ import annotations

from .analysis import AnalysisPage
from .base import Page, Panel, ScrollPage
from .collaboration import CollaborationPage
from .fleet import FleetPage
from .interaction import InteractionPage
from .login import LoginPage
from .map_page import MapPage
from .navigation import NavPage
from .overview import OverviewPage
from .settings import SettingsPage

__all__ = [
    "AnalysisPage",
    "CollaborationPage",
    "FleetPage",
    "InteractionPage",
    "LoginPage",
    "MapPage",
    "NavPage",
    "OverviewPage",
    "Page",
    "Panel",
    "ScrollPage",
    "SettingsPage",
]
