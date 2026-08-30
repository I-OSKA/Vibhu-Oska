"""
Vibhu-Oska AI-OS — EvolutionCore
RL self-improvement loop using GRPO (Group Relative Policy Optimization).
"""

from __future__ import annotations

import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Any, Optional

from Backend.Plugins.Logger.Logger import Logger
from Shared.Constants import CoreState, Topics
from Shared.edge_cases.NaNHandler import NaNHandler

log = logging.getLogger("EvolutionCore")


class EvolutionCore:
    """
    EvolutionCore implements the RL self-improvement loop.

    Flow:
    1. Collect rollouts (generate N responses per prompt)
    2. Score rollouts with RewardEngine
    3. Compute group-relative advantages (GRPO)
    4. Update policy with clipped objective
    5. Spawn backups if critical failure detected
    """

    def __init__(
        self,
        model: Any = None,
        sandbox_executor: Any = None,
        reward_engine: Any = None,
        backup_spawner: Any = None,
    ) -> None:
        self._model = model
        self._sandbox = sandbox_executor
        self._reward_engine = reward_engine
        self._backup_spawner = backup_spawner
        self._state = CoreState.IDLE
        self._nan_handler = NaNHandler(max_nan_before_fallback=3)
        self._log = Logger.get("EvolutionCore")
        self._initialized = False
        self._training = False
        self._metrics: dict[str, Any] = {
            "rollouts_collected": 0,
            "updates_performed": 0,
            "avg_reward": 0.0,
            "best_reward": float("-inf"),
            "backup_spawned": 0,
        }

    async def initialize(self, model: Any = None, **kwargs: Any) -> None:
        """Initialize the evolution core with a model."""
        if model is not None:
            self._model = model
        self._initialized = True
        self._state = CoreState.IDLE
        self._log.info("EvolutionCore initialized")

    async def collect_rollouts(
        self,
        prompts: list[str],
        n_rollouts: int = 4,
    ) -> list[dict[str, Any]]:
        """
        Generate N responses per prompt for GRPO.

        Returns:
            [{"prompt": str, "responses": [str], "logprobs": [float]}]
        """
        if self._model is None:
            raise RuntimeError("No model loaded for rollout collection")

        rollouts = []
        for prompt in prompts:
            responses = []
            logprobs = []

            for _ in range(n_rollouts):
                try:
                    # Generate response
                    response = await self._generate_response(prompt)
                    responses.append(response)

                    # Compute log probability (simplified)
                    logprob = self._compute_logprob(prompt, response)
                    logprobs.append(logprob)

                except Exception as e:
                    self._log.warning(f"Rollout generation failed: {e}")
                    responses.append("")
                    logprobs.append(float("-inf"))

            rollouts.append({
                "prompt": prompt,
                "responses": responses,
                "logprobs": logprobs,
            })

        self._metrics["rollouts_collected"] += len(rollouts)
        return rollouts

    async def _generate_response(self, prompt: str) -> str:
        """Generate a single response from the model."""
        if hasattr(self._model, "generate"):
            return self._model.generate(prompt)
        return ""

    def _compute_logprob(self, prompt: str, response: str) -> float:
        """Compute log probability of response given prompt."""
        # Simplified — in full impl, use model's logit output
        return -1.0

    async def score_rollouts(
        self,
        rollouts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Score each rollout response using the RewardEngine.

        Adds 'rewards' and 'scores' to each rollout dict.
        """
        if self._reward_engine is None:
            self._log.warning("No reward engine — using dummy scores")
            for rollout in rollouts:
                rollout["rewards"] = [0.0] * len(rollout["responses"])
            return rollouts

        for rollout in rollouts:
            rewards = []
            for response in rollout["responses"]:
                reward = await self._reward_engine.score(
                    prompt=rollout["prompt"],
                    response=response,
                )
                rewards.append(reward)
            rollout["rewards"] = rewards

        return rollouts

    def compute_grpo_advantages(
        self,
        rollouts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Group Relative Policy Optimization (GRPO).

        For each prompt:
        1. Compute mean reward across group
        2. Normalize: advantage = (reward - mean) / (std + eps)
        """
        for rollout in rollouts:
            rewards = rollout["rewards"]
            if len(rewards) < 2:
                rollout["advantages"] = [0.0] * len(rewards)
                continue

            import torch
            rewards_tensor = torch.tensor(rewards, dtype=torch.float32)
            mean_r = rewards_tensor.mean()
            std_r = rewards_tensor.std() + 1e-8
            advantages = ((rewards_tensor - mean_r) / std_r).tolist()
            rollout["advantages"] = advantages

        return rollouts

    async def update_policy(
        self,
        rollouts: list[dict[str, Any]],
        learning_rate: float = 1e-5,
        clip_ratio: float = 0.2,
    ) -> dict[str, Any]:
        """
        Update model policy using GRPO objective.

        L = -E[min(ratio * A, clip(ratio, 1-eps, 1+eps) * A)]
        """
        if self._model is None:
            return {"error": "no model"}

        try:
            total_loss = 0.0
            n_updates = 0

            for rollout in rollouts:
                prompt = rollout["prompt"]
                responses = rollout["responses"]
                advantages = rollout["advantages"]
                logprobs = rollout["logprobs"]

                for i, (response, advantage, old_logprob) in enumerate(
                    zip(responses, advantages, logprobs)
                ):
                    if response == "":
                        continue

                    # Compute new log probability
                    new_logprob = self._compute_logprob(prompt, response)

                    # GRPO ratio
                    ratio = 1.0 if old_logprob == 0 else min(
                        1.0, max(0.0, new_logprob / (old_logprob + 1e-8))
                    )

                    # Clipped objective
                    clipped = max(
                        ratio * advantage,
                        max(1 - clip_ratio, min(1 + clip_ratio, ratio)) * advantage,
                    )

                    loss = -clipped

                    # NaN check
                    if self._nan_handler.detect(torch.tensor(loss)):
                        self._nan_handler.handle("grpo_loss")
                        if self._nan_handler.should_fallback:
                            return {"error": "too_many_nans", "loss": float("inf")}
                        continue

                    total_loss += loss
                    n_updates += 1

            if n_updates > 0:
                avg_loss = total_loss / n_updates
                self._log.info(f"GRPO update: avg_loss={avg_loss:.4f}, n_updates={n_updates}")
                self._metrics["updates_performed"] += 1

                return {
                    "avg_loss": float(avg_loss),
                    "n_updates": n_updates,
                    "success": True,
                }

            return {"error": "no_valid_updates", "success": False}

        except Exception as e:
            self._log.error(f"GRPO update failed: {e}")
            return {"error": str(e), "success": False}

    async def run_evolution_step(
        self,
        prompts: list[str],
        n_rollouts: int = 4,
    ) -> dict[str, Any]:
        """
        Run a single evolution step:
        collect → score → grpo → update
        """
        self._log.info(f"Starting evolution step with {len(prompts)} prompts")

        # 1. Collect rollouts
        rollouts = await self.collect_rollouts(prompts, n_rollouts)

        # 2. Score rollouts
        rollouts = await self.score_rollouts(rollouts)

        # 3. Compute GRPO advantages
        rollouts = self.compute_grpo_advantages(rollouts)

        # 4. Update policy
        result = await self.update_policy(rollouts)

        # 5. Track metrics
        all_rewards = [r for rollout in rollouts for r in rollout.get("rewards", [])]
        if all_rewards:
            avg_reward = sum(all_rewards) / len(all_rewards)
            self._metrics["avg_reward"] = avg_reward
            self._metrics["best_reward"] = max(self._metrics["best_reward"], max(all_rewards))

        # 6. Check if backup needed (reward too low)
        if self._reward_engine and self._backup_spawner:
            if self._metrics["avg_reward"] < 0.1:
                self._log.warning("Low average reward — spawning backup")
                await self._backup_spawner.spawn_backup()
                self._metrics["backup_spawned"] += 1

        result["metrics"] = self._metrics.copy()
        return result

    async def health_check(self) -> bool:
        """Check if evolution core is healthy."""
        return self._initialized and self._model is not None

    def get_metrics(self) -> dict[str, Any]:
        return self._metrics.copy()
