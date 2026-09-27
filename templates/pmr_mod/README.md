# {{MOD_NAME}}

A car mod for **Project Motor Racing**, converted using **PMR Forge**.

---

## 📋 Mod Information

| Property | Value |
|----------|-------|
| **Version** | {{MOD_VERSION}} |
| **Author** | {{MOD_AUTHOR}} |
| **Conversion Date** | {{CREATION_DATE}} |
| **Source Format** | {{SOURCE_FORMAT}} |
| **PMR Forge Version** | 1.0.0 |

---

## 🚗 Car Specifications

### Performance
- **Mass**: {{MASS}} kg
- **Power**: {{MAX_POWER}} HP
- **Max RPM**: {{MAX_RPM}}
- **Top Speed**: ~{{TOP_SPEED}} km/h (estimated)
- **0-100 km/h**: ~{{ACCELERATION}} s (estimated)

### Dimensions
- **Length**: {{LENGTH}} m
- **Width**: {{WIDTH}} m
- **Height**: {{HEIGHT}} m
- **Wheelbase**: {{WHEELBASE}} m

### Drivetrain
- **Type**: {{DRIVETRAIN_TYPE}}
- **Transmission**: {{TRANSMISSION_TYPE}}
- **Gears**: {{NUM_GEARS}}

---

## 🎮 Features

### ✅ Included
- ✅ 3D Model ({{MAIN_MODEL}})
{% if GENERATE_PHYSICS %}- ✅ Physics Configuration
{% endif %}{% if CREATE_LODS %}- ✅ Level of Detail (LOD) Models
{% endif %}{% if CONVERT_TEXTURES %}- ✅ Converted Textures ({{TEXTURE_QUALITY}})
{% endif %}{% if INCLUDE_INTERIOR %}- ✅ Interior Model
{% endif %}{% if GENERATE_SOUNDS %}- ✅ Sound Effects
{% endif %}

### ❌ Not Included
{% if not GENERATE_PHYSICS %}- ❌ Physics Configuration (use default)
{% endif %}{% if not CREATE_LODS %}- ❌ Level of Detail Models
{% endif %}{% if not CONVERT_TEXTURES %}- ❌ Texture Conversion
{% endif %}{% if not INCLUDE_INTERIOR %}- ❌ Interior Model
{% endif %}{% if not GENERATE_SOUNDS %}- ❌ Sound Effects
{% endif %}

---

## 📁 Installation

### Method 1: Manual Installation
1. Navigate to your **Project Motor Racing** installation directory
2. Go to the `cars` folder
3. Copy the `{{MOD_NAME}}` folder into the `cars` directory
4. Launch the game
5. The car should now be available in your garage

### Method 2: Using PMR Mod Manager (Recommended)
1. Open **PMR Mod Manager**
2. Click **Import Mod**
3. Select the `{{MOD_NAME}}` folder
4. Click **Install**
5. Launch the game

---

## ⚙️ Configuration

### Mod Settings
You can customize the mod by editing the following files:

- **`mod.json`** - Mod metadata and compatibility
- **`car.json`** - Car appearance and behavior settings
- **`physics/physics.json`** - Physics parameters

### Recommended Tweaks

#### For Better Performance
```json
// In car.json
"performance": {
  "render_priority": 1,
  "cull_distance": 300.0
}
```

#### For More Realistic Handling
```json
// In physics/physics.json
"suspension": {
  "front": {
    "spring_rate": 150000.0,
    "damping": 15000.0
  },
  "rear": {
    "spring_rate": 170000.0,
    "damping": 17000.0
  }
}
```

---

## 🎨 Textures

The mod includes the following textures:
- **Diffuse**: Base color
- **Normal**: Surface normals for lighting
- **Specular**: Reflectivity
- **Emissive**: Glowing parts (if applicable)
- **Ambient Occlusion**: Shadow details

**Texture Quality**: {{TEXTURE_QUALITY}}
- **Low**: 1024x1024 (Best performance)
- **Medium**: 2048x2048 (Recommended)
- **High**: 4096x4096 (Best quality)

---

## 🔧 Physics Preset

**Current Preset**: {{PHYSICS_PRESET}}

| Preset | Description |
|--------|-------------|
| `default` | Balanced physics for most cars |
| `gt3` | GT3 racing car physics |
| `gt4` | GT4 racing car physics |
| `formula` | Open-wheel formula car physics |
| `rally` | Rally car physics with AWD |

---

## 📊 Conversion Details

### Source Information
- **Original Format**: {{SOURCE_FORMAT}}
- **Input Path**: {{INPUT_PATH}}
- **Scale Factor**: {{SCALE_FACTOR}}

### Conversion Options
```json
{
  "convert_textures": {{CONVERT_TEXTURES}},
  "generate_physics": {{GENERATE_PHYSICS}},
  "create_lods": {{CREATE_LODS}},
  "optimize_model": {{OPTIMIZE_MODEL}},
  "include_interior": {{INCLUDE_INTERIOR}},
  "generate_sounds": {{GENERATE_SOUNDS}}
}
```

---

## ⚠️ Known Issues

- Some features may not work perfectly due to automatic conversion
- Interior camera position may need manual adjustment
- Physics may require fine-tuning for realistic behavior
- Certain game-specific effects might be missing

---

## 🙏 Credits

- **Original Car Model**: [Original Author]
- **Conversion Tool**: PMR Forge
- **Special Thanks**: Project Motor Racing community

---

## 📜 License

This mod is provided as-is. Please respect the original author's rights.

**Redistribution**: Allowed with permission
**Modification**: Allowed
**Commercial Use**: Not allowed without explicit permission

---

## 🔗 Links

- [PMR Forge GitHub](https://github.com/Lilicris12/PMR-Forge)
- [Project Motor Racing](https://pmr-game.com)
- [PMR Modding Wiki](https://wiki.pmr-game.com)

---

*This README was generated automatically by PMR Forge*
