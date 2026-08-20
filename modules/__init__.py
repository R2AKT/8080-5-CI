"""Модули i8080-5 CI: шина памяти, устройства памяти."""
from .memory_bus import (
    MemoryBus, IOBus, MemoryRegion,
    RAMRegion, ROMRegion, ShadowROMRegion,
    BankedRegion, BankedROMRegion,
    PagedRegion, SegmentedRegion, SegmentedPagedRegion
)

"""Модули i8080-5 CI: устройства IO."""
from .io import IODevice, I8255
