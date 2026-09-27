const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { PythonShell } = require('python-shell');
const electronLog = require('electron-log');

// Configure logging
electronLog.init({ 
  logId: 'PMR-Forge',
  preload: true 
});

let mainWindow;
let conversionInProgress = false;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../../resources/icon.png'),
    title: 'PMR Forge - Car Conversion Tool'
  });

  // Load the index.html of the app
  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  // Open the DevTools in development mode
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// IPC Handlers for conversion
ipcMain.handle('start-conversion', async (event, { inputPath, outputPath, options }) => {
  if (conversionInProgress) {
    return { success: false, error: 'Conversion already in progress' };
  }

  conversionInProgress = true;
  electronLog.info(`Starting conversion: ${inputPath} -> ${outputPath}`);

  try {
    // Validate paths
    if (!fs.existsSync(inputPath)) {
      throw new Error(`Input path does not exist: ${inputPath}`);
    }

    // Create output directory
    if (!fs.existsSync(outputPath)) {
      fs.mkdirSync(outputPath, { recursive: true });
    }

    // Build conversion command
    const conversionScript = path.join(__dirname, '../backend/conversion_pipeline.py');
    
    const pythonOptions = {
      mode: 'text',
      pythonPath: 'python',
      pythonOptions: ['-u'],
      scriptPath: path.dirname(conversionScript),
      args: [
        inputPath,
        outputPath,
        JSON.stringify(options)
      ]
    };

    electronLog.info(`Executing conversion script: ${conversionScript}`);

    return new Promise((resolve, reject) => {
      const pyshell = new PythonShell('conversion_pipeline.py', pythonOptions);
      
      let outputData = '';
      let errorData = '';

      pyshell.on('message', (message) => {
        outputData += message.toString();
        electronLog.info(`Python: ${message}`);
        mainWindow.webContents.send('conversion-progress', { 
          message: message.toString(), 
          progress: -1 
        });
      });

      pyshell.on('error', (error) => {
        errorData += error.toString();
        electronLog.error(`Python error: ${error}`);
      });

      pyshell.on('close', (code) => {
        conversionInProgress = false;
        
        if (code !== 0) {
          electronLog.error(`Conversion failed with code: ${code}`);
          reject(new Error(`Conversion failed: ${errorData || 'Unknown error'}`));
        } else {
          electronLog.info('Conversion completed successfully');
          resolve({ 
            success: true, 
            output: outputData,
            outputPath 
          });
        }
      });

      pyshell.end((err) => {
        if (err) {
          electronLog.error(`Shell end error: ${err}`);
          reject(err);
        }
      });
    });

  } catch (error) {
    conversionInProgress = false;
    electronLog.error(`Conversion error: ${error.message}`);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('select-input-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Select Input Folder (Car Model Files)'
  });
  return result.filePaths[0] || null;
});

ipcMain.handle('select-output-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Select Output Folder (PMR Mod Destination)'
  });
  return result.filePaths[0] || null;
});

ipcMain.handle('get-supported-formats', () => {
  return {
    formats: [
      'OBJ', 'FBX', 'GLB', 
      'Assetto Corsa', 'rFactor', 
      'GTR2', 'Automobilista 1'
    ],
    description: 'Supported input formats for car model conversion'
  };
});

ipcMain.handle('check-python', async () => {
  try {
    const { PythonShell } = require('python-shell');
    const pyshell = new PythonShell('-c "import sys; print(sys.version)"');
    
    return new Promise((resolve) => {
      let version = '';
      pyshell.on('message', (message) => {
        version = message.toString().trim();
      });
      
      pyshell.on('close', () => {
        resolve({ available: true, version });
      });
      
      pyshell.on('error', () => {
        resolve({ available: false, version: null });
      });
    });
  } catch (error) {
    return { available: false, version: null, error: error.message };
  }
});

// Check for required dependencies
ipcMain.handle('check-dependencies', async () => {
  const checks = {
    python: false,
    blender: false,
    assettoCorsaTools: false,
    allRequired: false
  };

  // Check Python
  try {
    const pythonCheck = await ipcMain.invokeHandler('check-python');
    checks.python = pythonCheck.available;
  } catch (error) {
    checks.python = false;
  }

  // For now, we'll assume blender and AC tools might be available
  // In a real implementation, we'd check for these
  checks.blender = true; // Placeholder
  checks.assettoCorsaTools = true; // Placeholder
  
  checks.allRequired = checks.python && checks.blender;
  
  return checks;
});

// Handle window controls
ipcMain.on('minimize-window', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
});

ipcMain.on('maximize-window', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.on('close-window', () => {
  if (mainWindow) {
    mainWindow.close();
  }
});

// App ready
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Log unhandled errors
electronLog.catchErrors({
  onError: (error) => {
    electronLog.error('Unhandled error:', error);
  }
});

console.log('PMR Forge main process started');
