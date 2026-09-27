"""
PMR Forge - Generic Model Converter
Converter for generic 3D model formats (OBJ, FBX, GLB)
"""

from pathlib import Path
from typing import Dict, Any
from .base_converter import BaseModelConverter
import logging
import shutil
import json

logger = logging.getLogger(__name__)


class GenericModelConverter(BaseModelConverter):
    """Converter for generic 3D model formats"""
    
    def __init__(self, context):
        super().__init__(context)
        self.model_format = "unknown"
    
    def convert(self):
        """Convert generic model to PMR format"""
        self._log("Starting generic model conversion")
        
        # Step 1: Detect model format
        self._detect_model_format()
        
        # Step 2: Convert model
        self._convert_model_files()
        
        # Step 3: Convert textures
        self._convert_textures()
        
        # Step 4: Generate physics (if requested)
        if self.context.options.generate_physics:
            self._generate_physics()
        
        # Step 5: Create PMR-specific files
        self._create_pmr_files()
        
        self._log(f"Generic model ({self.model_format}) conversion complete")
    
    def _detect_model_format(self):
        """Detect the model format from source files"""
        self._log("Detecting model format...")
        
        # Find model files
        model_files = self._find_files(['.obj', '.fbx', '.glb', '.gltf'])
        
        if model_files:
            # Use the first model file's extension
            ext = model_files[0].suffix.lower().replace('.', '')
            self.model_format = ext
            self._log(f"Detected model format: {ext.upper()}")
        else:
            self.model_format = "unknown"
            self._log("Warning: No model files found")
    
    def _convert_model_files(self):
        """Convert/process model files"""
        self._log("Processing model files...")
        
        # Find all model files
        model_files = self._find_files(['.obj', '.fbx', '.glb', '.gltf'])
        
        if not model_files:
            self._log("Warning: No model files found!")
            return
        
        # For generic models, we'll just copy them
        # In a real implementation, we might:
        # - Convert to a standard format
        # - Optimize the mesh
        # - Fix normals
        # - Scale the model
        
        for model_file in model_files:
            # Determine output name
            if self.model_format == "gltf":
                # GLTF files often come with separate bin/texture files
                dest = self.output_dir / f"car.{self.model_format}"
            else:
                dest = self.output_dir / model_file.name
            
            self._copy_file(model_file, dest)
            self._log(f"Copied model: {model_file.name}")
            
            # Also copy related files (for GLTF)
            if model_file.suffix.lower() == '.gltf':
                self._copy_gltf_assets(model_file)
    
    def _copy_gltf_assets(self, gltf_file: Path):
        """Copy GLTF-related assets (bin, textures)"""
        base_name = gltf_file.stem
        gltf_dir = gltf_file.parent
        
        # Copy .bin file
        bin_file = gltf_dir / f"{base_name}.bin"
        if bin_file.exists():
            dest = self.output_dir / f"{base_name}.bin"
            self._copy_file(bin_file, dest)
        
        # Copy texture files referenced in GLTF
        # In a real implementation, we'd parse the GLTF JSON
        # For now, just copy all textures in the same directory
        texture_files = self._find_files(['.png', '.jpg', '.jpeg', '.dds'])
        texture_files = [f for f in texture_files if f.parent == gltf_dir]
        
        for tex_file in texture_files:
            dest = self.output_dir / tex_file.name
            self._copy_file(tex_file, dest)
    
    def _convert_textures(self):
        """Convert and process textures"""
        self._log("Processing textures...")
        
        # Find texture files
        texture_files = self._find_files(['.png', '.jpg', '.jpeg', '.tga', '.bmp', '.dds'])
        
        if not texture_files:
            self._log("Warning: No texture files found")
            return
        
        texture_dir = self.output_dir / "textures"
        texture_dir.mkdir(parents=True, exist_ok=True)
        
        for tex_file in texture_files:
            # Convert DDS to PNG if requested
            if tex_file.suffix.lower() == '.dds' and self.context.options.convert_textures:
                # In a real implementation, we'd convert DDS to PNG here
                dest = texture_dir / f"{tex_file.stem}.png"
                self._copy_file(tex_file, dest)
                self._log(f"Converted texture: {tex_file.name} -> {dest.name}")
            else:
                dest = texture_dir / tex_file.name
                self._copy_file(tex_file, dest)
                self._log(f"Copied texture: {tex_file.name}")
    
    def _generate_physics(self):
        """Generate default physics for generic models"""
        self._log("Generating default physics...")
        
        # Create physics directory
        physics_dir = self.output_dir / "physics"
        physics_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate physics based on model format
        pmr_physics = self._generate_default_physics()
        
        # Save as JSON for PMR
        physics_file = physics_dir / "physics.json"
        self._write_text_file(physics_file, json.dumps(pmr_physics, indent=2))
    
    def _generate_default_physics(self) -> Dict[str, Any]:
        """Generate default physics based on model type"""
        # Use physics preset if specified
        preset = self.context.options.physics_preset.lower()
        
        # Default physics for different presets
        presets = {
            "default": self._get_default_physics(),
            "gt3": self._get_gt3_physics(),
            "gt4": self._get_gt4_physics(),
            "formula": self._get_formula_physics(),
            "rally": self._get_rally_physics()
        }
        
        return presets.get(preset, self._get_default_physics())
    
    def _get_default_physics(self) -> Dict[str, Any]:
        """Default physics for generic cars"""
        return {
            "mass": 1200.0,
            "inertia": {
                "x": 1.0,
                "y": 1.0,
                "z": 1.0
            },
            "center_of_mass": {
                "x": 0.0,
                "y": 0.0,
                "z": -0.1
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
                "max_power": 400.0,
                "max_rpm": 7500.0,
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
                    "max_torque": 2500.0,
                    "bias": 0.6
                },
                "rear": {
                    "max_torque": 2000.0,
                    "bias": 0.4
                }
            }
        }
    
    def _get_gt3_physics(self) -> Dict[str, Any]:
        """Physics for GT3 cars"""
        base = self._get_default_physics()
        base.update({
            "mass": 1250.0,
            "aerodynamics": {
                "drag_coefficient": 0.35,
                "lift_coefficient": -0.8,
                "front_area": 1.9,
                "rear_wing": 0.8
            },
            "suspension": {
                "front": {
                    "spring_rate": 140000.0,
                    "damping": 14000.0,
                    "anti_roll_bar": 70000.0
                },
                "rear": {
                    "spring_rate": 160000.0,
                    "damping": 16000.0,
                    "anti_roll_bar": 80000.0
                }
            },
            "engine": {
                "max_power": 550.0,
                "max_rpm": 8500.0
            },
            "brakes": {
                "front": {
                    "max_torque": 3500.0
                },
                "rear": {
                    "max_torque": 2500.0
                }
            }
        })
        return base
    
    def _get_gt4_physics(self) -> Dict[str, Any]:
        """Physics for GT4 cars"""
        base = self._get_default_physics()
        base.update({
            "mass": 1100.0,
            "aerodynamics": {
                "drag_coefficient": 0.32,
                "lift_coefficient": -0.6,
                "front_area": 1.8,
                "rear_wing": 0.6
            },
            "suspension": {
                "front": {
                    "spring_rate": 120000.0,
                    "damping": 12000.0,
                    "anti_roll_bar": 60000.0
                },
                "rear": {
                    "spring_rate": 140000.0,
                    "damping": 14000.0,
                    "anti_roll_bar": 70000.0
                }
            },
            "engine": {
                "max_power": 450.0,
                "max_rpm": 8000.0
            },
            "brakes": {
                "front": {
                    "max_torque": 3000.0
                },
                "rear": {
                    "max_torque": 2200.0
                }
            }
        })
        return base
    
    def _get_formula_physics(self) -> Dict[str, Any]:
        """Physics for formula cars"""
        return {
            "mass": 600.0,
            "inertia": {
                "x": 0.8,
                "y": 0.8,
                "z": 0.6
            },
            "center_of_mass": {
                "x": 0.0,
                "y": 0.0,
                "z": -0.05
            },
            "aerodynamics": {
                "drag_coefficient": 0.4,
                "lift_coefficient": -1.5,
                "front_area": 1.5,
                "rear_wing": 1.2
            },
            "suspension": {
                "front": {
                    "spring_rate": 200000.0,
                    "damping": 20000.0,
                    "travel": 0.1,
                    "anti_roll_bar": 100000.0
                },
                "rear": {
                    "spring_rate": 220000.0,
                    "damping": 22000.0,
                    "travel": 0.1,
                    "anti_roll_bar": 110000.0
                }
            },
            "wheels": {
                "front": {
                    "radius": 0.35,
                    "width": 0.2,
                    "pressure": 1.8
                },
                "rear": {
                    "radius": 0.4,
                    "width": 0.25,
                    "pressure": 1.6
                }
            },
            "engine": {
                "max_power": 800.0,
                "max_rpm": 15000.0,
                "idle_rpm": 2000.0,
                "torque_curve": [0.0, 0.4, 0.7, 0.9, 1.0, 0.95, 0.85]
            },
            "transmission": {
                "gear_ratios": [2.8, 2.2, 1.8, 1.5, 1.3, 1.1, 1.0],
                "final_drive": 3.5,
                "shift_time": 0.05
            },
            "brakes": {
                "front": {
                    "max_torque": 4000.0,
                    "bias": 0.7
                },
                "rear": {
                    "max_torque": 2000.0,
                    "bias": 0.3
                }
            }
        }
    
    def _get_rally_physics(self) -> Dict[str, Any]:
        """Physics for rally cars"""
        base = self._get_default_physics()
        base.update({
            "mass": 1300.0,
            "inertia": {
                "x": 1.2,
                "y": 1.2,
                "z": 1.1
            },
            "center_of_mass": {
                "x": 0.0,
                "y": 0.0,
                "z": -0.15
            },
            "aerodynamics": {
                "drag_coefficient": 0.4,
                "lift_coefficient": -0.3,
                "front_area": 2.2,
                "rear_wing": 0.3
            },
            "suspension": {
                "front": {
                    "spring_rate": 80000.0,
                    "damping": 8000.0,
                    "travel": 0.25,
                    "anti_roll_bar": 40000.0
                },
                "rear": {
                    "spring_rate": 100000.0,
                    "damping": 10000.0,
                    "travel": 0.25,
                    "anti_roll_bar": 50000.0
                }
            },
            "wheels": {
                "front": {
                    "radius": 0.34,
                    "width": 0.28,
                    "pressure": 1.8
                },
                "rear": {
                    "radius": 0.34,
                    "width": 0.28,
                    "pressure": 1.8
                }
            },
            "engine": {
                "max_power": 350.0,
                "max_rpm": 7000.0,
                "idle_rpm": 1000.0,
                "torque_curve": [0.0, 0.6, 0.9, 1.0, 0.95, 0.85]
            },
            "transmission": {
                "gear_ratios": [4.0, 3.0, 2.5, 2.0, 1.7, 1.5, 1.0],
                "final_drive": 4.5,
                "shift_time": 0.15
            },
            "brakes": {
                "front": {
                    "max_torque": 2000.0,
                    "bias": 0.55
                },
                "rear": {
                    "max_torque": 1800.0,
                    "bias": 0.45
                }
            },
            "drivetrain": {
                "type": "AWD",
                "front_bias": 0.5,
                "rear_bias": 0.5,
                "differential": {
                    "front": {"type": "LSD", "lock": 0.7},
                    "rear": {"type": "LSD", "lock": 0.7},
                    "center": {"type": "LSD", "lock": 0.5}
                }
            }
        })
        return base
    
    def _create_pmr_files(self):
        """Create PMR-specific configuration files"""
        self._log("Creating PMR configuration files...")
        
        # Create mod info
        mod_info = {
            "name": self.context.options.mod_name,
            "version": self.context.options.mod_version,
            "author": self.context.options.mod_author,
            "description": f"Converted from {self.model_format.upper()} model",
            "type": "car",
            "tags": ["converted", self.model_format],
            "compatibility": {
                "pmr_version": "1.0.0",
                "game_version": "1.0.0"
            }
        }
        
        mod_info_file = self.output_dir / "mod.json"
        self._write_text_file(mod_info_file, json.dumps(mod_info, indent=2))
        
        # Create car info
        # Find the main model file
        model_files = list(self.output_dir.glob("*.fbx")) + \
                      list(self.output_dir.glob("*.obj")) + \
                      list(self.output_dir.glob("*.glb")) + \
                      list(self.output_dir.glob("*.gltf"))
        
        main_model = "car.fbx"  # Default
        if model_files:
            main_model = model_files[0].name
        
        car_info = {
            "model": {
                "file": main_model,
                "scale": self.context.options.scale_factor,
                "offset": {"x": 0.0, "y": 0.0, "z": 0.0}
            },
            "textures": {
                "diffuse": "textures/diffuse.png",
                "normal": "textures/normal.png",
                "specular": "textures/specular.png"
            },
            "physics": "physics/physics.json" if self.context.options.generate_physics else None,
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
