"""Tests for QuantumEngine module — CPU quantum simulation with usage limits."""

import asyncio
import pytest

from Backend.Core.MainCore.QuantumEngine.QuantumEngine import (
    QuantumEngine,
    QuantumOptimizer,
    UsageGovernor,
    QubitState,
    QuantumCircuit,
    QuantumMode,
)


class TestQubitState:
    def test_initial_state(self):
        q = QubitState()
        assert q.alpha == complex(1, 0)
        assert q.beta == complex(0, 0)

    def test_probability(self):
        q = QubitState()
        assert q.probability_zero() == 1.0
        assert q.probability_one() == 0.0

    def test_measure(self):
        q = QubitState()
        result = q.measure()
        assert result in (0, 1)

    def test_normalize(self):
        q = QubitState(alpha=complex(3, 0), beta=complex(4, 0))
        q.normalize()
        total = q.probability_zero() + q.probability_one()
        assert abs(total - 1.0) < 1e-6


class TestQuantumCircuit:
    def test_initialize(self):
        qc = QuantumCircuit()
        qc.initialize(3)
        assert qc.n_qubits == 3
        assert len(qc.qubits) == 3
        assert qc.depth == 0

    def test_hadamard(self):
        qc = QuantumCircuit()
        qc.initialize(2)
        qc.hadamard(0)
        assert qc.depth == 1

    def test_cnot(self):
        qc = QuantumCircuit()
        qc.initialize(2)
        qc.cnot(0, 1)
        assert qc.depth == 1

    def test_rotate_y(self):
        qc = QuantumCircuit()
        qc.initialize(1)
        qc.rotate_y(0, 3.14)
        assert qc.depth == 1

    def test_measure_all(self):
        qc = QuantumCircuit()
        qc.initialize(3)
        results = qc.measure_all()
        assert len(results) == 3
        assert all(r in (0, 1) for r in results)


class TestQuantumOptimizer:
    def test_create_optimizer(self):
        opt = QuantumOptimizer()
        assert opt is not None

    def test_optimize(self):
        opt = QuantumOptimizer()
        def cost_fn(params):
            return sum(p ** 2 for p in params)
        best_params, best_cost = opt.optimize(cost_fn, n_params=3, n_iterations=10, n_qubits=4)
        assert isinstance(best_params, list)
        assert isinstance(best_cost, float)
        assert best_cost < 100  # Should converge toward 0


class TestUsageGovernor:
    def test_can_execute(self):
        gov = UsageGovernor(max_tasks_per_hour=10, max_burst=3)
        assert gov.can_execute() is True

    def test_record_task(self):
        gov = UsageGovernor(max_tasks_per_hour=10, max_burst=3)
        gov.record_task()
        stats = gov.get_usage_stats()
        assert stats["total_tasks"] == 1

    def test_get_usage_stats(self):
        gov = UsageGovernor(max_tasks_per_hour=10, max_burst=3)
        stats = gov.get_usage_stats()
        assert "tasks_this_hour" in stats
        assert "can_execute" in stats


class TestQuantumEngine:
    @pytest.fixture
    def engine(self):
        return QuantumEngine.get_instance()

    def test_singleton(self):
        a = QuantumEngine.get_instance()
        b = QuantumEngine.get_instance()
        assert a is b

    @pytest.mark.asyncio
    async def test_initialize(self, engine):
        await engine.initialize()
        assert engine._initialized is True

    @pytest.mark.asyncio
    async def test_get_state(self, engine):
        await engine.initialize()
        state = engine.get_state()
        assert isinstance(state, dict)
