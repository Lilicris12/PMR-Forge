"""
PMR Forge - Assetto Corsa Converter
Converter for Assetto Corsa car models
"""

from pathlib import Path
from typing import Dict, Any
from .base_converter import BaseModelConverter
import logging
import shutil
import json

logger = logging.getLogger(__name__)


class AssettoCorsaConverter(BaseModelConverter):
    """Converter for Assetto Corsa car models"""
    
    def __init__(self, context):
        super().__init__(context)
        self.car_data = {}
        self.model_info = {}
        self.physics_info = {}
    
    def convert(self):
        """Convert Assetto Corsa car to PMR format"""
        self._log("Starting Assetto Corsa conversion")
        
        # Step 1: Parse AC files
        self._parse_ac_files()
        
        # Step 2: Convert model
        self._convert_model_files()
        
        # Step 3: Convert textures
        self._convert_textures()
        
        # Step 4: Convert physics
        self._convert_physics()
        
        # Step 5: Create PMR-specific files
        self._create_pmr_files()
        
        self._log("Assetto Corsa conversion complete")
    
    def _parse_ac_files(self):
        """Parse Assetto Corsa specific files"""
        self._log("Parsing Assetto Corsa files...")
        
        # Parse data.acd (car data)
        data_acd = self._find_file("data.acd")
        if data_acd:
            self.car_data = self._parse_ini_file(data_acd)
            self._log(f"Found car data: {list(self.car_data.keys())}")
        
        # Parse model.ini
        model_ini = self._find_file("model.ini")
        if model_ini:
            self.model_info = self._parse_ini_file(model_ini)
            self._log(f"Found model info: {list(self.model_info.keys())}")
        
        # Parse physics.ini
        physics_ini = self._find_file("physics.ini")
        if physics_ini:
            self.physics_info = self._parse_ini_file(physics_ini)
            self._log(f"Found physics info: {list(self.physics_info.keys())}")
        
        # Parse setup.ini
        setup_ini = self._find_file("setup.ini")
        if setup_ini:
            setup_data = self._parse_ini_file(setup_ini)
            self._log(f"Found setup data: {list(setup_data.keys())}")
    
    def _convert_model_files(self):
        """Convert AC model files"""
        self._log("Converting model files...")
        
        # AC typically uses .kn5 files (encrypted) or .fbx/.obj
        model_files = self._find_files(['.kn5', '.fbx', '.obj', '.glb'])
        
        if not model_files:
            self._log("Warning: No model files found!")
            return
        
        # For .kn5 files, we'd need to decrypt them first
        # For now, we'll just copy other formats
        for model_file in model_files:
            if model_file.suffix.lower() == '.kn5':
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
        """Convert AC textures"""
        self._log("Converting textures...")
        
        # AC uses .dds files for textures
        texture_files = self._find_files(['.dds', '.png', '.jpg', '.jpeg', '.tga'])
        
        texture_dir = self.output_dir / "textures"
        texture_dir.mkdir(parents=True, exist_ok=True)
        
        for tex_file in texture_files:
            # Convert DDS to PNG if requested
            if tex_file.suffix.lower() == '.dds' and self.context.options.convert_textures:
                # In a real implementation, we'd convert DDS to PNG here
                # For now, just copy
                dest = texture_dir / f"{tex_file.stem}.png"
                self._copy_file(tex_file, dest)
            else:
                dest = texture_dir / tex_file.name
                self._copy_file(tex_file, dest)
    
    def _convert_physics(self):
        """Convert AC physics to PMR format"""
        self._log("Converting physics...")
        
        # Create physics directory
        physics_dir = self.output_dir / "physics"
        physics_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert physics.ini to PMR format
        if self.physics_info:
            pmr_physics = self._convert_physics_data()
            
            # Save as JSON for PMR
            physics_file = physics_dir / "physics.json"
            self._write_text_file(physics_file, json.dumps(pmr_physics, indent=2))
        
        # Copy other physics files
        physics_files = self._find_files(['.ini', '.txt'])
        physics_files = [f for f in physics_files if 'physics' in f.name.lower()]
        
        for pf in physics_files:
            dest = physics_dir / pf.name
            self._copy_file(pf, dest)
    
    def _convert_physics_data(self) -> Dict[str, Any]:
        """Convert AC physics data to PMR format"""
        # Map AC physics parameters to PMR format
        pmr_physics = {
            "mass": 1000.0,  # Default mass in kg
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
                "drag_coefficient": 0.3,
                "lift_coefficient": -0.5,
                "front_area": 2.0,
                "rear_wing": 0.5
            },
            "suspension": {
                "front": {
                    "spring_rate": 100000.0,
                    "damping": 10000.0,
                    "travel": 0.2,
                    "anti_roll_bar": 50000.0
                },
                "rear": {
                    "spring_rate": 120000.0,
                    "damping": 12000.0,
                    "travel": 0.2,
                    "anti_roll_bar": 60000.0
                }
            },
            "wheels": {
                "front": {
                    "radius": 0.3,
                    "width": 0.25,
                    "pressure": 2.0
                },
                "rear": {
                    "radius": 0.35,
                    "width": 0.3,
                    "pressure": 1.8
                }
            },
            "engine": {
                "max_power": 500.0,  # HP
                "max_rpm": 8000.0,
                "idle_rpm": 1000.0,
                "torque_curve": [0.0, 0.5, 0.8, 1.0, 0.9, 0.7]
            },
            "transmission": {
                "gear_ratios": [3.5, 2.5, 2.0, 1.7, 1.5, 1.3, 1.0],
                "final_drive": 4.0,
                "shift_time": 0.1
            },
            "brakes": {
                "front": {
                    "max_torque": 3000.0,
                    "bias": 0.6
                },
                "rear": {
                    "max_torque": 2000.0,
                    "bias": 0.4
                }
            }
        }
        
        # Try to extract values from AC physics data
        if self.physics_info:
            # Extract from [DATA] section
            data_section = self.physics_info.get('DATA', {})
            
            # Mass
            if 'MASS' in data_section:
                try:
                    pmr_physics['mass'] = float(data_section['MASS'])
                except ValueError:
                    pass
            
            # Inertia
            if 'INERTIA' in data_section:
                try:
                    inertia = float(data_section['INERTIA'])
                    pmr_physics['inertia'] = {'x': inertia, 'y': inertia, 'z': inertia}
                except ValueError:
                    pass
            
            # Center of mass
            if 'CM_POSITION' in data_section:
                try:
                    parts = data_section['CM_POSITION'].split(',')
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
            "description": f"Converted from Assetto Corsa",
            "type": "car",
            "tags": ["converted", "assetto-corsa"],
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
                "file": "car.fbx",  # Default model file
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
        """Extract car name from AC data"""
        if self.car_data:
            # Try to get name from [DATA] section
            data_section = self.car_data.get('DATA', {})
            if 'NAME' in data_section:
                return data_section['NAME']
            
            # Try to get from folder name
            return self.context.input_path.name
        
        return self.context.options.mod_name
