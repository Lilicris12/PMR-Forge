"""
PMR Forge - Physics Generator
Generates physics configurations for PMR cars
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class PhysicsParameters:
    """Physics parameters for a car"""
    mass: float = 1000.0
    inertia: Dict[str, float] = field(default_factory=lambda: {"x": 1.0, "y": 1.0, "z": 1.0})
    center_of_mass: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})
    
    # Aerodynamics
    drag_coefficient: float = 0.3
    lift_coefficient: float = -0.5
    front_area: float = 2.0
    rear_wing: float = 0.5
    
    # Suspension
    front_spring_rate: float = 100000.0
    front_damping: float = 10000.0
    front_travel: float = 0.2
    front_anti_roll_bar: float = 50000.0
    
    rear_spring_rate: float = 120000.0
    rear_damping: float = 12000.0
    rear_travel: float = 0.2
    rear_anti_roll_bar: float = 60000.0
    
    # Wheels
    front_wheel_radius: float = 0.3
    front_wheel_width: float = 0.25
    front_wheel_pressure: float = 2.0
    
    rear_wheel_radius: float = 0.35
    rear_wheel_width: float = 0.3
    rear_wheel_pressure: float = 1.8
    
    # Engine
    max_power: float = 400.0
    max_rpm: float = 7500.0
    idle_rpm: float = 1000.0
    torque_curve: list = field(default_factory=lambda: [0.0, 0.5, 0.8, 1.0, 0.9, 0.7])
    
    # Transmission
    gear_ratios: list = field(default_factory=lambda: [3.5, 2.5, 2.0, 1.7, 1.5, 1.3, 1.0])
    final_drive: float = 4.0
    shift_time: float = 0.1
    
    # Brakes
    front_brake_torque: float = 2500.0
    rear_brake_torque: float = 2000.0
    brake_bias: float = 0.6
    
    # Drivetrain
    drivetrain_type: str = "RWD"
    front_bias: float = 0.0
    rear_bias: float = 1.0


class PhysicsGenerator:
    """Generates physics configurations for PMR cars"""
    
    # Physics presets for different car types
    PRESETS = {
        "default": {
            "mass": 1200.0,
            "inertia": {"x": 1.0, "y": 1.0, "z": 1.0},
            "center_of_mass": {"x": 0.0, "y": 0.0, "z": -0.1},
            "drag_coefficient": 0.3,
            "lift_coefficient": -0.5,
            "front_area": 2.0,
            "rear_wing": 0.5,
            "front_spring_rate": 100000.0,
            "front_damping": 10000.0,
            "front_travel": 0.2,
            "front_anti_roll_bar": 50000.0,
            "rear_spring_rate": 120000.0,
            "rear_damping": 12000.0,
            "rear_travel": 0.2,
            "rear_anti_roll_bar": 60000.0,
            "front_wheel_radius": 0.3,
            "front_wheel_width": 0.25,
            "front_wheel_pressure": 2.0,
            "rear_wheel_radius": 0.35,
            "rear_wheel_width": 0.3,
            "rear_wheel_pressure": 1.8,
            "max_power": 400.0,
            "max_rpm": 7500.0,
            "idle_rpm": 1000.0,
            "torque_curve": [0.0, 0.5, 0.8, 1.0, 0.9, 0.7],
            "gear_ratios": [3.5, 2.5, 2.0, 1.7, 1.5, 1.3, 1.0],
            "final_drive": 4.0,
            "shift_time": 0.1,
            "front_brake_torque": 2500.0,
            "rear_brake_torque": 2000.0,
            "brake_bias": 0.6,
            "drivetrain_type": "RWD",
            "front_bias": 0.0,
            "rear_bias": 1.0
        },
        "gt3": {
            "mass": 1250.0,
            "inertia": {"x": 1.1, "y": 1.1, "z": 0.9},
            "center_of_mass": {"x": 0.0, "y": 0.0, "z": -0.08},
            "drag_coefficient": 0.35,
            "lift_coefficient": -0.8,
            "front_area": 1.9,
            "rear_wing": 0.8,
            "front_spring_rate": 140000.0,
            "front_damping": 14000.0,
            "front_travel": 0.15,
            "front_anti_roll_bar": 70000.0,
            "rear_spring_rate": 160000.0,
            "rear_damping": 16000.0,
            "rear_travel": 0.15,
            "rear_anti_roll_bar": 80000.0,
            "front_wheel_radius": 0.32,
            "front_wheel_width": 0.28,
            "front_wheel_pressure": 2.1,
            "rear_wheel_radius": 0.36,
            "rear_wheel_width": 0.32,
            "rear_wheel_pressure": 1.9,
            "max_power": 550.0,
            "max_rpm": 8500.0,
            "idle_rpm": 1000.0,
            "torque_curve": [0.0, 0.5, 0.85, 1.0, 0.98, 0.9],
            "gear_ratios": [3.2, 2.4, 1.9, 1.6, 1.4, 1.2, 1.0],
            "final_drive": 4.2,
            "shift_time": 0.08,
            "front_brake_torque": 3500.0,
            "rear_brake_torque": 2500.0,
            "brake_bias": 0.65,
            "drivetrain_type": "RWD",
            "front_bias": 0.0,
            "rear_bias": 1.0
        },
        "gt4": {
            "mass": 1100.0,
            "inertia": {"x": 0.95, "y": 0.95, "z": 0.85},
            "center_of_mass": {"x": 0.0, "y": 0.0, "z": -0.09},
            "drag_coefficient": 0.32,
            "lift_coefficient": -0.6,
            "front_area": 1.8,
            "rear_wing": 0.6,
            "front_spring_rate": 120000.0,
            "front_damping": 12000.0,
            "front_travel": 0.18,
            "front_anti_roll_bar": 60000.0,
            "rear_spring_rate": 140000.0,
            "rear_damping": 14000.0,
            "rear_travel": 0.18,
            "rear_anti_roll_bar": 70000.0,
            "front_wheel_radius": 0.31,
            "front_wheel_width": 0.26,
            "front_wheel_pressure": 2.0,
            "rear_wheel_radius": 0.35,
            "rear_wheel_width": 0.3,
            "rear_wheel_pressure": 1.8,
            "max_power": 450.0,
            "max_rpm": 8000.0,
            "idle_rpm": 1000.0,
            "torque_curve": [0.0, 0.5, 0.8, 1.0, 0.95, 0.85],
            "gear_ratios": [3.4, 2.5, 2.0, 1.7, 1.5, 1.3, 1.0],
            "final_drive": 4.1,
            "shift_time": 0.1,
            "front_brake_torque": 3000.0,
            "rear_brake_torque": 2200.0,
            "brake_bias": 0.62,
            "drivetrain_type": "RWD",
            "front_bias": 0.0,
            "rear_bias": 1.0
        },
        "formula": {
            "mass": 600.0,
            "inertia": {"x": 0.6, "y": 0.6, "z": 0.4},
            "center_of_mass": {"x": 0.0, "y": 0.0, "z": -0.05},
            "drag_coefficient": 0.4,
            "lift_coefficient": -1.5,
            "front_area": 1.5,
            "rear_wing": 1.2,
            "front_spring_rate": 200000.0,
            "front_damping": 20000.0,
            "front_travel": 0.1,
            "front_anti_roll_bar": 100000.0,
            "rear_spring_rate": 220000.0,
            "rear_damping": 22000.0,
            "rear_travel": 0.1,
            "rear_anti_roll_bar": 110000.0,
            "front_wheel_radius": 0.35,
            "front_wheel_width": 0.2,
            "front_wheel_pressure": 1.8,
            "rear_wheel_radius": 0.4,
            "rear_wheel_width": 0.25,
            "rear_wheel_pressure": 1.6,
            "max_power": 800.0,
            "max_rpm": 15000.0,
            "idle_rpm": 2000.0,
            "torque_curve": [0.0, 0.4, 0.7, 0.9, 1.0, 0.95, 0.85],
            "gear_ratios": [2.8, 2.2, 1.8, 1.5, 1.3, 1.1, 1.0],
            "final_drive": 3.5,
            "shift_time": 0.05,
            "front_brake_torque": 4000.0,
            "rear_brake_torque": 2000.0,
            "brake_bias": 0.7,
            "drivetrain_type": "RWD",
            "front_bias": 0.0,
            "rear_bias": 1.0
        },
        "rally": {
            "mass": 1300.0,
            "inertia": {"x": 1.3, "y": 1.3, "z": 1.2},
            "center_of_mass": {"x": 0.0, "y": 0.0, "z": -0.15},
            "drag_coefficient": 0.4,
            "lift_coefficient": -0.3,
            "front_area": 2.2,
            "rear_wing": 0.3,
            "front_spring_rate": 80000.0,
            "front_damping": 8000.0,
            "front_travel": 0.25,
            "front_anti_roll_bar": 40000.0,
            "rear_spring_rate": 100000.0,
            "rear_damping": 10000.0,
            "rear_travel": 0.25,
            "rear_anti_roll_bar": 50000.0,
            "front_wheel_radius": 0.34,
            "front_wheel_width": 0.28,
            "front_wheel_pressure": 1.8,
            "rear_wheel_radius": 0.34,
            "rear_wheel_width": 0.28,
            "rear_wheel_pressure": 1.8,
            "max_power": 350.0,
            "max_rpm": 7000.0,
            "idle_rpm": 1000.0,
            "torque_curve": [0.0, 0.6, 0.9, 1.0, 0.95, 0.85],
            "gear_ratios": [4.0, 3.0, 2.5, 2.0, 1.7, 1.5, 1.0],
            "final_drive": 4.5,
            "shift_time": 0.15,
            "front_brake_torque": 2000.0,
            "rear_brake_torque": 1800.0,
            "brake_bias": 0.55,
            "drivetrain_type": "AWD",
            "front_bias": 0.5,
            "rear_bias": 0.5
        }
    }
    
    def __init__(self, context):
        """
        Initialize the physics generator
        
        Args:
            context: ConversionContext from the pipeline
        """
        self.context = context
        self.source_dir = context.temp_dir / "source"
        self.output_dir = context.temp_dir / "converted"
        
        logger.info("Initialized PhysicsGenerator")
    
    def generate(self) -> Optional[Path]:
        """
        Generate physics configuration
        
        Returns:
            Path to the generated physics file, or None if failed
        """
        self._log("Generating physics configuration...")
        
        # Get preset or use default
        preset = self.context.options.physics_preset.lower()
        preset_data = self.PRESETS.get(preset, self.PRESETS["default"])
        
        # Create physics parameters
        params = PhysicsParameters(**preset_data)
        
        # Apply scale factor to certain parameters
        scale = self.context.options.scale_factor
        if scale != 1.0:
            params.mass *= scale ** 3  # Mass scales with volume
            params.front_wheel_radius *= scale
            params.rear_wheel_radius *= scale
            params.front_wheel_width *= scale
            params.rear_wheel_width *= scale
            
            # Adjust suspension based on scale
            params.front_spring_rate /= scale
            params.rear_spring_rate /= scale
        
        # Convert to PMR physics format
        pmr_physics = self._to_pmr_format(params)
        
        # Create physics directory
        physics_dir = self.output_dir / "physics"
        physics_dir.mkdir(parents=True, exist_ok=True)
        
        # Save physics configuration
        physics_file = physics_dir / "physics.json"
        self._write_json(physics_file, pmr_physics)
        
        self._log(f"Physics configuration saved to {physics_file}")
        return physics_file
    
    def _to_pmr_format(self, params: PhysicsParameters) -> Dict[str, Any]:
        """Convert physics parameters to PMR format"""
        return {
            "mass": params.mass,
            "inertia": params.inertia,
            "center_of_mass": params.center_of_mass,
            "aerodynamics": {
                "drag_coefficient": params.drag_coefficient,
                "lift_coefficient": params.lift_coefficient,
                "front_area": params.front_area,
                "rear_wing": params.rear_wing
            },
            "suspension": {
                "front": {
                    "spring_rate": params.front_spring_rate,
                    "damping": params.front_damping,
                    "travel": params.front_travel,
                    "anti_roll_bar": params.front_anti_roll_bar
                },
                "rear": {
                    "spring_rate": params.rear_spring_rate,
                    "damping": params.rear_damping,
                    "travel": params.rear_travel,
                    "anti_roll_bar": params.rear_anti_roll_bar
                }
            },
            "wheels": {
                "front": {
                    "radius": params.front_wheel_radius,
                    "width": params.front_wheel_width,
                    "pressure": params.front_wheel_pressure
                },
                "rear": {
                    "radius": params.rear_wheel_radius,
                    "width": params.rear_wheel_width,
                    "pressure": params.rear_wheel_pressure
                }
            },
            "engine": {
                "max_power": params.max_power,
                "max_rpm": params.max_rpm,
                "idle_rpm": params.idle_rpm,
                "torque_curve": params.torque_curve
            },
            "transmission": {
                "gear_ratios": params.gear_ratios,
                "final_drive": params.final_drive,
                "shift_time": params.shift_time
            },
            "brakes": {
                "front": {
                    "max_torque": params.front_brake_torque,
                    "bias": params.brake_bias
                },
                "rear": {
                    "max_torque": params.rear_brake_torque,
                    "bias": 1.0 - params.brake_bias
                }
            },
            "drivetrain": {
                "type": params.drivetrain_type,
                "front_bias": params.front_bias,
                "rear_bias": params.rear_bias,
                "differential": self._get_differential(params.drivetrain_type)
            }
        }
    
    def _get_differential(self, drivetrain_type: str) -> Dict[str, Any]:
        """Get differential settings based on drivetrain type"""
        if drivetrain_type == "AWD":
            return {
                "front": {"type": "LSD", "lock": 0.6},
                "rear": {"type": "LSD", "lock": 0.7},
                "center": {"type": "OPEN", "lock": 0.0}
            }
        elif drivetrain_type == "FWD":
            return {
                "front": {"type": "OPEN", "lock": 0.0},
                "rear": {"type": "NONE", "lock": 0.0},
                "center": {"type": "NONE", "lock": 0.0}
            }
        else:  # RWD or default
            return {
                "front": {"type": "NONE", "lock": 0.0},
                "rear": {"type": "LSD", "lock": 0.7},
                "center": {"type": "NONE", "lock": 0.0}
            }
    
    def _log(self, message: str):
        """Log a message"""
        logger.info(f"[PhysicsGenerator] {message}")
        self.context.log_messages.append(f"[PhysicsGenerator] {message}")
        print(f"[PhysicsGenerator] {message}")
    
    def _write_json(self, path: Path, data: Dict[str, Any]):
        """Write JSON data to a file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
