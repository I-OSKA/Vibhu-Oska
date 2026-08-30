"""
Vibhu-Oska AI-OS — GRPO (Group Relative Policy Optimization)
Implementation of the GRPO algorithm for RL self-improvement.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from typing import Optional


class GRPO:
    """
    Group Relative Policy Optimization.

    GRPO computes advantages relative to a group of rollouts,
    eliminating the need for a separate critic network.

    Algorithm:
    1. Collect N rollouts per prompt
    2. Score each rollout
    3. Compute group-normalized advantages
    4. Update policy with clipped surrogate objective
    """

    def __init__(
        self,
        clip_ratio: float = 0.2,
        learning_rate: float = 1e-5,
        entropy_coeff: float = 0.01,
        value_coeff: float = 0.5,
    ) -> None:
        self._clip_ratio = clip_ratio
        self._learning_rate = learning_rate
        self._entropy_coeff = entropy_coeff
        self._value_coeff = value_coeff
        self._update_count: int = 0

    @property
    def update_count(self) -> int:
        return self._update_count

    def compute_advantages(
        self,
        rewards: torch.Tensor,
        eps: float = 1e-8,
    ) -> torch.Tensor:
        """
        Compute group-relative advantages.

        advantage = (reward - mean) / (std + eps)
        """
        if rewards.numel() < 2:
            return torch.zeros_like(rewards)

        mean_r = rewards.mean()
        std_r = rewards.std()
        advantages = (rewards - mean_r) / (std_r + eps)
        return advantages

    def compute_ratio(
        self,
        old_logprobs: torch.Tensor,
        new_logprobs: torch.Tensor,
    ) -> torch.Tensor:
        """Compute probability ratio: pi_new / pi_old."""
        log_ratio = new_logprobs - old_logprobs
        ratio = torch.exp(log_ratio)
        return ratio

    def clipped_surrogate_loss(
        self,
        ratio: torch.Tensor,
        advantages: torch.Tensor,
        clip_ratio: Optional[float] = None,
    ) -> torch.Tensor:
        """
        Compute clipped surrogate objective.

        L = -E[min(ratio * A, clip(ratio, 1-eps, 1+eps) * A)]
        """
        clip = clip_ratio or self._clip_ratio

        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - clip, 1 + clip) * advantages

        loss = -torch.min(surr1, surr2)
        return loss.mean()

    def entropy_bonus(self, logits: torch.Tensor) -> torch.Tensor:
        """Compute entropy bonus for exploration."""
        probs = F.softmax(logits, dim=-1)
        log_probs = F.log_softmax(logits, dim=-1)
        entropy = -(probs * log_probs).sum(dim=-1).mean()
        return entropy

    def update(
        self,
        old_logprobs: torch.Tensor,
        new_logprobs: torch.Tensor,
        rewards: torch.Tensor,
        logits: Optional[torch.Tensor] = None,
    ) -> dict[str, float]:
        """
        Perform a single GRPO update step.

        Returns loss metrics.
        """
        # 1. Compute advantages
        advantages = self.compute_advantages(rewards)

        # 2. Compute ratio
        ratio = self.compute_ratio(old_logprobs, new_logprobs)

        # 3. Clipped surrogate loss
        policy_loss = self.clipped_surrogate_loss(ratio, advantages)

        # 4. Entropy bonus
        entropy_loss = torch.tensor(0.0)
        if logits is not None:
            entropy_loss = -self._entropy_coeff * self.entropy_bonus(logits)

        # 5. Total loss
        total_loss = policy_loss + entropy_loss

        # 6. Metrics
        with torch.no_grad():
            approx_kl = (torch.log(ratio)).mean().item()
            clip_frac = ((ratio - 1).abs() > self._clip_ratio).float().mean().item()

        self._update_count += 1

        return {
            "total_loss": total_loss.item(),
            "policy_loss": policy_loss.item(),
            "entropy_loss": entropy_loss.item(),
            "approx_kl": approx_kl,
            "clip_fraction": clip_frac,
            "mean_advantage": advantages.mean().item(),
            "mean_reward": rewards.mean().item(),
            "update_count": self._update_count,
        }

    def compute_returns(
        self,
        rewards: list[float],
        gamma: float = 0.99,
    ) -> list[float]:
        """Compute discounted returns (for multi-step rollouts)."""
        returns = []
        R = 0.0
        for r in reversed(rewards):
            R = r + gamma * R
            returns.insert(0, R)
        return returns
