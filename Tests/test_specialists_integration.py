"""
Vibhu-Oska AI-OS — Specialist Integration Tests
Tests that all specialists work correctly with the SpecialistRouter.
"""

import asyncio
import pytest
from typing import Any

from Backend.Core.MainCore.OrchestratorCore.SpecialistRouter import SpecialistRouter
from Backend.Core.SpecializedCore.CodingDomain import (
    PythonCore,
    CppCore,
    RustCore,
    JavaScriptCore,
    GoCore,
    SQLCore,
    BashShellCore,
    RegexCore,
    CodingRouter,
)
from Backend.Core.SpecializedCore.RealWorldDomain import (
    ExcelCore,
    WebScrapingCore,
    FileSystemCore,
    SystemAdminCore,
    KnowledgeCore,
    NetworkCore,
    DatabaseAdminCore,
    CloudCore,
    SecurityCore,
    RealWorldRouter,
)


class TestSpecialistIntegration:
    """Integration tests for all specialists with SpecialistRouter."""

    @pytest.fixture
    def router(self) -> SpecialistRouter:
        """Create a SpecialistRouter instance."""
        return SpecialistRouter()

    @pytest.fixture
    def coding_specialists(self) -> list:
        """Create all coding specialists."""
        return [
            PythonCore(),
            CppCore(),
            RustCore(),
            JavaScriptCore(),
            GoCore(),
            SQLCore(),
            BashShellCore(),
            RegexCore(),
            CodingRouter(),
        ]

    @pytest.fixture
    def real_world_specialists(self) -> list:
        """Create all real-world specialists."""
        return [
            ExcelCore(),
            WebScrapingCore(),
            FileSystemCore(),
            SystemAdminCore(),
            KnowledgeCore(),
            NetworkCore(),
            DatabaseAdminCore(),
            CloudCore(),
            SecurityCore(),
            RealWorldRouter(),
        ]

    @pytest.mark.asyncio
    async def test_coding_specialists_initialization(self, coding_specialists: list) -> None:
        """Test that all coding specialists can be initialized."""
        for specialist in coding_specialists:
            await specialist.initialize()
            assert specialist._initialized is True

    @pytest.mark.asyncio
    async def test_real_world_specialists_initialization(self, real_world_specialists: list) -> None:
        """Test that all real-world specialists can be initialized."""
        for specialist in real_world_specialists:
            await specialist.initialize()
            assert specialist._initialized is True

    @pytest.mark.asyncio
    async def test_python_core_processing(self) -> None:
        """Test PythonCore processing."""
        specialist = PythonCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I debug Python code?",
        })
        
        assert result.success is True
        assert "PythonCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_cpp_core_processing(self) -> None:
        """Test CppCore processing."""
        specialist = CppCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "Explain C++ smart pointers",
        })
        
        assert result.success is True
        assert "CppCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_rust_core_processing(self) -> None:
        """Test RustCore processing."""
        specialist = RustCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How does Rust ownership work?",
        })
        
        assert result.success is True
        assert "RustCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_javascript_core_processing(self) -> None:
        """Test JavaScriptCore processing."""
        specialist = JavaScriptCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "Explain TypeScript generics",
        })
        
        assert result.success is True
        assert "JavaScriptCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_go_core_processing(self) -> None:
        """Test GoCore processing."""
        specialist = GoCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do goroutines work?",
        })
        
        assert result.success is True
        assert "GoCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_sql_core_processing(self) -> None:
        """Test SQLCore processing."""
        specialist = SQLCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "Optimize this SQL query",
        })
        
        assert result.success is True
        assert "SQLCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_bash_shell_core_processing(self) -> None:
        """Test BashShellCore processing."""
        specialist = BashShellCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I use awk for text processing?",
        })
        
        assert result.success is True
        assert "BashShellCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_regex_core_processing(self) -> None:
        """Test RegexCore processing."""
        specialist = RegexCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "Write a regex for email validation",
        })
        
        assert result.success is True
        assert "RegexCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_excel_core_processing(self) -> None:
        """Test ExcelCore processing."""
        specialist = ExcelCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I use VLOOKUP in Excel?",
        })
        
        assert result.success is True
        assert "ExcelCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_web_scraping_core_processing(self) -> None:
        """Test WebScrapingCore processing."""
        specialist = WebScrapingCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I scrape with BeautifulSoup?",
        })
        
        assert result.success is True
        assert "WebScrapingCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_file_system_core_processing(self) -> None:
        """Test FileSystemCore processing."""
        specialist = FileSystemCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I use pathlib for file operations?",
        })
        
        assert result.success is True
        assert "FileSystemCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_system_admin_core_processing(self) -> None:
        """Test SystemAdminCore processing."""
        specialist = SystemAdminCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I create a systemd service?",
        })
        
        assert result.success is True
        assert "SystemAdminCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_knowledge_core_processing(self) -> None:
        """Test KnowledgeCore processing."""
        specialist = KnowledgeCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "Explain quantum physics basics",
        })
        
        assert result.success is True
        assert "KnowledgeCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_network_core_processing(self) -> None:
        """Test NetworkCore processing."""
        specialist = NetworkCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I design a REST API?",
        })
        
        assert result.success is True
        assert "NetworkCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_database_admin_core_processing(self) -> None:
        """Test DatabaseAdminCore processing."""
        specialist = DatabaseAdminCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I configure PostgreSQL replication?",
        })
        
        assert result.success is True
        assert "DatabaseAdminCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_cloud_core_processing(self) -> None:
        """Test CloudCore processing."""
        specialist = CloudCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I use AWS Lambda?",
        })
        
        assert result.success is True
        assert "CloudCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_security_core_processing(self) -> None:
        """Test SecurityCore processing."""
        specialist = SecurityCore()
        await specialist.initialize()
        
        result = await specialist.process_with_tracking({
            "prompt": "How do I implement JWT authentication?",
        })
        
        assert result.success is True
        assert "SecurityCore" in result.metadata.get("specialist", "")
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_router_registration(self, router: SpecialistRouter, coding_specialists: list, real_world_specialists: list) -> None:
        """Test that all specialists can be registered with the router."""
        for specialist in coding_specialists:
            await specialist.initialize()
            router.register(specialist.name, specialist)
        
        for specialist in real_world_specialists:
            await specialist.initialize()
            router.register(specialist.name, specialist)
        
        metrics = router.get_metrics()
        assert metrics["registered_specialists"] == len(coding_specialists) + len(real_world_specialists)

    @pytest.mark.asyncio
    async def test_router_routing(self, router: SpecialistRouter) -> None:
        """Test that the router can route to specialists."""
        # Register PythonCore
        python_core = PythonCore()
        await python_core.initialize()
        router.register("PythonCore", python_core)
        
        # Route a task
        result = await router.route(
            domain="code_generation",
            subdomain="python",
            input_data={"prompt": "Write a Python function"},
        )
        
        assert result["success"] is True
        assert result["specialist"] == "PythonCore"

    @pytest.mark.asyncio
    async def test_router_fallback(self, router: SpecialistRouter) -> None:
        """Test that the router falls back when no specialist is available."""
        result = await router.route(
            domain="unknown_domain",
            subdomain="unknown",
            input_data={"prompt": "Unknown task"},
        )
        
        # Should fallback to BackupCore or return no specialist
        assert result["success"] is True or result["method"] == "failed"

    @pytest.mark.asyncio
    async def test_coding_router_detection(self) -> None:
        """Test CodingRouter language detection."""
        router = CodingRouter()
        await router.initialize()
        
        # Test Python detection
        assert router.detect_language("Write a Python function") == "python"
        
        # Test C++ detection
        assert router.detect_language("Explain C++ templates") == "cpp"
        
        # Test Rust detection
        assert router.detect_language("How does Rust ownership work?") == "rust"
        
        # Test JavaScript detection
        assert router.detect_language("Explain TypeScript generics") == "javascript"
        
        # Test Go detection
        assert router.detect_language("How do goroutines work?") == "go"
        
        # Test SQL detection
        assert router.detect_language("Optimize this SQL query") == "sql"
        
        # Test Bash detection
        assert router.detect_language("How do I use awk?") == "bash"

    @pytest.mark.asyncio
    async def test_real_world_router_detection(self) -> None:
        """Test RealWorldRouter domain detection."""
        router = RealWorldRouter()
        await router.initialize()
        
        # Test Excel detection
        assert router.detect_domain("How do I use pivot tables?") == "excel"
        
        # Test web scraping detection
        assert router.detect_domain("How do I scrape with BeautifulSoup?") == "web_scraping"
        
        # Test file system detection
        assert router.detect_domain("How do I use pathlib?") == "file_system"
        
        # Test system admin detection
        assert router.detect_domain("How do I create a systemd service?") == "system_admin"
        
        # Test knowledge detection
        assert router.detect_domain("Explain quantum physics") == "knowledge"
        
        # Test networking detection
        assert router.detect_domain("How do I design a REST API?") == "networking"
        
        # Test security detection
        assert router.detect_domain("How do I implement JWT?") == "security"
        
        # Test cloud detection
        assert router.detect_domain("How do I use AWS Lambda?") == "cloud"
        
        # Test database detection
        assert router.detect_domain("How do I configure PostgreSQL?") == "database"
