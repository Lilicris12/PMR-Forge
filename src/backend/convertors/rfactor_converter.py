"""
PMR Forge - rFactor Converter
Converter for rFactor car models
"""

from pathlib import Path
from typing import Dict, Any
from .base_converter import BaseModelConverter
import logging
import shutil
import json

logger = logging.getLogger(__name__)


class RFactorConverter(BaseModelConverter):
    """Converter for rFactor car models"""
    
    def __init__(self, context):
        super().__init__(context)
        self.vehicle_data = {}
        self.physics_data = {}
    
    def convert(self):
        """Convert rFactor car to PMR format"""
        self._log("Starting rFactor conversion")
        
        # Step 1: Parse rFactor files
        self._parse_rfactor_files()
        
        # Step 2: Convert model
        self._convert_model_files()
        
        # Step 3: Convert textures
        self._convert_textures()
        
        # Step 4: Convert physics
        self._convert_physics()
        
        # Step 5: Create PMR-specific files
        self._create_pmr_files()
        
        self._log("rFactor conversion complete")
    
    def _parse_rfactor_files(self):
        """Parse rFactor specific files"""
        self._log("Parsing rFactor files...")
        
        # Parse .veh file (vehicle definition)
        veh_file = self._find_file("*.veh")
        if veh_file:
            self.vehicle_data = self._parse_veh_file(veh_file)
            self._log(f"Found vehicle data: {list(self.vehicle_data.keys())}")
        
        # Parse .gen file (physics)
        gen_file = self._find_file("*.gen")
        if gen_file:
            self.physics_data = self._parse_gen_file(gen_file)
            self._log(f"Found physics data: {list(self.physics_data.keys())}")
        
        # Parse vehicle.ini
        vehicle_ini = self._find_file("vehicle.ini")
        if vehicle_ini:
            ini_data = self._parse_ini_file(vehicle_ini)
            self._log(f"Found INI data: {list(ini_data.keys())}")
    
    def _parse_veh_file(self, path: Path) -> Dict[str, Any]:
        """Parse rFactor .veh file"""
        # .veh files are binary, but we can extract some info
        # In a real implementation, we'd use a proper parser
        data = {}
        
        try:
            content = self._read_text_file(path)
            if content:
                # Try to parse as text (some .veh files have text sections)
                lines = content.split('\n')
                for line in lines:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        data[key.strip()] = value.strip()
        except Exception as e:
            self._log(f"Error parsing .veh file: {e}")
        
        return data
    
    def _parse_gen_file(self, path: Path) -> Dict[str, Any]:
        """Parse rFactor .gen file (physics)"""
        # .gen files are also binary
        # In a real implementation, we'd use a proper parser
        data = {}
        
        try:
            # Try to read as text
            content = self._read_text_file(path)
            if content:
                # Simple parsing
                data['content'] = content[:200] + "..."  # Just store beginning
        except Exception as e:
            self._log(f"Error parsing .gen file: {e}")
        
        return data
    
    def _convert_model_files(self):
        """Convert rFactor model files"""
        self._log("Converting model files...")
        
        # rFactor uses .mas files (encrypted) or .fbx/.obj
        model_files = self._find_files(['.mas', '.fbx', '.obj', '.glb'])
        
        if not model_files:
            self._log("Warning: No model files found!")
            return
        
        for model_file in model_files:
            if model_file.suffix.lower() == '.mas':
                # Try to find corresponding .fbx or .obj
                base_name = model_file.stem
                alt_files = self._find_files_by_pattern(f"{base_name}.*")
                alt_files = [f for f in alt_files if f.suffix.lower() in ['.fbx', '.obj', '.glb']]
                
                if alt_files:
                    for alt_file in alt_files:
                        dest = self.output_dir / alt_file.name
                        self._copy_file(alt_file, dest)
                else:
                    self._log(f"Warning: No alternative model file for {model_file.name}")
            else:
                # Copy directly
                dest = self.output_dir / model_file.name
                self._copy_file(model_file, dest)
    
    def _convert_textures(self):
        """Convert rFactor textures"""
        self._log("Converting textures...")
        
        # rFactor uses .dds files for textures
        texture_files = self._find_files(['.dds', '.png', '.jpg', '.jpeg', '.tga'])
        
        texture_dir = self.output_dir / "textures"
        texture_dir.mkdir(parents=True, exist_ok=True)
        
        for tex_file in texture_files:
            # Convert DDS to PNG if requested
            if tex_file.suffix.lower() == '.dds' and self.context.options.convert_textures:
                # In a real implementation, we'd convert DDS to PNG here
                dest = texture_dir / f"{tex_file.stem}.png"
                self._copy_file(tex_file, dest)
            else:
                dest = texture_dir / tex_file.name
                self._copy_file(tex_file, dest)
    
    def _convert_physics(self):
        """Convert rFactor physics to PMR format"""
        self._log("Converting physics...")
        
        # Create physics directory
        physics_dir = self.output_dir / "physics"
        physics_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert physics data to PMR format
        pmr_physics = self._convert_physics_data()
        
        # Save as JSON for PMR
        physics_file = physics_dir / "physics.json"
        self._write_text_file(physics_file, json.dumps(pmr_physics, indent=2))
        
        # Copy other physics files
        physics_files = self._find_files(['.ini', '.txt', '.gen'])
        physics_files = [f for f in physics_files if 'physics' in f.name.lower() or 'gen' in f.name.lower()]
        
        for pf in physics_files:
            dest = physics_dir / pf.name
            self._copy_file(pf, dest)
    
    def _convert_physics_data(self) -> Dict[str, Any]:
        """Convert rFactor physics data to PMR format"""
        # Default PMR physics structure
        pmr_physics = {
            "mass": 1000.0,
            "inertia": {
                "x": 1.0,
                "y": 1.0,
                "z": 1.0
            },
            "center_of_mass": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "aerodynamics": {
                "drag_coefficient": 0.35,
                "lift_coefficient": -0.6,
                "front_area": 2.0,
                "rear_wing": 0.6
            },
            "suspension": {
                "front": {
                    "spring_rate": 120000.0,
                    "damping": 12000.0,
                    "travel": 0.2,
                    "anti_roll_bar": 60000.0
                },
                "rear": {
                    "spring_rate": 140000.0,
                    "damping": 14000.0,
                    "travel": 0.2,
                    "anti_roll_bar": 70000.0
                }
            },
            "wheels": {
                "front": {
                    "radius": 0.32,
                    "width": 0.28,
                    "pressure": 2.2
                },
                "rear": {
                    "radius": 0.36,
                    "width": 0.32,
                    "pressure": 2.0
                }
            },
            "engine": {
                "max_power": 550.0,
                "max_rpm": 8500.0,
                "idle_rpm": 1000.0,
                "torque_curve": [0.0, 0.5, 0.85, 1.0, 0.95, 0.8]
            },
            "transmission": {
                "gear_ratios": [3.2, 2.4, 1.9, 1.6, 1.4, 1.2, 1.0],
                "final_drive": 4.2,
                "shift_time": 0.08
            },
            "brakes": {
                "front": {
                    "max_torque": 3500.0,
                    "bias": 0.62
                },
                "rear": {
                    "max_torque": 2500.0,
                    "bias": 0.38
                }
            },
            "drivetrain": {
                "type": "AWD",
                "front_bias": 0.4,
                "rear_bias": 0.6,
                "differential": {
                    "front": {"type": "LSD", "lock": 0.6},
                    "rear": {"type": "LSD", "lock": 0.7},
                    "center": {"type": "OPEN", "lock": 0.0}
                }
            }
        }
        
        # Try to extract values from rFactor data
        if self.vehicle_data:
            # Extract mass
            if 'MASS' in self.vehicle_data:
                try:
                    pmr_physics['mass'] = float(self.vehicle_data['MASS'])
                except ValueError:
                    pass
        
        return pmr_physics
    
    def _create_pmr_files(self):
        """Create PMR-specific configuration files"""
        self._log("Creating PMR configuration files...")
        
        # Create mod info
        mod_info = {
            "name": self.context.options.mod_name,
            "version": self.context.options.mod_version,
            "author": self.context.options.mod_author,
            "description": f"Converted from rFactor",
            "type": "car",
            "tags": ["converted", "rfactor"],
            "compatibility": {
                "pmr_version": "1.0.0",
                "game_version": "1.0.0"
            }
        }
        
        mod_info_file = self.output_dir / "mod.json"
        self._write_text_file(mod_info_file, json.dumps(mod_info, indent=2))
        
        # Create car info
        car_info = {
            "model": {
                "file": "car.fbx",
                "scale": self.context.options.scale_factor,
                "offset": {"x": 0.0, "y": 0.0, "z": 0.0}
            },
            "textures": {
                "diffuse": "textures/diffuse.png",
                "normal": "textures/normal.png",
                "specular": "textures/specular.png"
            },
            "physics": "physics/physics.json",
            "sounds": {
                "engine": "sounds/engine.wav",
                "exhaust": "sounds/exhaust.wav"
            } if self.context.options.generate_sounds else None,
            "lods": [
                {"distance": 50.0, "file": "lod1.fbx"},
                {"distance": 100.0, "file": "lod2.fbx"}
            ] if self.context.options.create_lods else []
        }
        
        car_info_file = self.output_dir / "car.json"
        self._write_text_file(car_info_file, json.dumps(car_info, indent=2))
    
    def _extract_car_name(self) -> str:
        """Extract car name from rFactor data"""
        if self.vehicle_data:
            if 'NAME' in self.vehicle_data:
                return self.vehicle_data['NAME']
            if 'CarName' in self.vehicle_data:
                return self.vehicle_data['CarName']
        
        return self.context.options.mod_name
