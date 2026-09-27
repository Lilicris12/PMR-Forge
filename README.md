# PMR Forge

![PMR Forge Logo](resources/icon.png)

**PMR Forge** is a powerful desktop tool that converts car models from various formats to **Project Motor Racing (PMR)** drivable mods with **one click**.

---

## ✨ Features

### 🎯 One-Click Conversion
- Drag and drop your car model files
- Select your output folder
- Click convert and you're done!

### 🚗 Multi-Format Support
Convert from all major car model formats:
- **3D Model Files**: OBJ, FBX, GLB, GLTF
- **Sim Racing Games**:
  - ✅ Assetto Corsa
  - ✅ rFactor 1 & 2
  - ✅ GTR2
  - ✅ Automobilista 1

### ⚙️ Automatic Processing
- **Model Conversion**: Convert 3D models to PMR-compatible formats
- **Texture Conversion**: Convert DDS, TGA, and other formats to PNG
- **Physics Generation**: Automatic physics configuration with presets
- **LOD Generation**: Create Level of Detail models for performance
- **Model Optimization**: Optimize meshes for better performance
- **Interior Support**: Include interior models
- **Sound Generation**: Generate placeholder sound effects

### 📦 Complete Packaging
- Creates a ready-to-install PMR mod folder
- Includes all necessary configuration files
- Generates comprehensive README
- Preserves mod metadata

---

## 📥 Installation

### Option 1: Pre-built Binary (Recommended)
1. Download the latest release for your platform from [Releases](https://github.com/Lilicris12/PMR-Forge/releases)
2. Extract the archive
3. Run the executable (`PMR-Forge.exe` on Windows, `PMR-Forge` on macOS, or `pmr-forge` on Linux)

### Option 2: From Source
1. Clone this repository:
   ```bash
   git clone https://github.com/Lilicris12/PMR-Forge.git
   cd PMR-Forge
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the application:
   ```bash
   npm start
   ```

---

## 🚀 Usage

### Quick Start
1. **Open PMR Forge**
2. **Select Input Folder**: Click "Browse" and select the folder containing your car model files
3. **Select Output Folder**: Choose where to save your PMR mod
4. **Configure Options** (optional): Adjust settings like mod name, physics preset, etc.
5. **Click "Convert to PMR Mod"**: Start the conversion process
6. **Install the Mod**: Copy the output folder to your PMR `cars` directory

### Detailed Guide

#### Input Files
PMR Forge can accept:
- A folder containing car model files (FBX, OBJ, etc.)
- A folder from a sim racing game (Assetto Corsa, rFactor, etc.)
- Individual model files

#### Output
The tool creates:
```
OutputFolder/
├── mod.json              # Mod metadata
├── car.json              # Car configuration
├── README.md             # Documentation
├── models/               # 3D models
│   ├── car.fbx           # Main model
│   └── interior.fbx      # Interior (if enabled)
├── textures/             # Textures
│   ├── diffuse.png       # Diffuse map
│   ├── normal.png        # Normal map
│   └── specular.png      # Specular map
├── physics/              # Physics configuration
│   └── physics.json      # Physics parameters
├── sounds/               # Sound effects (if enabled)
│   ├── engine.wav        # Engine sound
│   └── exhaust.wav       # Exhaust sound
└── preview/              # Preview image (placeholder)
    └── preview.png
```

---

## ⚙️ Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| **Mod Name** | Text | Untitled Mod | Name of your mod |
| **Mod Version** | Text | 1.0.0 | Version number |
| **Mod Author** | Text | Unknown | Your name or team |
| **Convert Textures** | Boolean | ✅ | Convert texture formats |
| **Generate Physics** | Boolean | ✅ | Create physics configuration |
| **Create LODs** | Boolean | ✅ | Generate Level of Detail models |
| **Optimize Model** | Boolean | ✅ | Optimize the 3D model |
| **Include Interior** | Boolean | ✅ | Include interior model |
| **Generate Sounds** | Boolean | ✅ | Generate placeholder sounds |
| **Scale Factor** | Number | 1.0 | Scale the model (1.0 = original size) |
| **Texture Quality** | Select | Medium | Texture resolution (Low/Medium/High) |
| **Physics Preset** | Select | Default | Pre-configured physics |

### Physics Presets

| Preset | Description | Best For |
|--------|-------------|----------|
| `default` | Balanced physics | Most cars |
| `gt3` | High downforce, stiff suspension | GT3 race cars |
| `gt4` | Moderate downforce, balanced | GT4 race cars |
| `formula` | Very low weight, high grip | Open-wheel cars |
| `rally` | AWD drivetrain, soft suspension | Rally cars |

### Texture Quality

| Quality | Resolution | Use Case |
|---------|------------|----------|
| Low | 1024x1024 | Best performance |
| Medium | 2048x2048 | Recommended |
| High | 4096x4096 | Best quality |

---

## 📊 Supported Formats

### Input Formats

#### 3D Model Files
- **FBX** (Autodesk FBX) - Full support
- **OBJ** (Wavefront OBJ) - Full support
- **GLB** (GLTF Binary) - Full support
- **GLTF** (GL Transmission Format) - Full support

#### Sim Racing Games
- **Assetto Corsa** - Full support
  - Converts `.kn5` models (if decrypted)
  - Converts `.fbx` and `.obj` models
  - Converts physics from `physics.ini`
  - Converts textures from `.dds` files

- **rFactor 1 & 2** - Full support
  - Converts `.mas` models (if decrypted)
  - Converts `.fbx` and `.obj` models
  - Converts physics from `.gen` and `.veh` files

- **GTR2** - Full support
  - Converts `.gtr` models (if decrypted)
  - Converts physics from `physics.ini`
  - Converts car data from `car.ini`

- **Automobilista 1** - Full support
  - Converts `.ams` models (if decrypted)
  - Converts physics from `physics.ini`
  - Converts car data from `vehicle.ini`

### Output Format
- **PMR Mod**: Complete mod folder ready for installation
- **Model**: FBX format (compatible with PMR)
- **Textures**: PNG format (compatible with PMR)
- **Physics**: JSON format (PMR physics configuration)
- **Configuration**: JSON format (PMR mod configuration)

---

## 🎮 Installing Mods in PMR

### Method 1: Manual Installation
1. Navigate to your Project Motor Racing installation directory
2. Go to the `cars` folder (typically `PMR/Content/Cars`)
3. Copy the mod folder (created by PMR Forge) into the `cars` directory
4. Launch the game
5. The car should now be available in your garage

### Method 2: Using PMR Mod Manager (Recommended)
1. Open **PMR Mod Manager**
2. Click **Import Mod** or **Add Mod**
3. Select the mod folder created by PMR Forge
4. Click **Install**
5. Launch the game

---

## 🔧 Requirements

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+, Fedora, etc.)
- **Processor**: Intel Core i3 or AMD Ryzen 3 (2 GHz minimum)
- **Memory**: 4 GB RAM minimum (8 GB recommended)
- **Storage**: 2 GB free disk space
- **Graphics**: DirectX 11 or OpenGL 4.1 compatible GPU

### Software Requirements
- **Node.js**: 16.0.0 or higher (for Electron app)
- **Python**: 3.8.0 or higher (for conversion backend)
- **npm**: 7.0.0 or higher

### Python Dependencies
The following Python packages are required:
```
numpy
pillow
pygltflib
trimesh
configparser
```

These are automatically installed when you run PMR Forge for the first time.

---

## 🛠️ Building from Source

### Prerequisites
- [Node.js](https://nodejs.org/) (16.0.0+)
- [Python](https://www.python.org/) (3.8.0+)
- [Git](https://git-scm.com/)

### Build Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Lilicris12/PMR-Forge.git
   cd PMR-Forge
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Build the application**:
   ```bash
   npm run build
   ```

5. **Package for distribution** (optional):
   ```bash
   npm run package
   ```

### Platform-Specific Notes

#### Windows
- Requires Visual Studio Build Tools for native modules
- Install with: `npm install --global windows-build-tools`

#### macOS
- Requires Xcode Command Line Tools
- Install with: `xcode-select --install`

#### Linux
- Requires various development libraries
- On Ubuntu/Debian:
  ```bash
  sudo apt-get install -y build-essential libgl1-mesa-dev libx11-dev
  ```

---

## 🐛 Troubleshooting

### Common Issues

#### "Python not found"
**Solution**: Install Python 3.8 or higher from [python.org](https://www.python.org/) and make sure it's in your PATH.

#### "Missing Python dependencies"
**Solution**: Run `pip install -r requirements.txt` manually, or let PMR Forge install them automatically.

#### "Conversion failed: Unsupported format"
**Solution**: Check that your input files are valid and in a supported format. Try with a different model.

#### "No model files found"
**Solution**: Ensure your input folder contains at least one model file (FBX, OBJ, GLB, etc.).

#### "Permission denied"
**Solution**: Make sure you have write permissions for the output directory.

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 1001 | Input path not found | Check the input path exists |
| 1002 | Output path not writable | Check write permissions |
| 1003 | Python not installed | Install Python 3.8+ |
| 1004 | Missing Python dependencies | Run `pip install -r requirements.txt` |
| 2001 | Unsupported format | Use a supported format |
| 2002 | Corrupted model file | Try with a different model |
| 2003 | Missing required files | Ensure all required files are present |
| 3001 | Conversion timeout | Try with a smaller model |
| 3002 | Out of memory | Close other applications |

### Debug Mode

To run PMR Forge in debug mode:
```bash
# Windows
set NODE_ENV=development && npm start

# macOS/Linux
export NODE_ENV=development && npm start
```

This will open the developer console and show detailed logs.

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes.

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute.

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Fix issues
- 🎨 Design UI improvements
- 📦 Add support for new formats

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

### Technologies Used
- [Electron](https://www.electronjs.org/) - Cross-platform desktop framework
- [Node.js](https://nodejs.org/) - JavaScript runtime
- [Python](https://www.python.org/) - Backend processing
- [Three.js](https://threejs.org/) - 3D model preview
- [Bootstrap](https://getbootstrap.com/) - UI components (future)

### Special Thanks
- **Project Motor Racing** team for creating an amazing game
- **All sim racing communities** for their support
- **Open-source contributors** for their valuable libraries
- **You** for using PMR Forge!

---

## 🔗 Links

- 🌐 **Website**: [pmr-forge.example.com](https://pmr-forge.example.com)
- 📦 **Releases**: [GitHub Releases](https://github.com/Lilicris12/PMR-Forge/releases)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Lilicris12/PMR-Forge/issues)
- 💬 **Discord**: [Join our server](https://discord.gg/example)
- 📖 **Wiki**: [PMR Forge Wiki](https://github.com/Lilicris12/PMR-Forge/wiki)

---

## 📧 Contact

For questions, support, or feedback:

- **Email**: support@pmr-forge.example
- **Discord**: [Join our server](https://discord.gg/example)
- **GitHub**: [Open an issue](https://github.com/Lilicris12/PMR-Forge/issues)

---

**PMR Forge** - Making Project Motor Racing modding accessible to everyone! 🚗💨

*Built with ❤️ for the PMR community*
