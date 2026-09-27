// PMR Forge - Main Application JavaScript

// Global state
let currentInputPath = null;
let currentOutputPath = null;
let conversionInProgress = false;

// DOM Elements
const inputPathEl = document.getElementById('inputPath');
const outputPathEl = document.getElementById('outputPath');
const modNameEl = document.getElementById('modName');
const modVersionEl = document.getElementById('modVersion');
const modAuthorEl = document.getElementById('modAuthor');
const convertBtn = document.getElementById('convertBtn');
const convertBtnText = document.getElementById('convertBtnText');
const convertBtnLoading = document.getElementById('convertBtnLoading');
const progressPanel = document.getElementById('progressPanel');
const conversionPanel = document.querySelector('.conversion-panel');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const progressPercent = document.getElementById('progressPercent');
const progressLog = document.getElementById('progressLog');
const successPanel = document.getElementById('successPanel');
const successMessage = document.getElementById('successMessage');
const detectedFormatGroup = document.getElementById('detectedFormatGroup');
const detectedFormat = document.getElementById('detectedFormat');
const pythonStatus = document.getElementById('pythonStatus');
const dependenciesStatus = document.getElementById('dependenciesStatus');
const toastContainer = document.getElementById('toastContainer');

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    console.log('PMR Forge initializing...');
    
    // Check dependencies
    await checkDependencies();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load saved settings
    loadSettings();
    
    console.log('PMR Forge initialized');
});

// Setup event listeners
function setupEventListeners() {
    // Input path change
    inputPathEl.addEventListener('input', () => {
        currentInputPath = inputPathEl.value;
        updateConvertButton();
        detectFormat(currentInputPath);
    });
    
    outputPathEl.addEventListener('input', () => {
        currentOutputPath = outputPathEl.value;
        updateConvertButton();
    });
    
    // Progress updates from main process
    window.pmrForge.onConversionProgress((data) => {
        updateProgress(data);
    });
    
    // Form input validation
    [modNameEl, modVersionEl, modAuthorEl].forEach(el => {
        el.addEventListener('input', saveSettings);
    });
    
    // Checkbox changes
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', saveSettings);
    });
    
    // Select changes
    document.querySelectorAll('select').forEach(select => {
        select.addEventListener('change', saveSettings);
    });
}

// Check dependencies
async function checkDependencies() {
    try {
        console.log('Checking Python...');
        const pythonCheck = await window.pmrForge.checkPython();
        
        if (pythonCheck.available) {
            pythonStatus.textContent = `Python ${pythonCheck.version}`;
            pythonStatus.style.color = '#10B981';
        } else {
            pythonStatus.textContent = 'Python not found';
            pythonStatus.style.color = '#EF4444';
            showToast('Python is required but not found. Please install Python 3.8+', 'error');
        }
        
        console.log('Checking all dependencies...');
        const depsCheck = await window.pmrForge.checkDependencies();
        
        if (depsCheck.allRequired) {
            dependenciesStatus.textContent = 'All dependencies ready';
            dependenciesStatus.style.color = '#10B981';
        } else {
            dependenciesStatus.textContent = 'Missing dependencies';
            dependenciesStatus.style.color = '#EF4444';
        }
        
    } catch (error) {
        console.error('Error checking dependencies:', error);
        pythonStatus.textContent = 'Error checking Python';
        dependenciesStatus.textContent = 'Error checking dependencies';
    }
}

// Select input folder
async function selectInputFolder() {
    try {
        const path = await window.pmrForge.selectInputFolder();
        if (path) {
            currentInputPath = path;
            inputPathEl.value = path;
            updateConvertButton();
            detectFormat(path);
            saveSettings();
        }
    } catch (error) {
        console.error('Error selecting input folder:', error);
        showToast('Error selecting folder: ' + error.message, 'error');
    }
}

// Select output folder
async function selectOutputFolder() {
    try {
        const path = await window.pmrForge.selectOutputFolder();
        if (path) {
            currentOutputPath = path;
            outputPathEl.value = path;
            updateConvertButton();
            saveSettings();
        }
    } catch (error) {
        console.error('Error selecting output folder:', error);
        showToast('Error selecting folder: ' + error.message, 'error');
    }
}

// Detect format from input path
function detectFormat(path) {
    if (!path) {
        detectedFormatGroup.style.display = 'none';
        return;
    }
    
    // Simple detection based on folder contents or path
    const lowerPath = path.toLowerCase();
    
    // Check for known game folders
    if (lowerPath.includes('assettocorsa') || lowerPath.includes('ac')) {
        detectedFormat.textContent = 'Assetto Corsa';
        detectedFormatGroup.style.display = 'block';
        return;
    }
    
    if (lowerPath.includes('rfactor') || lowerPath.includes('rf1') || lowerPath.includes('rf2')) {
        detectedFormat.textContent = 'rFactor';
        detectedFormatGroup.style.display = 'block';
        return;
    }
    
    if (lowerPath.includes('gtr2')) {
        detectedFormat.textContent = 'GTR2';
        detectedFormatGroup.style.display = 'block';
        return;
    }
    
    if (lowerPath.includes('automobilista') || lowerPath.includes('ams') || lowerPath.includes('ams1')) {
        detectedFormat.textContent = 'Automobilista 1';
        detectedFormatGroup.style.display = 'block';
        return;
    }
    
    // Check for file extensions in the folder (this would be more accurate with actual file checking)
    // For now, we'll just show a generic message
    detectedFormat.textContent = 'Multiple files (auto-detect)';
    detectedFormatGroup.style.display = 'block';
}

// Update convert button state
function updateConvertButton() {
    const hasInput = currentInputPath && currentInputPath.trim() !== '';
    const hasOutput = currentOutputPath && currentOutputPath.trim() !== '';
    const hasName = modNameEl.value.trim() !== '';
    
    const canConvert = hasInput && hasOutput && hasName && !conversionInProgress;
    
    convertBtn.disabled = !canConvert;
}

// Start conversion
async function startConversion() {
    if (conversionInProgress) return;
    
    conversionInProgress = true;
    
    // Show progress panel
    conversionPanel.style.display = 'none';
    progressPanel.style.display = 'block';
    successPanel.style.display = 'none';
    
    // Update button state
    convertBtnText.style.display = 'none';
    convertBtnLoading.style.display = 'inline-block';
    
    // Reset progress
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';
    progressLog.textContent = '';
    
    // Get options
    const options = {
        modName: modNameEl.value.trim(),
        modVersion: modVersionEl.value.trim(),
        modAuthor: modAuthorEl.value.trim(),
        convertTextures: document.getElementById('convertTextures').checked,
        generatePhysics: document.getElementById('generatePhysics').checked,
        createLODs: document.getElementById('createLODs').checked,
        optimizeModel: document.getElementById('optimizeModel').checked,
        includeInterior: document.getElementById('includeInterior').checked,
        generateSounds: document.getElementById('generateSounds').checked,
        scaleFactor: parseFloat(document.getElementById('scaleFactor').value),
        textureQuality: document.getElementById('textureQuality').value,
        physicsPreset: document.getElementById('physicsPreset').value
    };
    
    console.log('Starting conversion with options:', options);
    
    // Log initial message
    addProgressLog('Starting conversion...\n');
    addProgressLog(`Input: ${currentInputPath}\n`);
    addProgressLog(`Output: ${currentOutputPath}\n`);
    addProgressLog(`Mod: ${options.modName} v${options.modVersion}\n\n`);
    
    try {
        const result = await window.pmrForge.startConversion(
            currentInputPath, 
            currentOutputPath, 
            options
        );
        
        if (result.success) {
            // Conversion successful
            showSuccess(result);
        } else {
            // Conversion failed
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Conversion failed:', error);
        showToast('Conversion failed: ' + error.message, 'error');
        
        // Reset UI
        resetConversionUI();
    }
}

// Update progress
function updateProgress(data) {
    if (data.progress >= 0) {
        progressFill.style.width = `${data.progress}%`;
        progressPercent.textContent = `${Math.round(data.progress)}%`;
    }
    
    if (data.message) {
        addProgressLog(data.message);
    }
}

// Add message to progress log
function addProgressLog(message) {
    progressLog.textContent += message;
    progressLog.scrollTop = progressLog.scrollHeight;
}

// Show success panel
function showSuccess(result) {
    conversionInProgress = false;
    
    // Hide progress, show success
    progressPanel.style.display = 'none';
    successPanel.style.display = 'block';
    
    // Update success message
    successMessage.textContent = `Your PMR mod "${document.getElementById('modName').value}" has been successfully created and is ready to install!`;
    
    // Reset button
    convertBtnText.style.display = 'inline';
    convertBtnLoading.style.display = 'none';
    
    // Save settings for next conversion
    saveSettings();
    
    console.log('Conversion successful:', result);
}

// Reset conversion UI
function resetConversionUI() {
    conversionInProgress = false;
    
    // Reset panels
    progressPanel.style.display = 'none';
    successPanel.style.display = 'none';
    conversionPanel.style.display = 'block';
    
    // Reset button
    convertBtnText.style.display = 'inline';
    convertBtnLoading.style.display = 'none';
    
    updateConvertButton();
}

// Reset form
function resetForm() {
    resetConversionUI();
    
    // Clear inputs
    inputPathEl.value = '';
    outputPathEl.value = '';
    modNameEl.value = '';
    modVersionEl.value = '1.0.0';
    modAuthorEl.value = '';
    
    currentInputPath = null;
    currentOutputPath = null;
    
    // Reset checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = true;
    });
    
    // Reset selects
    document.getElementById('textureQuality').value = 'medium';
    document.getElementById('physicsPreset').value = 'default';
    document.getElementById('scaleFactor').value = '1.0';
    
    // Hide detected format
    detectedFormatGroup.style.display = 'none';
    
    updateConvertButton();
}

// Open output folder
function openOutputFolder() {
    if (currentOutputPath) {
        // In a real implementation, we'd use the shell API to open the folder
        // For now, we'll just show a toast
        showToast(`Output folder: ${currentOutputPath}`, 'success');
    }
}

// Cancel conversion
function cancelConversion() {
    // In a real implementation, we'd send a cancel signal to the conversion process
    showToast('Cancelling conversion...', 'warning');
    
    // For now, just reset the UI
    setTimeout(() => {
        resetConversionUI();
        showToast('Conversion cancelled', 'warning');
    }, 1000);
}

// Toggle advanced options
function toggleAdvancedOptions() {
    const content = document.getElementById('advancedContent');
    const toggleText = document.getElementById('advancedToggleText');
    const icon = document.querySelector('#advancedToggleText + .icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggleText.textContent = 'Hide Advanced Options';
        icon.textContent = '🔼';
    } else {
        content.style.display = 'none';
        toggleText.textContent = 'Show Advanced Options';
        icon.textContent = '🔽';
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = document.createElement('span');
    icon.className = 'toast-icon';
    icon.textContent = type === 'success' ? '✓' : 
                      type === 'error' ? '✗' : 
                      type === 'warning' ? '⚠' : 'ℹ';
    
    const text = document.createElement('span');
    text.textContent = message;
    
    toast.appendChild(icon);
    toast.appendChild(text);
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}

// Save settings to localStorage
function saveSettings() {
    const settings = {
        inputPath: inputPathEl.value,
        outputPath: outputPathEl.value,
        modName: modNameEl.value,
        modVersion: modVersionEl.value,
        modAuthor: modAuthorEl.value,
        convertTextures: document.getElementById('convertTextures').checked,
        generatePhysics: document.getElementById('generatePhysics').checked,
        createLODs: document.getElementById('createLODs').checked,
        optimizeModel: document.getElementById('optimizeModel').checked,
        includeInterior: document.getElementById('includeInterior').checked,
        generateSounds: document.getElementById('generateSounds').checked,
        scaleFactor: document.getElementById('scaleFactor').value,
        textureQuality: document.getElementById('textureQuality').value,
        physicsPreset: document.getElementById('physicsPreset').value
    };
    
    localStorage.setItem('pmrForgeSettings', JSON.stringify(settings));
    console.log('Settings saved');
}

// Load settings from localStorage
function loadSettings() {
    const saved = localStorage.getItem('pmrForgeSettings');
    
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            
            // Restore form values
            if (settings.inputPath) {
                inputPathEl.value = settings.inputPath;
                currentInputPath = settings.inputPath;
            }
            if (settings.outputPath) {
                outputPathEl.value = settings.outputPath;
                currentOutputPath = settings.outputPath;
            }
            if (settings.modName) modNameEl.value = settings.modName;
            if (settings.modVersion) modVersionEl.value = settings.modVersion;
            if (settings.modAuthor) modAuthorEl.value = settings.modAuthor;
            
            // Restore checkboxes
            if (settings.convertTextures !== undefined) 
                document.getElementById('convertTextures').checked = settings.convertTextures;
            if (settings.generatePhysics !== undefined) 
                document.getElementById('generatePhysics').checked = settings.generatePhysics;
            if (settings.createLODs !== undefined) 
                document.getElementById('createLODs').checked = settings.createLODs;
            if (settings.optimizeModel !== undefined) 
                document.getElementById('optimizeModel').checked = settings.optimizeModel;
            if (settings.includeInterior !== undefined) 
                document.getElementById('includeInterior').checked = settings.includeInterior;
            if (settings.generateSounds !== undefined) 
                document.getElementById('generateSounds').checked = settings.generateSounds;
            
            // Restore selects and inputs
            if (settings.scaleFactor) 
                document.getElementById('scaleFactor').value = settings.scaleFactor;
            if (settings.textureQuality) 
                document.getElementById('textureQuality').value = settings.textureQuality;
            if (settings.physicsPreset) 
                document.getElementById('physicsPreset').value = settings.physicsPreset;
            
            // Update UI
            updateConvertButton();
            detectFormat(currentInputPath);
            
            console.log('Settings loaded');
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
}

// Open settings modal
function openSettings() {
    showToast('Settings panel coming soon!', 'info');
}

// Open help
function openHelp() {
    showToast('Help documentation coming soon!', 'info');
}

// Open about
function openAbout() {
    showToast('PMR Forge v1.0.0 - Car Conversion Tool', 'info');
}

// Open documentation
function openDocumentation() {
    showToast('Documentation coming soon!', 'info');
}

// Make functions globally available for HTML onclick handlers
window.selectInputFolder = selectInputFolder;
window.selectOutputFolder = selectOutputFolder;
window.startConversion = startConversion;
window.openOutputFolder = openOutputFolder;
window.cancelConversion = cancelConversion;
window.toggleAdvancedOptions = toggleAdvancedOptions;
window.openSettings = openSettings;
window.openHelp = openHelp;
window.openAbout = openAbout;
window.openDocumentation = openDocumentation;
window.resetForm = resetForm;
