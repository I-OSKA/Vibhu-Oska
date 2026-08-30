"""
Vibhu-Oska AI-OS — OrchestratorCore (Brahma — The Creator)
Driven by the ZeroMQ Event Bus, orchestrating the request processing lifecycle.
Absorbs HybridCore routing: speculative router, primary/backup handover, contingency protocol.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any

from Backend.Core.BackupCore.BackupCore import BackupCore
from Backend.Core.EventBus.EventBus import EventBus
from Backend.Core.EventBus.Events import Event, EventFactory
from Backend.Core.EventBus.Topics import Topics
from Backend.Core.MainCore.CognitionCore.cognition import CognitionCore
from Backend.Core.MainCore.ValidationCore.validation import ValidationCore
from Backend.Core.MainCore.MonitoringCore.MonitoringCore import MonitoringCore
from Backend.Core.MainCore.OptimizationCore.OptimizationCore import OptimizationCore
from Backend.Core.MainCore.HardwareAdapter.HardwareAdapter import HardwareAdapter
from Backend.Core.MainCore.QuantumEngine.QuantumEngine import QuantumEngine
from Backend.Core.SpecializedCore.DataCore.datacore import DataCore
from Backend.Core.SpecializedCore.AutomationCore.AutomationCore import AutomationCore
from Backend.Core.SpecializedCore.DesignCore.DesignCore import DesignCore
from Backend.Core.SpecializedCore.ImageGenerationCore.ImageGenerationCore import ImageGenerationCore
from Backend.Plugins.Logger.Logger import Logger
from Backend.Plugins.ToolRegistry.Registry import ToolRegistry
from Shared.Models import TaskResponse, ExecutionTarget, CoreStatus, StatusCode


class OrchestratorCore:
    """
    OrchestratorCore (Brahma) manages the lifecycle of chat & task execution.
    Driven by event subscriptions, coordinating double-validation, memory, and cognition.

    Absorbs HybridCore routing responsibilities:
    - Speculative router model (task/target classification)
    - Primary (CognitionCore/GPU) → Backup (BackupCore/CPU) handover
    - Contingency protocol: fault, timeout, capacity overflow
    """

    def __init__(self) -> None:
        self._event_bus: EventBus | None = None
        self._registry: ToolRegistry | None = None
        self._data_core = DataCore()
        self._validation = ValidationCore()
        self._monitoring = MonitoringCore()
        self._optimization = OptimizationCore()
        self._automation_core = AutomationCore()
        self._design_core = DesignCore()
        self._image_core = ImageGenerationCore()
        self._log = Logger.get("Orchestrator")
        self._initialized = False

        # ── Routing state (absorbed from HybridCore) ──────────────────────
        self._primary: CognitionCore | None = None
        self._backup: BackupCore | None = None
        self._status = CoreStatus.HEALTHY
        self._primary_timeout = 60.0
        self._max_concurrent_primary = 2
        self._primary_in_flight = 0
        self._router = None
        self._router_tokenizer = None

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def status(self) -> CoreStatus:
        return self._status

    @property
    def backup_core(self) -> BackupCore:
        return self._backup

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self, event_bus: EventBus, registry: ToolRegistry) -> None:
        """Boot the orchestrator and subscribe to central user input events."""
        if self._initialized:
            return

        self._event_bus = event_bus
        self._registry = registry

        # Initialize sub-cores
        await self._data_core.initialize(registry)
        self._validation.initialize()
        await self._monitoring.initialize(registry, event_bus)
        await self._optimization.initialize(registry)
        await self._automation_core.initialize()
        await self._design_core.initialize()
        await self._image_core.initialize()

        # ── Initialize HardwareAdapter (auto-detect hardware) ──────────
        self._hardware_adapter = HardwareAdapter.get_instance()
        await self._hardware_adapter.initialize()
        hw_config = self._hardware_adapter.get_config()
        self._log.info(
            "HardwareAdapter: tier=%s, backend=%s, context=%d, threads=%d",
            self._hardware_adapter.get_profile().power_tier.value,
            hw_config.backend_device,
            hw_config.context_window,
            hw_config.threads,
        )

        # ── Initialize QuantumEngine (CPU-only, limited usage) ─────────
        self._quantum_engine = QuantumEngine.get_instance()
        await self._quantum_engine.initialize()

        # ── Initialize routing cores (absorbed from HybridCore) ──────────
        primary_cog = registry.get_safe("cognition")
        if primary_cog and isinstance(primary_cog, CognitionCore):
            self._primary = primary_cog
        else:
            self._primary = CognitionCore()
        self._backup = BackupCore()

        await self._primary.initialize()
        self._status = CoreStatus.HEALTHY

        # Pre-load router in background so first request doesn't pay the load cost
        try:
            await asyncio.to_thread(self._load_router)
            self._log.info("Speculative router pre-loaded on startup")
        except Exception as e:
            self._log.warning("Router pre-load failed — will load on first request", error=str(e))

        # Subscribe to user inputs
        await self._event_bus.subscribe(Topics.USER_INPUT, self.handle_user_input)
        
        # Subscribe to scheduled training/feedback events
        await self._event_bus.subscribe("feedback.export", self.handle_feedback_export)
        await self._event_bus.subscribe("training.eval", self.handle_training_eval)
        
        self._log.info("Orchestrator registered on EventBus", topics=[Topics.USER_INPUT, "feedback.export", "training.eval"])
        self._initialized = True

    async def shutdown(self) -> None:
        """Teardown orchestrator components."""
        await self._data_core.shutdown()
        self._initialized = False

    # ── Health Check ──────────────────────────────────────────────────────────

    async def check_health(self) -> bool:
        """Directly query primary model status to see if it is online."""
        try:
            test_resp = await self._primary.generate("ping", max_tokens=1)
            self._status = CoreStatus.HEALTHY
            return True
        except Exception:
            self._status = CoreStatus.DEGRADED
            return False

    # ==================================================================================================

    # # Router Loading (Absorbed from HybridCore)

    # =================─────────────────────────────────────────────────────────────────────────────────

    def _load_router(self) -> None:
        """Lazily load the router model and BPE tokenizer."""
        if hasattr(self, "_router") and self._router is not None:
            return

        try:
            import torch
            from pathlib import Path
            from Models.router.architecture import RouterConfig, VibhuOskaRouter
            from Models.karsh.tokenizer import KarshBPETokenizer

            root = Path(__file__).resolve().parent.parent.parent.parent.parent
            ckpt_dir = root / "Models" / "router" / "checkpoints"
            ckpt_path = ckpt_dir / "best_router.pt"
            vocab_path = ckpt_dir / "router_vocab.json"

            if not ckpt_path.exists() or not vocab_path.exists():
                self._log.warning("Router checkpoints not found. Speculative routing is disabled.", ckpt=str(ckpt_path))
                self._router = None
                self._router_tokenizer = None
                return

            self._log.info("Loading speculative router model and tokenizer...")
            self._router_tokenizer = KarshBPETokenizer.load(vocab_path)

            checkpoint = torch.load(ckpt_path, map_location="cpu")
            cfg_dict = checkpoint["config"]

            valid_keys = {
                "vocab_size", "hidden_size", "intermediate_size", "num_layers",
                "num_heads", "max_seq_len", "dropout", "layer_norm_eps",
                "num_target_classes", "num_task_classes", "pad_token_id"
            }
            cfg_filtered = {k: v for k, v in cfg_dict.items() if k in valid_keys}

            config = RouterConfig(**cfg_filtered)
            model = VibhuOskaRouter(config)
            model.load_state_dict(checkpoint["model_state"])
            model.eval()

            self._router = model
            self._log.info("Router loaded successfully.")
        except Exception as e:
            self._log.error("Failed to load speculative router", error=str(e))
            self._router = None
            self._router_tokenizer = None

    # ==================================================================================================

    # # Request Routing (Absorbed from HybridCore)

    # =================─────────────────────────────────────────────────────────────────────────────────

    async def _route_request(
        self,
        prompt: str,
        system_prompt: str,
        context: list[dict[str, Any]] | None,
        model_id: str,
    ) -> TaskResponse:
        """
        Strict contingency routing protocol (absorbed from HybridCore):

        1. Everything routes through the PRIMARY engine first.
        2. BackupCore activates ONLY on:
           a. primary execution fault,
           b. primary at max capacity (in-flight threshold),
           c. primary unresponsive (asyncio.wait_for timeout).
        3. Every handover is logged (error for fault/timeout, warning for capacity)
           and stamped with contingency metadata.
        """
        # Speculative routing if model_id is not explicitly set
        if not model_id:
            try:
                self._load_router()
                if hasattr(self, "_router") and self._router is not None and self._router_tokenizer is not None:
                    import torch
                    from Models.router.train import pad_sequence

                    raw_ids = self._router_tokenizer.encode(prompt)
                    max_len = self._router.config.max_seq_len
                    ids, attn = pad_sequence(raw_ids, max_len, pad_id=self._router_tokenizer.pad_id)

                    input_ids = torch.tensor([ids], dtype=torch.long)
                    attention_mask = torch.tensor([attn], dtype=torch.long)

                    prediction = self._router.predict(input_ids, attention_mask)
                    self._log.info(
                        "Speculative router predicted task/target",
                        task=prediction["task"],
                        target=prediction["target"],
                        task_conf=prediction["task_conf"],
                        target_conf=prediction["target_conf"]
                    )

                    model_id = "karsh"
                    self._log.info("Speculative routing -> Karsh (Primary GPU Core)")
                else:
                    model_id = "karsh"
            except Exception as e:
                self._log.warning("Speculative routing failed, attempting Karsh as primary default", error=str(e))
                model_id = "karsh"

        # Explicit backup request (user-forced contingency)
        if model_id == "backup-1":
            return await self._handover(
                reason="explicit",
                error="Explicit backup-1 model request",
                prompt=prompt,
                system_prompt=system_prompt,
                context=context,
            )

        # Primary at capacity → handover without attempting primary
        if self._primary_in_flight >= self._max_concurrent_primary:
            return await self._handover(
                reason="capacity",
                error=f"Primary at capacity (in-flight={self._primary_in_flight})",
                prompt=prompt,
                system_prompt=system_prompt,
                context=context,
            )

        # Try primary (with unresponsiveness guard)
        try:
            self._log.info("Routing request to primary local GPU inference engine", prompt_len=len(prompt))
            self._primary_in_flight += 1
            try:
                response = await asyncio.wait_for(
                    self._primary.generate(
                        prompt,
                        system_prompt=system_prompt,
                        context=context,
                        model_id=model_id,
                    ),
                    timeout=self._primary_timeout,
                )
            finally:
                self._primary_in_flight -= 1

            # Update target metadata
            response.metadata.executed_on = ExecutionTarget.GPU
            self._status = CoreStatus.HEALTHY
            return response

        except asyncio.TimeoutError as e:
            return await self._handover(
                reason="timeout",
                error=f"Primary inference timed out after {self._primary_timeout}s",
                prompt=prompt,
                system_prompt=system_prompt,
                context=context,
            )

        except Exception as e:
            return await self._handover(
                reason="fault",
                error=str(e),
                prompt=prompt,
                system_prompt=system_prompt,
                context=context,
            )

    # ── Streaming routing ──────────────────────────────────────────────────

    async def _route_request_stream(
        self,
        prompt: str,
        system_prompt: str,
        context: list[dict[str, Any]] | None,
        model_id: str,
    ):
        """Streaming variant of _route_request — yields (token_id, accumulated_text) tuples.
        Falls back to non-streaming BackupCore on primary failure (yields full text as single chunk).
        """
        # Resolve model_id
        if not model_id:
            model_id = "karsh"

        if model_id == "backup-1":
            resp = await self._handover(
                reason="explicit", error="Explicit backup request",
                prompt=prompt, system_prompt=system_prompt, context=context,
            )
            yield resp.content
            return

        if self._primary_in_flight >= self._max_concurrent_primary:
            resp = await self._handover(
                reason="capacity",
                error=f"Primary at capacity (in-flight={self._primary_in_flight})",
                prompt=prompt, system_prompt=system_prompt, context=context,
            )
            yield resp.content
            return

        try:
            self._primary_in_flight += 1
            try:
                async for token_id, accumulated in self._primary.generate_karsh_stream(
                    prompt, system_prompt=system_prompt, context=context,
                ):
                    yield token_id, accumulated
            finally:
                self._primary_in_flight -= 1
            self._status = CoreStatus.HEALTHY

        except (asyncio.TimeoutError, Exception) as e:
            reason = "timeout" if isinstance(e, asyncio.TimeoutError) else "fault"
            self._log.warning(f"Streaming primary {reason}", error=str(e))
            self._status = CoreStatus.DEGRADED
            resp = await self._handover(
                reason=reason, error=str(e),
                prompt=prompt, system_prompt=system_prompt, context=context,
            )
            yield resp.content

    async def _handover(
        self,
        reason: str,
        error: str,
        prompt: str,
        system_prompt: str,
        context: list[dict[str, Any]] | None,
    ) -> TaskResponse:
        """
        STRICT FALLBACK HANDOVER: log the activation, assume control via the
        shared BackupCore instance, and stamp contingency metadata.
        """
        if reason in ("fault", "timeout"):
            self._log.error(
                "SYSTEM ERROR DETECTED: Primary core failed or is offline. Handing over to BackupCore.",
                reason=reason,
                primary_error=str(error),
                prompt_preview=prompt[:60],
            )
            self._status = CoreStatus.DEGRADED
        else:
            self._log.warning(
                "Handing over to BackupCore.",
                reason=reason,
                primary_error=str(error),
                prompt_preview=prompt[:60],
            )

        response = await self._backup.activate(
            reason=reason,
            error=error,
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
        )
        response.metadata.executed_on = ExecutionTarget.CPU

        if response.metadata.status.code == StatusCode.COMPLETED:
            response.metadata.status.message = (
                f"Contingency Handover ({reason}): {response.metadata.status.message} "
                f"(Fault: {str(error)[:60]})"
            )

        return response

    # ==================================================================================================

    # # Event-Driven Orchestration Pipeline

    # =================─────────────────────────────────────────────────────────────────────────────────

    async def handle_user_input(self, event: Event) -> None:
        """
        Orchestration pipeline triggered by incoming user inputs.
        Flow: input → validate → memory context → specialized routing → cognition → validate → publish.
        """
        if not self._initialized:
            return

        prompt = event.payload.get("prompt", "")
        session_id = event.payload.get("session_id", "")
        user_id = event.payload.get("user_id", "operator")
        model_id = event.payload.get("model_id", "")
        request_id = event.event_id

        # Bind tracing ID for diagnostics
        Logger.bind_request(request_id)
        self._log.info("Processing user input event", session_id=session_id, user_id=user_id)
        start_time = time.time()

        try:
            # 1. VALIDATION CORE (Input Gate)
            input_pkg = {
                "prompt": prompt,
                "type": 1,  # CHAT
                "metadata": {
                    "request_id": request_id,
                    "session_id": session_id,
                    "user_id": user_id
                }
            }

            is_valid, reason = self._validation.validate_input_package(input_pkg)
            if not is_valid:
                self._log.warning("Input failed validation check", reason=reason)
                fail_event = Event(
                    topic=Topics.TASK_FAILED,
                    source="orchestrator",
                    payload={"request_id": request_id, "error": f"Input validation failed: {reason}"}
                )
                await self._event_bus.publish(fail_event)

                alert_event = EventFactory.alert(
                    source="validation",
                    title="Input Validation Failure",
                    description=f"Request {request_id} rejected: {reason}",
                    severity=1
                )
                await self._event_bus.publish(alert_event)
                return

            # 1.5 OPTIMIZATION CORE (Cache Check)
            cached_reply = await self._optimization.check_query_cache(prompt)
            if cached_reply:
                self._log.info("Cache hit! Serving response directly", prompt=prompt)

                await self._data_core.create_session(session_id, user_id)
                user_msg_id = str(uuid.uuid4())
                ai_msg_id = str(uuid.uuid4())
                await self._data_core.save_chat_message(user_msg_id, session_id, "user", prompt)
                await self._data_core.save_chat_message(ai_msg_id, session_id, "assistant", cached_reply)

                completed_payload = {
                    "content": cached_reply,
                    "request_id": request_id,
                    "metadata": {
                        "status": {"code": 5, "message": "Inference completed successfully (cache hit)"},
                        "processing_time_ms": int((time.time() - start_time) * 1000)
                    }
                }
                completed_event = Event(
                    topic=Topics.TASK_COMPLETED,
                    source="orchestrator",
                    payload=completed_payload
                )
                await self._event_bus.publish(completed_event)
                return

            # 2. CREATE TASK & PERSIST SESSION
            await self._data_core.create_session(session_id, user_id)

            created_event = EventFactory.task_created(
                task_id=request_id,
                task_type="chat",
                prompt=prompt
            )
            await self._event_bus.publish(created_event)

            # 3. DATA CORE (Context Retrieval)
            history = await self._data_core.get_session_history(session_id, limit=2)
            semantic_context = await self._data_core.query_memory(prompt, top_k=1)
            kg_context_str = await self._data_core.query_knowledge_graph(prompt)

            context = []
            for msg in history:
                context.append({
                    "source": f"chat_history:{msg['role']}",
                    "content": msg["content"]
                })
            context.extend(semantic_context)
            if kg_context_str:
                context.append({
                    "source": "knowledge_graph",
                    "content": kg_context_str
                })

            context = await self._optimization.optimize_prompt_context(context)

            # 4. SPECIALIZED CORE ROUTING (Pre-Cognition Task Dispatcher)
            specialized_response = await self._route_to_specialized_core(prompt, context)
            if specialized_response is not None:
                response = specialized_response
            else:
                # 4b. PRIMARY ROUTING (CognitionCore/GPU → BackupCore/CPU handover)
                system_prompt = (
                    "You are Vibhu-Oska AI-OS. Respond concisely and professionally. "
                    "Ensure your response is valid and answers the prompt directly."
                )
                response = await self._route_request(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    context=context,
                    model_id=model_id
                )

            # 5. DYNAMIC TOOL REGISTRY (Tool Execution)
            if response.tool_calls:
                for tool in response.tool_calls:
                    self._log.info("Executing tool call", tool=tool.tool_name, action=tool.action)
                    tool_req = EventFactory.tool_request(
                        tool_name=tool.tool_name,
                        action=tool.action,
                        arguments=json.loads(tool.arguments_json)
                    )
                    await self._event_bus.publish(tool_req)

                    try:
                        plugin = self._registry.get(tool.tool_name)
                        result = await plugin.execute(tool.action, **json.loads(tool.arguments_json))

                        tool_res = Event(
                            topic=Topics.tool_result_for(tool.tool_name),
                            source="orchestrator",
                            payload={"status": "success", "result": result}
                        )
                        await self._event_bus.publish(tool_res)
                    except Exception as err:
                        self._log.error("Tool execution failed", tool=tool.tool_name, error=str(err))
                        tool_res = Event(
                            topic=Topics.tool_result_for(tool.tool_name),
                            source="orchestrator",
                            payload={"status": "error", "error": str(err)}
                        )
                        await self._event_bus.publish(tool_res)

            # 6. VALIDATION CORE (Output Gate)
            is_output_valid, out_reason = self._validation.validate_ai_output(response)
            if not is_output_valid:
                self._log.error("AI output failed validation check", reason=out_reason)
                fail_event = Event(
                    topic=Topics.TASK_FAILED,
                    source="orchestrator",
                    payload={"request_id": request_id, "error": f"Output validation failed: {out_reason}"}
                )
                await self._event_bus.publish(fail_event)
                return

            # 7. DATA CORE (Save chat interaction)
            user_msg_id = str(uuid.uuid4())
            ai_msg_id = str(uuid.uuid4())
            await self._data_core.save_chat_message(user_msg_id, session_id, "user", prompt)
            await self._data_core.save_chat_message(ai_msg_id, session_id, "assistant", response.content)

            await self._optimization.save_response_cache(prompt, response.content)

            # 8. PUBLISH RESULT
            elapsed_ms = int((time.time() - start_time) * 1000)
            response.metadata.processing_time_ms = elapsed_ms

            completed_payload = response.model_dump()
            completed_payload["request_id"] = request_id

            completed_event = Event(
                topic=Topics.TASK_COMPLETED,
                source="orchestrator",
                payload=completed_payload
            )
            await self._event_bus.publish(completed_event)
            self._log.info("Request completed successfully", elapsed_ms=elapsed_ms)

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            self._log.exception("Unhandled error during request orchestration")

            fail_event = Event(
                topic=Topics.TASK_FAILED,
                source="orchestrator",
                payload={"request_id": request_id, "error": f"Internal exception: {str(e)}"}
            )
            await self._event_bus.publish(fail_event)

        finally:
            Logger.clear_context()

    # ==================================================================================================

    # # Specialized Core Routing

    # =================─────────────────────────────────────────────────────────────────────────────────

    async def _route_to_specialized_core(
        self, prompt: str, context: list[dict[str, Any]]
    ) -> TaskResponse | None:
        """
        Pre-cognition specialized core router.
        Returns None if no specialized core matches — allowing the primary routing path.
        """
        from Shared.Models import TaskResponse, TokenUsage, ResponseMetadata, Status, StatusCode
        import json as _json

        prompt_lower = prompt.lower()

        # ── IMAGE GENERATION ─────────────────────────────────────────────
        _image_triggers = {
            "generate image", "draw", "render image", "create image",
            "picture of", "show me an image", "make an image", "paint",
        }
        if any(trigger in prompt_lower for trigger in _image_triggers):
            try:
                self._log.info("Routing to ImageGenerationCore", prompt_fragment=prompt[:60])
                result = await self._image_core.execute(
                    "generate_image", prompt=prompt
                )
                content = (
                    result.get("message") or
                    result.get("descriptor", {}).get("message") or
                    f"Image generation: {result.get('status', 'unknown')}"
                )
                if result.get("status") == "success" and result.get("image_base64"):
                    content = f"[IMAGE_GENERATED] base64:{result['image_base64'][:64]}..."
                return TaskResponse(
                    content=content,
                    token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    metadata=ResponseMetadata(
                        status=Status(code=StatusCode.COMPLETED, message="Handled by ImageGenerationCore"),
                    ),
                )
            except Exception as e:
                self._log.warning("ImageGenerationCore routing failed, falling back", error=str(e))

        # ── DESIGN / UI GENERATION ────────────────────────────────────────
        _design_triggers = {
            "design", "layout", "ui component", "generate component",
            "create a dashboard", "build a ui", "html", "css layout",
            "interface", "webpage", "make a page",
        }
        if any(trigger in prompt_lower for trigger in _design_triggers):
            try:
                self._log.info("Routing to DesignCore", prompt_fragment=prompt[:60])
                if any(k in prompt_lower for k in ["card", "modal", "table", "nav", "button", "stat"]):
                    comp = next(
                        (c for c in ["card", "modal", "table", "nav_item", "stat_card", "chat"]
                         if c.replace("_", " ") in prompt_lower or c in prompt_lower), "card"
                    )
                    result = await self._design_core.execute(
                        "generate_component",
                        component_type=comp,
                        props={"title": "Generated Component", "body": prompt},
                    )
                    content = f"[COMPONENT_HTML]\n{result.get('html', '')}"
                else:
                    result = await self._design_core.execute(
                        "generate_layout",
                        description=prompt,
                        page_title="Vibhu-Oska Generated",
                    )
                    content = f"[LAYOUT_HTML]\n{result.get('html', '')[:1024]}"

                return TaskResponse(
                    content=content,
                    token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    metadata=ResponseMetadata(
                        status=Status(code=StatusCode.COMPLETED, message="Handled by DesignCore"),
                    ),
                )
            except Exception as e:
                self._log.warning("DesignCore routing failed, falling back", error=str(e))

        # ── OS / AUTOMATION ───────────────────────────────────────────────
        _os_triggers = {
            "list files", "list directory", "list folder", "show files",
            "run command", "execute", "open app", "launch", "open application",
            "cpu usage", "memory usage", "system info", "disk space",
            "what processes", "kill process", "terminate", "check process",
            "read file", "write file", "what is my ram", "gpu info",
            "system status", "hardware",
        }
        if any(trigger in prompt_lower for trigger in _os_triggers):
            try:
                self._log.info("Routing to AutomationCore", prompt_fragment=prompt[:60])

                if any(k in prompt_lower for k in ["cpu", "memory", "ram", "disk", "gpu", "system info", "hardware", "system status"]):
                    result = await self._automation_core.execute("get_system_info")
                    data = result.get("data", {})
                    cpu = data.get("cpu", {})
                    mem = data.get("memory", {})
                    disk = data.get("disk", {})
                    gpu = data.get("gpu", {})
                    content = (
                        f"**System Telemetry**\n"
                        f"CPU: {cpu.get('usage_percent', '?')}% ({cpu.get('physical_cores', '?')} cores @ {cpu.get('frequency_mhz', '?')}MHz)\n"
                        f"Memory: {mem.get('used_gb', '?')}GB used / {mem.get('total_gb', '?')}GB total ({mem.get('usage_percent', '?')}%)\n"
                        f"Disk: {disk.get('free_gb', '?')}GB free / {disk.get('total_gb', '?')}GB total\n"
                        f"GPU: {gpu.get('name', 'N/A')} — {gpu.get('vram_allocated_mb', 'N/A')}MB allocated"
                    )

                elif any(k in prompt_lower for k in ["list files", "list directory", "list folder", "show files"]):
                    import re as _re
                    path_match = _re.search(r'[A-Za-z]:[\\\\./\w\s-]+|/[\w./\s-]+', prompt)
                    target_path = path_match.group(0).strip() if path_match else "."
                    result = await self._automation_core.execute("list_directory", path=target_path)
                    entries = result.get("entries", [])
                    lines = [f"**Directory: {result.get('path', target_path)}**"]
                    for e in entries[:30]:
                        icon = "📁" if e["type"] == "directory" else "📄"
                        size = f" ({e['size_bytes']}B)" if e.get("size_bytes") is not None else ""
                        lines.append(f"{icon} {e['name']}{size}")
                    if len(entries) > 30:
                        lines.append(f"... and {len(entries) - 30} more")
                    content = "\n".join(lines)

                else:
                    result = await self._automation_core.execute("get_system_info")
                    content = f"AutomationCore result: {_json.dumps(result.get('data', result), indent=2)[:800]}"

                return TaskResponse(
                    content=content,
                    token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    metadata=ResponseMetadata(
                        status=Status(code=StatusCode.COMPLETED, message="Handled by AutomationCore"),
                    ),
                )
            except Exception as e:
                self._log.warning("AutomationCore routing failed, falling back", error=str(e))

        # No specialized core matched — return None to trigger primary routing
        return None

    # ══════════════════════════════════════════════════════════════════════
    # Scheduled Event Handlers
    # ══════════════════════════════════════════════════════════════════════

    async def handle_feedback_export(self, event: Event) -> None:
        """Handle feedback export event from Scheduler — export RLHF data and optionally trigger fine-tuning."""
        self._log.info("Handling feedback export event")
        try:
            feedback_collector = self._registry.get_safe("feedback_collector")
            if not feedback_collector:
                self._log.warning("FeedbackCollector not available for export")
                return

            output_file = event.payload.get("output_file", "nightly_feedback.jsonl")
            result = await feedback_collector.execute("export_training_data", output_file=output_file)
            self._log.info("Feedback export completed", result=result)

        except Exception as e:
            self._log.error("Feedback export failed", error=str(e))

    async def handle_training_eval(self, event: Event) -> None:
        """Handle training evaluation event from Scheduler — trigger QLoRA fine-tuning on accumulated feedback."""
        self._log.info("Handling training eval event — triggering QLoRA fine-tuning")
        try:
            # Export feedback data first
            feedback_collector = self._registry.get_safe("feedback_collector")
            if feedback_collector:
                await feedback_collector.execute("export_training_data", output_file="training_feedback.jsonl")

            # Trigger QLoRA fine-tuning via subprocess
            import subprocess
            from pathlib import Path
            root = Path(__file__).resolve().parent.parent.parent.parent.parent
            script = root / "Models" / "reasoning" / "finetune.py"
            if script.exists():
                self._log.info("Launching QLoRA fine-tuning subprocess...")
                subprocess.Popen(
                    ["python", "-m", "Models.reasoning.finetune", "--epochs", "1", "--model", "qwen2.5-coder"],
                    cwd=str(root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self._log.info("QLoRA fine-tuning launched in background")
            else:
                self._log.warning("Fine-tuning script not found at %s", script)

        except Exception as e:
            self._log.error("Training eval failed", error=str(e))

    def process_request(self, request: Any) -> Any:
        """Stub pass-through."""
        pass
