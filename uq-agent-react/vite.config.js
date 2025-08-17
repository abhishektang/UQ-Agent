import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import { resolve } from 'path';
import fs from 'fs/promises';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-files',
      async closeBundle() {
        try {
          // Create dist directory if it doesn't exist
          await fs.mkdir('dist', { recursive: true });
          
          // Copy files
          await Promise.all([
            fs.copyFile('src/contentScript.js', 'dist/contentScript.js'),
            fs.copyFile('manifest.json', 'dist/manifest.json'),
            copyDir('assets', 'dist/assets')
          ]);
          
          console.log('Files copied successfully');
        } catch (err) {
          console.error('Error copying files:', err);
        }
      }
    }
  ],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        contentScript: resolve(__dirname, 'src/contentScript.js')
      }
    }
  }
});

// Helper function to copy directories
async function copyDir(src, dest) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });
  
  for (let entry of entries) {
    const srcPath = resolve(src, entry.name);
    const destPath = resolve(dest, entry.name);
    
    entry.isDirectory() 
      ? await copyDir(srcPath, destPath)
      : await fs.copyFile(srcPath, destPath);
  }
}