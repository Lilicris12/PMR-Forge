"""
PMR Forge - Automobilista 1 Converter
Converter for Automobilista 1 car models
"""

from pathlib import Path
from typing import Dict, Any
from .base_converter import BaseModelConverter
import logging
import shutil
import json

logger = logging.getLogger(__name__)


class Automobilista1Converter(BaseModelConverter):
    """Converter for Automobilista 1 car models"""
    
    def __init__(self, context):
        super().__init__(context)
        self.car_data = {}
        self.physics_data = {}
        self.setup_data = {}
    
    def convert(self):
        """Convert Automobilista 1 car to PMR format"""
        self._log("Starting Automobilista 1 conversion")
        
        # Step 1: Parse AMS1 files
        self._parse_ams1_files()
        
        # Step 2: Convert model
        self._convert_model_files()
        
        # Step 3: Convert textures
        self._convert_textures()
        
        # Step 4: Convert physics
        self._convert_physics()
        
        # Step 5: Create PMR-specific files
        self._create_pmr_files()
        
        self._log("Automobilista 1 conversion complete")
    
    def _parse_ams1_files(self):
        """Parse Automobilista 1 specific files"""
        self._log("Parsing Automobilista 1 files...")
        
        # Parse vehicle.ini
        vehicle_ini = self._find_file("vehicle.ini")
        if vehicle_ini:
            self.car_data = self._parse_ini_file(vehicle_ini)
            self._log(f"Found vehicle data: {list(self.car_data.keys())}")
        
        # Parse setup.ini
        setup_ini = self._find_file("setup.ini")
        if setup_ini:
            self.setup_data = self._parse_ini_file(setup_ini)
            self._log(f"Found setup data: {list(self.setup_data.keys())}")
        
        # Parse physics.ini
        physics_ini = self._find_file("physics.ini")
        if physics_ini:
            self.physics_data = self._parse_ini_file(physics_ini)
            self._log(f"Found physics data: {list(self.physics_data.keys())}")
        
        # Parse .ams file (AMS1 car definition)
        ams_file = self._find_file("*.ams")
        if ams_file:
            ams_data = self._parse_ams_file(ams_file)
            self._log(f"Found AMS data: {list(ams_data.keys())}")
    
    def _parse_ams_file(self, path: Path) -> Dict[str, Any]:
        """Parse Automobilista 1 .ams file"""
        # .ams files are binary
        # In a real implementation, we'd use a proper parser
        data = {}
        
        try:
            content = self._read_text_file(path)
            if content:
                data['content'] = content[:200] + "..."
        except Exception as e:
            self._log(f"Error parsing .ams file: {e}")
        
        return data
    
    def _convert_model_files(self):
        """Convert AMS1 model files"""
        self._log("Converting model files...")
        
        # AMS1 uses .ams files or .fbx/.obj
        model_files = self._find_files(['.ams', '.fbx', '.obj', '.glb'])
        
        if not model_files:
            self._log("Warning: No model files found!")
            return
        
        for model_file in model_files:
            if model_file.suffix.lower() == '.ams':
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
        """Convert AMS1 textures"""
        self._log("Converting textures...")
        
        # AMS1 uses .dds files for textures
        texture_files = self._find_files(['.dds', '.png', '.jpg', '.jpeg', '.tga'])
        
        texture_dir = self.output_dir / "textures"
        texture_dir.mkdir(parents=True, exist_ok=True)
        
        for tex_file in texture_files:
            # Convert DDS to PNG if requested
            if tex_file.suffix.lower() == '.dds' and self.context.options.convert_textures:
                dest = texture_dir / f"{tex_file.stem}.png"
                self._copy_file(tex_file, dest)
            else:
                dest = texture_dir / tex_file.name
                self._copy_file(tex_file, dest)
    
    def _convert_physics(self):
        """Convert AMS1 physics to PMR format"""
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
        physics_files = self._find_files(['.ini', '.txt'])
        physics_files = [f for f in physics_files if 'physics' in f.name.lower() or 'setup' in f.name.lower()]
        
        for pf in physics_files:
            dest = physics_dir / pf.name
            self._copy_file(pf, dest)
    
    def _convert_physics_data(self) -> Dict[str, Any]:
        """Convert AMS1 physics data to PMR format"""
        # Default PMR physics structure with AMS1-style defaults
        # AMS1 is based on GTR2, so similar physics
        pmr_physics = {
            "mass": 1050.0,
            "inertia": {
                "x": 1.15,
                "y": 1.15,
                "z": 0.95
            },
            "center_of_mass": {
                "x": 0.0,
                "y": 0.0,
                "z": -0.08
            },
            "aerodynamics": {
                "drag_coefficient": 0.34,
                "lift_coefficient": -0.65,
                "front_area": 1.95,
                "rear_wing": 0.65
            },
            "suspension": {
                "front": {
                    "spring_rate": 130000.0,
                    "damping": 13000.0,
                    "travel": 0.19,
                    "anti_roll_bar": 65000.0
                },
                "rear": {
                    "spring_rate": 150000.0,
                    "damping": 15000.0,
                    "travel": 0.19,
                    "anti_roll_bar": 75000.0
                }
            },
            "wheels": {
                "front": {
                    "radius": 0.325,
                    "width": 0.285,
                    "pressure": 2.25
                },
                "rear": {
                    "radius": 0.365,
                    "width": 0.315,
                    "pressure": 2.05
                }
            },
            "engine": {
                "max_power": 575.0,
                "max_rpm": 8800.0,
                "idle_rpm": 1050.0,
                "torque_curve": [0.0, 0.52, 0.88, 1.0, 0.96, 0.82]
            },
            "transmission": {
                "gear_ratios": [3.1, 2.3, 1.9, 1.6, 1.4, 1.2, 1.0],
                "final_drive": 4.3,
                "shift_time": 0.075
            },
            "brakes": {
                "front": {
                    "max_torque": 3750.0,
                    "bias": 0.63
                },
                "rear": {
                    "max_torque": 2750.0,
                    "bias": 0.37
                }
            },
            "drivetrain": {
                "type": "AWD",
                "front_bias": 0.42,
                "rear_bias": 0.58,
                "differential": {
                    "front": {"type": "LSD", "lock": 0.55},
                    "rear": {"type": "LSD", "lock": 0.65},
                    "center": {"type": "OPEN", "lock": 0.0}
                }
            }
        }
        
        # Try to extract values from AMS1 data
        if self.car_data:
            # Extract from [VEHICLE] section
            vehicle_section = self.car_data.get('VEHICLE', {})
            
            # Mass
            if 'MASS' in vehicle_section:
                try:
                    pmr_physics['mass'] = float(vehicle_section['MASS'])
                except ValueError:
                    pass
        
        if self.setup_data:
            # Extract from [SETUP] section
            setup_section = self.setup_data.get('SETUP', {})
            
            # Center of mass
            if 'CM_POSITION' in setup_section:
                try:
                    parts = setup_section['CM_POSITION'].split(',')
                    if len(parts) >= 3:
                        pmr_physics['center_of_mass'] = {
                            'x': float(parts[0]),
                            'y': float(parts[1]),
                            'z': float(parts[2])
                        }
                except (ValueError, IndexError):
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
            "description": f"Converted from Automobilista 1",
            "type": "car",
            "tags": ["converted", "automobilista-1", "ams1"],
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
        """Extract car name from AMS1 data"""
        if self.car_data:
            # Try to get name from [VEHICLE] section
            vehicle_section = self.car_data.get('VEHICLE', {})
            if 'NAME' in vehicle_section:
                return vehicle_section['NAME']
            if 'CarName' in vehicle_section:
                return vehicle_section['CarName']
        
        return self.context.options.mod_name
