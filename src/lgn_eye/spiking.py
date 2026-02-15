"""Spiking neural network accumulator using snnTorch LIF neurons.

Provides a biologically-plausible alternative to the simple EMA accumulator.
LIF (Leaky Integrate-and-Fire) neurons fire when accumulated evidence exceeds
a threshold, with membrane potential decaying exponentially between inputs.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import snntorch as snn

from lgn_eye.config import LGNConfig


class SpikingAccumulator(nn.Module):
    """Replace simple EMA with LIF neurons from snnTorch.

    Uses snntorch.Leaky for leaky integrate-and-fire dynamics.
    The spiking version produces event maps that more closely
    model biological LGN temporal dynamics:
    - Neurons fire when accumulated evidence exceeds threshold
    - Membrane potential decays exponentially between inputs
    - Refractory period prevents rapid re-firing
    """

    def __init__(self, config: LGNConfig):
        super().__init__()
        self.config = config

        # LIF neuron layer: beta controls membrane decay rate
        # Higher beta = slower decay = more temporal integration
        self.lif = snn.Leaky(
            beta=config.decay_alpha,
            threshold=config.accumulator_threshold,
            learn_beta=False,
            learn_threshold=False,
            reset_mechanism="subtract",
        )

        # Persistent membrane potential
        self.mem: torch.Tensor | None = None

    def reset(self):
        """Reset membrane potential."""
        self.mem = None

    def forward(self, abs_diff: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Process absolute temporal difference through LIF dynamics.

        Args:
            abs_diff: (B, 1, H, W) absolute temporal difference.

        Returns:
            Tuple of (spikes, membrane_potential), both (B, 1, H, W).
            - spikes: binary spike events (fires when membrane > threshold)
            - membrane_potential: continuous accumulated evidence (like motion_energy)
        """
        if self.mem is None:
            self.mem = torch.zeros_like(abs_diff)

        # LIF forward: input current -> spike output + updated membrane
        spikes, self.mem = self.lif(abs_diff, self.mem)

        return spikes, self.mem.clone()
