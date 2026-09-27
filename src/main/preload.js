const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'pmrForge', {
    // Conversion API
    startConversion: (inputPath, outputPath, options) => 
      ipcRenderer.invoke('start-conversion', { inputPath, outputPath, options }),
    
    // Dialog API
    selectInputFolder: () => ipcRenderer.invoke('select-input-folder'),
    selectOutputFolder: () => ipcRenderer.invoke('select-output-folder'),
    
    // Info API
    getSupportedFormats: () => ipcRenderer.invoke('get-supported-formats'),
    checkDependencies: () => ipcRenderer.invoke('check-dependencies'),
    checkPython: () => ipcRenderer.invoke('check-python'),
    
    // Window controls
    minimizeWindow: () => ipcRenderer.send('minimize-window'),
    maximizeWindow: () => ipcRenderer.send('maximize-window'),
    closeWindow: () => ipcRenderer.send('close-window'),
    
    // Progress updates
    onConversionProgress: (callback) => 
      ipcRenderer.on('conversion-progress', (event, data) => callback(data)),
    
    // Remove listener
    removeConversionProgress: () => 
      ipcRenderer.removeAllListeners('conversion-progress')
  }
);

console.log('PMR Forge preload script loaded');
