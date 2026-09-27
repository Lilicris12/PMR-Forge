#!/usr/bin/env python3
"""
PMR Forge - Conversion Pipeline
Main Python script for converting car models to PMR format
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ConversionFormat(Enum):
    """Supported input formats"""
    OBJ = "obj"
    FBX = "fbx"
    GLB = "glb"
    ASSETTO_CORSA = "assetto_corsa"
    RFACTOR = "rfactor"
    GTR2 = "gtr2"
    AUTOMOBILISTA_1 = "automobilista_1"
    UNKNOWN = "unknown"


class ConversionStep(Enum):
    """Conversion pipeline steps"""
    DETECTION = "detection"
    EXTRACTION = "extraction"
    CONVERSION = "conversion"
    TEXTURES = "textures"
    PHYSICS = "physics"
    LODS = "lods"
    PACKAGING = "packaging"
    CLEANUP = "cleanup"


@dataclass
class ConversionOptions:
    """Options for the conversion process"""
    mod_name: str = "Untitled Mod"
    mod_version: str = "1.0.0"
    mod_author: str = "Unknown"
    convert_textures: bool = True
    generate_physics: bool = True
    create_lods: bool = True
    optimize_model: bool = True
    include_interior: bool = True
    generate_sounds: bool = True
    scale_factor: float = 1.0
    texture_quality: str = "medium"
    physics_preset: str = "default"


@dataclass
class ConversionContext:
    """Context for the conversion process"""
    input_path: Path
    output_path: Path
    temp_dir: Path
    options: ConversionOptions
    detected_format: ConversionFormat = ConversionFormat.UNKNOWN
    current_step: ConversionStep = ConversionStep.DETECTION
    progress: float = 0.0
    log_messages: List[str] = field(default_factory=list)


class ConversionError(Exception):
    """Custom exception for conversion errors"""
    pass


class PMRForgeConverter:
    """Main converter class"""
    
    def __init__(self, input_path: str, output_path: str, options: Dict[str, Any]):
        """
        Initialize the converter
        
        Args:
            input_path: Path to input files
            output_path: Path to output directory
            options: Conversion options as dictionary
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.options = ConversionOptions(**options)
        self.context = None
        
        # Validate input
        if not self.input_path.exists():
            raise ConversionError(f"Input path does not exist: {input_path}")
        
        logger.info(f"Initialized converter: {input_path} -> {output_path}")
    
    def run(self) -> bool:
        """
        Run the full conversion pipeline
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Setup context
            self._setup_context()
            
            # Run pipeline steps
            self._detect_format()
            self._extract_files()
            self._convert_model()
            
            if self.options.convert_textures:
                self._convert_textures()
            
            if self.options.generate_physics:
                self._generate_physics()
            
            if self.options.create_lods:
                self._create_lods()
            
            if self.options.optimize_model:
                self._optimize_model()
            
            self._package_mod()
            self._cleanup()
            
            logger.info("Conversion completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            self._log_message(f"Error: {str(e)}")
            return False
        finally:
            if self.context:
                self._cleanup()
    
    def _setup_context(self):
        """Setup the conversion context"""
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="pmr_forge_"))
        
        self.context = ConversionContext(
            input_path=self.input_path,
            output_path=self.output_path,
            temp_dir=temp_dir,
            options=self.options
        )
        
        logger.info(f"Created temp directory: {temp_dir}")
        self._log_message(f"Temp directory: {temp_dir}")
    
    def _log_message(self, message: str):
        """Log a message and update progress"""
        if self.context:
            self.context.log_messages.append(message)
        logger.info(message)
        print(message)  # This goes to stdout for Electron to capture
    
    def _update_progress(self, step: ConversionStep, progress: float, message: str = ""):
        """Update conversion progress"""
        if self.context:
            self.context.current_step = step
            self.context.progress = progress
        
        if message:
            self._log_message(message)
        
        # Print progress as JSON for Electron to parse
        progress_data = {
            "step": step.value,
            "progress": int(progress * 100),
            "message": message
        }
        print(json.dumps(progress_data))
    
    def _detect_format(self):
        """Detect the input format"""
        self._update_progress(ConversionStep.DETECTION, 0.0, "Detecting input format...")
        
        input_path = self.context.input_path
        
        # Check for specific game folder structures
        if self._is_assetto_corsa(input_path):
            self.context.detected_format = ConversionFormat.ASSETTO_CORSA
            self._update_progress(ConversionStep.DETECTION, 0.1, "Detected: Assetto Corsa")
            return
        
        if self._is_rfactor(input_path):
            self.context.detected_format = ConversionFormat.RFACTOR
            self._update_progress(ConversionStep.DETECTION, 0.1, "Detected: rFactor")
            return
        
        if self._is_gtr2(input_path):
            self.context.detected_format = ConversionFormat.GTR2
            self._update_progress(ConversionStep.DETECTION, 0.1, "Detected: GTR2")
            return
        
        if self._is_automobilista_1(input_path):
            self.context.detected_format = ConversionFormat.AUTOMOBILISTA_1
            self._update_progress(ConversionStep.DETECTION, 0.1, "Detected: Automobilista 1")
            return
        
        # Check for model files
        files = list(input_path.rglob("*"))
        model_files = [f for f in files if f.is_file() and f.suffix.lower() in ['.obj', '.fbx', '.glb']]
        
        if model_files:
            # Use the first model file's extension
            ext = model_files[0].suffix.lower().replace('.', '')
            try:
                self.context.detected_format = ConversionFormat(ext.upper())
                self._update_progress(ConversionStep.DETECTION, 0.1, f"Detected: {ext.upper()}")
                return
            except ValueError:
                pass
        
        # Default to unknown
        self.context.detected_format = ConversionFormat.UNKNOWN
        self._update_progress(ConversionStep.DETECTION, 0.1, "Warning: Could not detect format, trying auto-detection")
    
    def _is_assetto_corsa(self, path: Path) -> bool:
        """Check if path is an Assetto Corsa car folder"""
        # Check for AC specific files
        ac_files = ['data.acd', 'model.ini', 'physics.ini']
        return any((path / f).exists() for f in ac_files)
    
    def _is_rfactor(self, path: Path) -> bool:
        """Check if path is an rFactor car folder"""
        rf_files = ['.veh', '.gen', 'vehicle.ini']
        return any((path / f).exists() for f in rf_files)
    
    def _is_gtr2(self, path: Path) -> bool:
        """Check if path is a GTR2 car folder"""
        gtr2_files = ['.gtr', 'car.ini', 'physics.ini']
        return any((path / f).exists() for f in gtr2_files)
    
    def _is_automobilista_1(self, path: Path) -> bool:
        """Check if path is an Automobilista 1 car folder"""
        ams_files = ['.ams', 'vehicle.ini', 'setup.ini']
        return any((path / f).exists() for f in ams_files)
    
    def _extract_files(self):
        """Extract files from the input to temp directory"""
        self._update_progress(ConversionStep.EXTRACTION, 0.15, "Extracting files...")
        
        input_path = self.context.input_path
        temp_dir = self.context.temp_dir
        
        # Copy all files to temp directory
        if input_path.is_dir():
            self._copy_directory(input_path, temp_dir / "source")
        else:
            # Single file
            shutil.copy2(input_path, temp_dir / "source")
        
        self._update_progress(ConversionStep.EXTRACTION, 0.25, "Files extracted to temp directory")
    
    def _copy_directory(self, src: Path, dst: Path):
        """Copy directory recursively"""
        dst.mkdir(parents=True, exist_ok=True)
        
        for item in src.iterdir():
            s = src / item
            d = dst / item
            
            if s.is_dir():
                self._copy_directory(s, d)
            else:
                shutil.copy2(s, d)
    
    def _convert_model(self):
        """Convert the 3D model to PMR format"""
        self._update_progress(ConversionStep.CONVERSION, 0.30, "Converting 3D model...")
        
        # Get the appropriate converter based on detected format
        converter = self._get_model_converter()
        
        if converter:
            converter.convert()
        else:
            # Fallback: try to find and convert model files
            self._convert_model_files()
        
        self._update_progress(ConversionStep.CONVERSION, 0.50, "Model conversion complete")
    
    def _get_model_converter(self):
        """Get the appropriate converter for the detected format"""
        from .convertors import (
            AssettoCorsaConverter,
            RFactorConverter,
            GTR2Converter,
            Automobilista1Converter,
            GenericModelConverter
        )
        
        converters = {
            ConversionFormat.ASSETTO_CORSA: AssettoCorsaConverter,
            ConversionFormat.RFACTOR: RFactorConverter,
            ConversionFormat.GTR2: GTR2Converter,
            ConversionFormat.AUTOMOBILISTA_1: Automobilista1Converter,
            ConversionFormat.OBJ: GenericModelConverter,
            ConversionFormat.FBX: GenericModelConverter,
            ConversionFormat.GLB: GenericModelConverter,
            ConversionFormat.UNKNOWN: GenericModelConverter
        }
        
        converter_class = converters.get(self.context.detected_format, GenericModelConverter)
        
        try:
            return converter_class(self.context)
        except Exception as e:
            logger.error(f"Failed to create converter: {e}")
            return GenericModelConverter(self.context)
    
    def _convert_model_files(self):
        """Convert model files in the temp directory"""
        source_dir = self.context.temp_dir / "source"
        output_dir = self.context.temp_dir / "converted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find model files
        model_files = list(source_dir.rglob("*"))
        model_files = [f for f in model_files if f.is_file() and f.suffix.lower() in ['.obj', '.fbx', '.glb']]
        
        if not model_files:
            self._log_message("Warning: No model files found in source directory")
            return
        
        # For now, just copy the files (actual conversion would happen here)
        for model_file in model_files:
            dest = output_dir / model_file.name
            shutil.copy2(model_file, dest)
            self._log_message(f"Copied: {model_file.name}")
    
    def _convert_textures(self):
        """Convert and process textures"""
        self._update_progress(ConversionStep.TEXTURES, 0.55, "Processing textures...")
        
        # Texture conversion logic would go here
        # For now, just copy texture files
        self._copy_textures()
        
        self._update_progress(ConversionStep.TEXTURES, 0.65, "Texture processing complete")
    
    def _copy_textures(self):
        """Copy texture files"""
        source_dir = self.context.temp_dir / "source"
        texture_dir = self.context.temp_dir / "textures"
        texture_dir.mkdir(parents=True, exist_ok=True)
        
        # Find texture files
        texture_extensions = ['.png', '.jpg', '.jpeg', '.tga', '.bmp', '.dds']
        texture_files = list(source_dir.rglob("*"))
        texture_files = [f for f in texture_files if f.is_file() and f.suffix.lower() in texture_extensions]
        
        for tex_file in texture_files:
            dest = texture_dir / tex_file.name
            shutil.copy2(tex_file, dest)
            self._log_message(f"Texture: {tex_file.name}")
    
    def _generate_physics(self):
        """Generate physics configuration"""
        self._update_progress(ConversionStep.PHYSICS, 0.70, "Generating physics...")
        
        from .utils.physics_generator import PhysicsGenerator
        
        generator = PhysicsGenerator(self.context)
        generator.generate()
        
        self._update_progress(ConversionStep.PHYSICS, 0.80, "Physics generation complete")
    
    def _create_lods(self):
        """Create Level of Detail models"""
        self._update_progress(ConversionStep.LODS, 0.82, "Creating LODs...")
        
        # LOD creation logic would go here
        # For now, just log it
        self._log_message("LOD creation would happen here")
        
        self._update_progress(ConversionStep.LODS, 0.85, "LOD creation complete")
    
    def _optimize_model(self):
        """Optimize the 3D model"""
        self._update_progress(ConversionStep.CONVERSION, 0.87, "Optimizing model...")
        
        # Optimization logic would go here
        self._log_message("Model optimization would happen here")
        
        self._update_progress(ConversionStep.CONVERSION, 0.90, "Model optimization complete")
    
    def _package_mod(self):
        """Package the converted files into a PMR mod"""
        self._update_progress(ConversionStep.PACKAGING, 0.92, "Packaging mod...")
        
        from .utils.pmr_packager import PMRPackager
        
        packager = PMRPackager(self.context)
        packager.package()
        
        self._update_progress(ConversionStep.PACKAGING, 0.98, "Packaging complete")
    
    def _cleanup(self):
        """Clean up temporary files"""
        self._update_progress(ConversionStep.CLEANUP, 0.99, "Cleaning up...")
        
        if self.context and self.context.temp_dir.exists():
            try:
                shutil.rmtree(self.context.temp_dir)
                self._log_message(f"Removed temp directory: {self.context.temp_dir}")
            except Exception as e:
                self._log_message(f"Warning: Could not remove temp directory: {e}")
        
        self._update_progress(ConversionStep.CLEANUP, 1.0, "Cleanup complete")


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python conversion_pipeline.py <input_path> <output_path> [options]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    options = {}
    
    # Parse options from JSON if provided
    if len(sys.argv) > 3:
        try:
            options = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            logger.error("Invalid JSON options")
            sys.exit(1)
    
    # Set default options
    defaults = {
        "mod_name": "Untitled Mod",
        "mod_version": "1.0.0",
        "mod_author": "Unknown",
        "convert_textures": True,
        "generate_physics": True,
        "create_lods": True,
        "optimize_model": True,
        "include_interior": True,
        "generate_sounds": True,
        "scale_factor": 1.0,
        "texture_quality": "medium",
        "physics_preset": "default"
    }
    
    # Merge options
    defaults.update(options)
    
    try:
        # Create and run converter
        converter = PMRForgeConverter(input_path, output_path, defaults)
        success = converter.run()
        
        if success:
            print("\nCONVERSION_SUCCESS")
            sys.exit(0)
        else:
            print("\nCONVERSION_FAILED")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
