from dataclasses import dataclass


@dataclass
class IoLoopMonitorState:
    wall_loop_duration: float
    cpu_loop_duration: float
