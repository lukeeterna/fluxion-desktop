"""
Fluxion VAD Module
==================

Professional Voice Activity Detection for Fluxion Voice Agent.
Uses ten-vad library (standalone, NO cloud dependencies).
"""

from .ten_vad_integration import (
    FluxionVAD,
    VADConfig,
    VADResult,
    VADState,
    create_vad,
)

from .vad_pipeline_integration import (
    VADPipelineManager,
    TurnConfig,
    TurnResult,
    create_vad_pipeline_manager,
)

__all__ = [
    # Core VAD
    "FluxionVAD",
    "VADConfig",
    "VADResult",
    "VADState",
    "create_vad",
    # Pipeline Integration
    "VADPipelineManager",
    "TurnConfig",
    "TurnResult",
    "create_vad_pipeline_manager",
]
