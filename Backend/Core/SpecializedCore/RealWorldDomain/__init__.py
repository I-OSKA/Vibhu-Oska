"""
Vibhu-Oska AI-OS — RealWorldDomain Specialists
Handles all real-world tasks with domain-specific specialists.
"""

from Backend.Core.SpecializedCore.RealWorldDomain.ExcelCore import ExcelCore
from Backend.Core.SpecializedCore.RealWorldDomain.WebScrapingCore import WebScrapingCore
from Backend.Core.SpecializedCore.RealWorldDomain.FileSystemCore import FileSystemCore
from Backend.Core.SpecializedCore.RealWorldDomain.SystemAdminCore import SystemAdminCore
from Backend.Core.SpecializedCore.RealWorldDomain.KnowledgeCore import KnowledgeCore
from Backend.Core.SpecializedCore.RealWorldDomain.NetworkCore import NetworkCore
from Backend.Core.SpecializedCore.RealWorldDomain.DatabaseAdminCore import DatabaseAdminCore
from Backend.Core.SpecializedCore.RealWorldDomain.CloudCore import CloudCore
from Backend.Core.SpecializedCore.RealWorldDomain.SecurityCore import SecurityCore
from Backend.Core.SpecializedCore.RealWorldDomain.RealWorldRouter import RealWorldRouter

__all__ = [
    "ExcelCore",
    "WebScrapingCore",
    "FileSystemCore",
    "SystemAdminCore",
    "KnowledgeCore",
    "NetworkCore",
    "DatabaseAdminCore",
    "CloudCore",
    "SecurityCore",
    "RealWorldRouter",
]
