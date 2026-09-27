"""
PMR Forge - Texture Converter
Converts and processes texture files for PMR
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging
import shutil
import json

logger = logging.getLogger(__name__)


class TextureConverter:
    """Converts and processes texture files"""
    
    # Supported texture formats and their priorities
    TEXTURE_FORMATS = {
        '.png': {'priority': 1, 'convertible': True},
        '.jpg': {'priority': 2, 'convertible': True},
        '.jpeg': {'priority': 2, 'convertible': True},
        '.tga': {'priority': 3, 'convertible': True},
        '.bmp': {'priority': 4, 'convertible': True},
        '.dds': {'priority': 5, 'convertible': True},
        '.exr': {'priority': 6, 'convertible': True},
        '.psd': {'priority': 7, 'convertible': False},
        '.gif': {'priority': 8, 'convertible': False}
    }
    
    # Quality presets
    QUALITY_PRESETS = {
        "low": {
            "max_size": 1024,
            "compression": "high",
            "format": "png"
        },
        "medium": {
            "max_size": 2048,
            "compression": "medium",
            "format": "png"
        },
        "high": {
            "max_size": 4096,
            "compression": "low",
            "format": "png"
        }
    }
    
    def __init__(self, context):
        """
        Initialize the texture converter
        
        Args:
            context: ConversionContext from the pipeline
        """
        self.context = context
        self.source_dir = context.temp_dir / "source"
        self.output_dir = context.temp_dir / "converted"
        
        logger.info("Initialized TextureConverter")
    
    def convert(self) -> bool:
        """
        Convert all textures
        
        Returns:
            True if successful, False otherwise
        """
        self._log("Starting texture conversion...")
        
        try:
            # Find all texture files
            texture_files = self._find_texture_files()
            
            if not texture_files:
                self._log("No texture files found")
                return True
            
            # Create output texture directory
            texture_dir = self.output_dir / "textures"
            texture_dir.mkdir(parents=True, exist_ok=True)
            
            # Get quality preset
            quality = self.QUALITY_PRESETS.get(
                self.context.options.texture_quality.lower(),
                self.QUALITY_PRESETS["medium"]
            )
            
            # Process each texture
            for tex_file in texture_files:
                self._process_texture(tex_file, texture_dir, quality)
            
            self._log(f"Texture conversion complete. Processed {len(texture_files)} files.")
            return True
            
        except Exception as e:
            self._log(f"Error converting textures: {e}")
            return False
    
    def _find_texture_files(self) -> list:
        """Find all texture files in source directory"""
        files = list(self.source_dir.rglob("*"))
        texture_files = []
        
        for file_path in files:
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.TEXTURE_FORMATS:
                    texture_files.append(file_path)
        
        # Sort by format priority (higher priority first)
        texture_files.sort(
            key=lambda f: self.TEXTURE_FORMATS.get(f.suffix.lower(), {}).get('priority', 100)
        )
        
        return texture_files
    
    def _process_texture(self, tex_file: Path, output_dir: Path, quality: Dict[str, Any]):
        """Process a single texture file"""
        ext = tex_file.suffix.lower()
        
        # Generate output filename
        output_name = self._generate_output_name(tex_file, quality)
        output_path = output_dir / output_name
        
        # In a real implementation, we would:
        # 1. Convert the texture to the target format
        # 2. Resize if needed
        # 3. Apply compression
        # 4. Handle mipmaps
        # 5. Optimize for PMR
        
        # For now, we'll just copy the file with the new name
        self._copy_and_convert(tex_file, output_path, quality)
        
        self._log(f"Processed: {tex_file.relative_to(self.source_dir)} -> {output_name}")
    
    def _generate_output_name(self, tex_file: Path, quality: Dict[str, Any]) -> str:
        """Generate output filename for a texture"""
        # Use the target format from quality preset
        target_format = quality.get('format', 'png')
        
        # Replace extension with target format
        return f"{tex_file.stem}.{target_format}"
    
    def _copy_and_convert(self, src: Path, dst: Path, quality: Dict[str, Any]):
        """Copy and optionally convert a texture file"""
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # In a real implementation, we would use an image library
        # (like Pillow, OpenCV, or ImageMagick) to convert the image
        
        # For now, just copy the file
        shutil.copy2(src, dst)
        
        # If the source is DDS, note that we should convert it
        if src.suffix.lower() == '.dds':
            self._log(f"  Note: DDS texture {src.name} should be converted to PNG for best compatibility")
    
    def _should_convert_format(self, src_ext: str, target_ext: str) -> bool:
        """Determine if we should convert from source to target format"""
        # Always convert DDS to PNG
        if src_ext == '.dds' and target_ext == '.png':
            return True
        
        # Convert lossy formats to PNG for quality
        if src_ext in ['.jpg', '.jpeg'] and target_ext == '.png':
            return True
        
        # Don't convert if same format
        if src_ext == target_ext:
            return False
        
        return True
    
    def _get_texture_type(self, filename: str) -> str:
        """Determine the type of texture based on filename"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['diffuse', 'albedo', 'color']):
            return "diffuse"
        elif any(word in filename_lower for word in ['normal', 'bump']):
            return "normal"
        elif any(word in filename_lower for word in ['specular', 'roughness', 'gloss']):
            return "specular"
        elif any(word in filename_lower for word in ['emissive', 'emission', 'glow']):
            return "emissive"
        elif any(word in filename_lower for word in ['ao', 'occlusion', 'ambient']):
            return "ambient_occlusion"
        elif any(word in filename_lower for word in ['metallic', 'metalness']):
            return "metallic"
        elif any(word in filename_lower for word in ['height', 'displacement']):
            return "height"
        elif any(word in filename_lower for word in ['opacity', 'alpha']):
            return "opacity"
        else:
            return "unknown"
    
    def _get_target_resolution(self, texture_type: str, quality: Dict[str, Any]) -> Tuple[int, int]:
        """Get target resolution based on texture type and quality"""
        max_size = quality.get('max_size', 2048)
        
        # Different resolutions for different texture types
        type_resolutions = {
            "diffuse": max_size,
            "normal": max_size,
            "specular": max_size // 2,
            "emissive": max_size // 2,
            "ambient_occlusion": max_size // 2,
            "metallic": max_size // 2,
            "height": max_size,
            "opacity": max_size // 2,
            "unknown": max_size
        }
        
        resolution = type_resolutions.get(texture_type, max_size)
        return (resolution, resolution)
    
    def _log(self, message: str):
        """Log a message"""
        logger.info(f"[TextureConverter] {message}")
        self.context.log_messages.append(f"[TextureConverter] {message}")
        print(f"[TextureConverter] {message}")


class DDSConverter:
    """Specialized DDS texture converter"""
    
    @staticmethod
    def is_dds(file_path: Path) -> bool:
        """Check if a file is a DDS texture"""
        # Check extension
        if file_path.suffix.lower() != '.dds':
            return False
        
        # Check file signature (DDS magic number)
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                return magic == b'DDS '  # DDS file signature
        except Exception:
            return False
    
    @staticmethod
    def get_dds_info(file_path: Path) -> Optional[Dict[str, Any]]:
        """Get information about a DDS file"""
        try:
            with open(file_path, 'rb') as f:
                # Read header
                magic = f.read(4)
                if magic != b'DDS ':
                    return None
                
                # Read header (124 bytes for DDS_HEADER)
                header = f.read(124)
                
                # Parse header (simplified)
                info = {
                    'format': 'DDS',
                    'compressed': True,  # Most DDS are compressed
                    'mipmaps': True
                }
                
                return info
        except Exception as e:
            logger.error(f"Error reading DDS file {file_path}: {e}")
            return None
