"""
PMR Forge - PMR Packager
Packages converted files into a PMR mod structure
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json
import shutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PMRModStructure:
    """PMR mod directory structure"""
    mod_name: str
    version: str
    author: str
    
    # Directories
    models_dir: str = "models"
    textures_dir: str = "textures"
    physics_dir: str = "physics"
    sounds_dir: str = "sounds"
    lods_dir: str = "lods"
    config_dir: str = "config"
    
    # Main files
    mod_info_file: str = "mod.json"
    car_info_file: str = "car.json"
    
    def get_structure(self) -> Dict[str, Any]:
        """Get the complete mod structure"""
        return {
            "name": self.mod_name,
            "version": self.version,
            "author": self.author,
            "date": datetime.now().isoformat(),
            "structure": {
                "directories": [
                    self.models_dir,
                    self.textures_dir,
                    self.physics_dir,
                    self.sounds_dir,
                    self.lods_dir,
                    self.config_dir
                ],
                "files": [
                    self.mod_info_file,
                    self.car_info_file
                ]
            }
        }


class PMRPackager:
    """Packages converted files into a PMR mod"""
    
    def __init__(self, context):
        """
        Initialize the packager
        
        Args:
            context: ConversionContext from the pipeline
        """
        self.context = context
        self.source_dir = context.temp_dir / "converted"
        self.output_dir = context.output_path
        
        # Create mod structure info
        self.mod_structure = PMRModStructure(
            mod_name=context.options.mod_name,
            version=context.options.mod_version,
            author=context.options.mod_author
        )
        
        logger.info("Initialized PMRPackager")
    
    def package(self) -> bool:
        """
        Package the converted files into a PMR mod
        
        Returns:
            True if successful, False otherwise
        """
        self._log("Packaging PMR mod...")
        
        try:
            # Create output directory
            self._create_output_directory()
            
            # Copy/modify files to output
            self._copy_files()
            
            # Create mod configuration
            self._create_mod_config()
            
            # Create car configuration
            self._create_car_config()
            
            # Create README
            self._create_readme()
            
            # Create preview image placeholder
            self._create_preview_placeholder()
            
            self._log(f"PMR mod packaged successfully to {self.output_dir}")
            return True
            
        except Exception as e:
            self._log(f"Error packaging mod: {e}")
            return False
    
    def _create_output_directory(self):
        """Create the output directory structure"""
        # Create main mod directory (use mod name)
        mod_dir = self.output_dir / self.context.options.mod_name
        mod_dir.mkdir(parents=True, exist_ok=True)
        
        # Update output dir to be the mod directory
        self.output_dir = mod_dir
        
        # Create subdirectories
        directories = [
            self.output_dir / self.mod_structure.models_dir,
            self.output_dir / self.mod_structure.textures_dir,
            self.output_dir / self.mod_structure.physics_dir,
            self.output_dir / self.mod_structure.sounds_dir,
            self.output_dir / self.mod_structure.lods_dir,
            self.output_dir / self.mod_structure.config_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self._log(f"Created directory structure at {self.output_dir}")
    
    def _copy_files(self):
        """Copy files from source to output with proper organization"""
        self._log("Copying files...")
        
        # Copy model files
        model_files = list(self.source_dir.glob("*.fbx")) + \
                      list(self.source_dir.glob("*.obj")) + \
                      list(self.source_dir.glob("*.glb")) + \
                      list(self.source_dir.glob("*.gltf")) + \
                      list(self.source_dir.glob("*.bin"))
        
        for model_file in model_files:
            dest = self.output_dir / self.mod_structure.models_dir / model_file.name
            self._copy_file(model_file, dest)
        
        # Copy texture files
        texture_dir = self.source_dir / "textures"
        if texture_dir.exists():
            for tex_file in texture_dir.iterdir():
                if tex_file.is_file():
                    dest = self.output_dir / self.mod_structure.textures_dir / tex_file.name
                    self._copy_file(tex_file, dest)
        
        # Copy physics files
        physics_dir = self.source_dir / "physics"
        if physics_dir.exists():
            for phys_file in physics_dir.iterdir():
                if phys_file.is_file():
                    dest = self.output_dir / self.mod_structure.physics_dir / phys_file.name
                    self._copy_file(phys_file, dest)
        
        # Copy LOD files if they exist
        lod_files = list(self.source_dir.glob("lod*.fbx")) + \
                     list(self.source_dir.glob("lod*.obj")) + \
                     list(self.source_dir.glob("lod*.glb"))
        
        for lod_file in lod_files:
            dest = self.output_dir / self.mod_structure.lods_dir / lod_file.name
            self._copy_file(lod_file, dest)
        
        # Copy other files (configs, etc.)
        other_files = [
            self.source_dir / "mod.json",
            self.source_dir / "car.json"
        ]
        
        for other_file in other_files:
            if other_file.exists():
                dest = self.output_dir / self.mod_structure.config_dir / other_file.name
                self._copy_file(other_file, dest)
        
        self._log("Files copied successfully")
    
    def _copy_file(self, src: Path, dst: Path):
        """Copy a file with logging"""
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        self._log(f"Copied: {src.relative_to(self.source_dir)} -> {dst.relative_to(self.output_dir)}")
    
    def _create_mod_config(self):
        """Create mod.json configuration"""
        self._log("Creating mod configuration...")
        
        mod_config = {
            "name": self.context.options.mod_name,
            "version": self.context.options.mod_version,
            "author": self.context.options.mod_author,
            "description": f"Car mod converted using PMR Forge",
            "type": "car",
            "tags": ["converted"],
            "compatibility": {
                "pmr_version": "1.0.0",
                "game_version": "1.0.0",
                "minimum_version": "1.0.0"
            },
            "dependencies": [],
            "conflicts": [],
            "installation": {
                "method": "copy",
                "destination": "cars"
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "created_by": "PMR Forge",
                "source_format": self.context.detected_format.value if self.context.detected_format else "unknown",
                "conversion_options": {
                    "convert_textures": self.context.options.convert_textures,
                    "generate_physics": self.context.options.generate_physics,
                    "create_lods": self.context.options.create_lods,
                    "optimize_model": self.context.options.optimize_model,
                    "include_interior": self.context.options.include_interior,
                    "generate_sounds": self.context.options.generate_sounds,
                    "scale_factor": self.context.options.scale_factor,
                    "texture_quality": self.context.options.texture_quality,
                    "physics_preset": self.context.options.physics_preset
                }
            }
        }
        
        # Add source info if available
        if self.context.detected_format:
            mod_config["tags"].append(self.context.detected_format.value)
        
        mod_config_file = self.output_dir / self.mod_structure.mod_info_file
        self._write_json(mod_config_file, mod_config)
        
        self._log("Mod configuration created")
    
    def _create_car_config(self):
        """Create car.json configuration"""
        self._log("Creating car configuration...")
        
        # Find the main model file
        model_files = list((self.output_dir / self.mod_structure.models_dir).glob("*"))
        model_files = [f for f in model_files if f.is_file() and f.suffix.lower() in ['.fbx', '.obj', '.glb', '.gltf']]
        
        main_model = "car.fbx"  # Default
        if model_files:
            main_model = model_files[0].name
        
        # Find texture files
        texture_files = list((self.output_dir / self.mod_structure.textures_dir).glob("*"))
        texture_files = [f for f in texture_files if f.is_file()]
        
        # Find physics file
        physics_files = list((self.output_dir / self.mod_structure.physics_dir).glob("*"))
        physics_files = [f for f in physics_files if f.is_file()]
        
        physics_file = None
        if physics_files:
            physics_file = self.mod_structure.physics_dir + "/" + physics_files[0].name
        
        # Find LOD files
        lod_files = list((self.output_dir / self.mod_structure.lods_dir).glob("*"))
        lod_files = [f for f in lod_files if f.is_file()]
        
        lods = []
        if lod_files and self.context.options.create_lods:
            for i, lod_file in enumerate(lod_files):
                lods.append({
                    "distance": 50.0 * (i + 1),
                    "file": self.mod_structure.lods_dir + "/" + lod_file.name
                })
        
        # Find sounds
        sound_files = list((self.output_dir / self.mod_structure.sounds_dir).glob("*"))
        sound_files = [f for f in sound_files if f.is_file()]
        
        sounds = None
        if sound_files and self.context.options.generate_sounds:
            sounds = {
                "engine": self.mod_structure.sounds_dir + "/engine.wav",
                "exhaust": self.mod_structure.sounds_dir + "/exhaust.wav"
            }
        
        # Build texture map
        textures = {
            "diffuse": None,
            "normal": None,
            "specular": None,
            "emissive": None,
            "ambient_occlusion": None
        }
        
        if texture_files:
            for tex_file in texture_files:
                tex_name = tex_file.name.lower()
                if "diffuse" in tex_name or "albedo" in tex_name:
                    textures["diffuse"] = self.mod_structure.textures_dir + "/" + tex_file.name
                elif "normal" in tex_name:
                    textures["normal"] = self.mod_structure.textures_dir + "/" + tex_file.name
                elif "specular" in tex_name or "roughness" in tex_name:
                    textures["specular"] = self.mod_structure.textures_dir + "/" + tex_file.name
                elif "emissive" in tex_name or "emission" in tex_name:
                    textures["emissive"] = self.mod_structure.textures_dir + "/" + tex_file.name
                elif "ao" in tex_name or "occlusion" in tex_name:
                    textures["ambient_occlusion"] = self.mod_structure.textures_dir + "/" + tex_file.name
        
        # Remove None values
        textures = {k: v for k, v in textures.items() if v is not None}
        
        car_config = {
            "name": self.context.options.mod_name,
            "model": {
                "file": self.mod_structure.models_dir + "/" + main_model,
                "scale": self.context.options.scale_factor,
                "offset": {"x": 0.0, "y": 0.0, "z": 0.0},
                "shadow_cast": True,
                "shadow_receive": True
            },
            "textures": textures,
            "physics": physics_file,
            "sounds": sounds,
            "lods": lods,
            "interior": {
                "enabled": self.context.options.include_interior,
                "model": None,
                "camera": {
                    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
                }
            } if self.context.options.include_interior else None,
            "features": {
                "damage": True,
                "dirty": True,
                "headlights": True,
                "brake_lights": True,
                "reverse_lights": True,
                "turn_signals": True,
                "wipers": False,
                "movable_steering_wheel": True,
                "working_gauges": True
            },
            "camera": {
                "near_clip": 0.1,
                "far_clip": 1000.0,
                "fov": 60.0
            }
        }
        
        car_config_file = self.output_dir / self.mod_structure.car_info_file
        self._write_json(car_config_file, car_config)
        
        self._log("Car configuration created")
    
    def _create_readme(self):
        """Create a README file for the mod"""
        self._log("Creating README...")
        
        readme_content = f"""# {self.context.options.mod_name}

A car mod for Project Motor Racing, converted using PMR Forge.

## Mod Information

- **Version**: {self.context.options.mod_version}
- **Author**: {self.context.options.mod_author}
- **Conversion Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source Format**: {self.context.detected_format.value if self.context.detected_format else 'Unknown'}

## Installation

1. Copy the `{self.context.options.mod_name}` folder to your PMR `cars` directory
2. Launch the game
3. Select the car from the garage

## Features

- Converted from original {self.context.detected_format.value if self.context.detected_format else 'model'} files
- Physics: {'Generated' if self.context.options.generate_physics else 'Not included'}
- LODs: {'Included' if self.context.options.create_lods else 'Not included'}
- Interior: {'Included' if self.context.options.include_interior else 'Not included'}
- Textures: {'Converted' if self.context.options.convert_textures else 'Original'}

## Conversion Options

- Scale Factor: {self.context.options.scale_factor}
- Texture Quality: {self.context.options.texture_quality}
- Physics Preset: {self.context.options.physics_preset}

## Notes

This mod was automatically converted using PMR Forge. Some features may need manual adjustment for optimal performance.

## Credits

- Original car model: [Original Author]
- Conversion: PMR Forge

---

**PMR Forge** - One-click car conversion tool for Project Motor Racing
"""
        
        readme_file = self.output_dir / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
        
        self._log("README created")
    
    def _create_preview_placeholder(self):
        """Create a placeholder for preview image"""
        self._log("Creating preview placeholder...")
        
        preview_dir = self.output_dir / "preview"
        preview_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a placeholder text file
        placeholder_file = preview_dir / "preview.png"
        placeholder_file.write_text(
            "PMR Mod Preview Image\n\nPlace your preview image here (1920x1080 recommended)",
            encoding='utf-8'
        )
        
        self._log("Preview placeholder created")
    
    def _log(self, message: str):
        """Log a message"""
        logger.info(f"[PMRPackager] {message}")
        self.context.log_messages.append(f"[PMRPackager] {message}")
        print(f"[PMRPackager] {message}")
    
    def _write_json(self, path: Path, data: Dict[str, Any]):
        """Write JSON data to a file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
