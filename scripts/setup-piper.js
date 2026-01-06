#!/usr/bin/env node
/**
 * FLUXION - Piper TTS Setup Script
 * Downloads Piper binary and Italian voice for all platforms
 *
 * Usage: node scripts/setup-piper.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');

const PIPER_VERSION = 'v2023.11.14-2';
const VOICE_NAME = 'it_IT-paola-medium';

// Platform-specific URLs
const PIPER_RELEASES = {
  darwin: {
    x64: `https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_macos_x64.tar.gz`,
    arm64: `https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_macos_aarch64.tar.gz`,
  },
  win32: {
    x64: `https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_windows_amd64.zip`,
  },
  linux: {
    x64: `https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_linux_x86_64.tar.gz`,
    arm64: `https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_linux_aarch64.tar.gz`,
  },
};

const VOICE_URL = `https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/${VOICE_NAME}.onnx`;
const VOICE_CONFIG_URL = `https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/${VOICE_NAME}.onnx.json`;

const PIPER_DIR = path.join(__dirname, '..', 'piper');
const VOICES_DIR = path.join(PIPER_DIR, 'voices');

function getPlatformUrl() {
  const platform = process.platform;
  const arch = process.arch;

  if (!PIPER_RELEASES[platform]) {
    console.error(`Unsupported platform: ${platform}`);
    process.exit(1);
  }

  const url = PIPER_RELEASES[platform][arch];
  if (!url) {
    console.error(`Unsupported architecture: ${arch} on ${platform}`);
    process.exit(1);
  }

  return url;
}

function downloadFile(url, destPath) {
  return new Promise((resolve, reject) => {
    console.log(`Downloading: ${url}`);
    const file = fs.createWriteStream(destPath);

    https.get(url, (response) => {
      // Handle redirects
      if (response.statusCode === 302 || response.statusCode === 301) {
        file.close();
        fs.unlinkSync(destPath);
        return downloadFile(response.headers.location, destPath).then(resolve).catch(reject);
      }

      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }

      const totalSize = parseInt(response.headers['content-length'], 10);
      let downloaded = 0;

      response.on('data', (chunk) => {
        downloaded += chunk.length;
        const percent = totalSize ? Math.round((downloaded / totalSize) * 100) : '?';
        process.stdout.write(`\rProgress: ${percent}%`);
      });

      response.pipe(file);

      file.on('finish', () => {
        file.close();
        console.log('\nDownload complete!');
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(destPath, () => {});
      reject(err);
    });
  });
}

async function extractArchive(archivePath, destDir) {
  const ext = path.extname(archivePath);

  if (ext === '.gz' || archivePath.endsWith('.tar.gz')) {
    console.log('Extracting tar.gz...');
    execSync(`tar -xzf "${archivePath}" -C "${destDir}"`, { stdio: 'inherit' });
  } else if (ext === '.zip') {
    console.log('Extracting zip...');
    if (process.platform === 'win32') {
      execSync(`powershell -command "Expand-Archive -Path '${archivePath}' -DestinationPath '${destDir}' -Force"`, { stdio: 'inherit' });
    } else {
      execSync(`unzip -o "${archivePath}" -d "${destDir}"`, { stdio: 'inherit' });
    }
  }
}

async function main() {
  console.log('='.repeat(50));
  console.log('FLUXION - Piper TTS Setup');
  console.log('='.repeat(50));
  console.log(`Platform: ${process.platform}`);
  console.log(`Architecture: ${process.arch}`);
  console.log('');

  // Create directories
  if (!fs.existsSync(PIPER_DIR)) {
    fs.mkdirSync(PIPER_DIR, { recursive: true });
  }
  if (!fs.existsSync(VOICES_DIR)) {
    fs.mkdirSync(VOICES_DIR, { recursive: true });
  }

  // Check if Piper already installed
  const piperBinary = process.platform === 'win32' ? 'piper.exe' : 'piper';
  const piperPath = path.join(PIPER_DIR, 'piper', piperBinary);

  if (fs.existsSync(piperPath)) {
    console.log('Piper already installed, skipping binary download.');
  } else {
    // Download Piper binary
    const piperUrl = getPlatformUrl();
    const archiveExt = piperUrl.endsWith('.zip') ? '.zip' : '.tar.gz';
    const archivePath = path.join(PIPER_DIR, `piper${archiveExt}`);

    try {
      await downloadFile(piperUrl, archivePath);
      await extractArchive(archivePath, PIPER_DIR);
      fs.unlinkSync(archivePath); // Cleanup archive

      // Make executable on Unix
      if (process.platform !== 'win32') {
        const extractedPiper = path.join(PIPER_DIR, 'piper', 'piper');
        if (fs.existsSync(extractedPiper)) {
          fs.chmodSync(extractedPiper, '755');
        }
      }

      console.log('Piper binary installed!');
    } catch (err) {
      console.error('Failed to install Piper binary:', err.message);
      console.log('You can manually download from: https://github.com/rhasspy/piper/releases');
    }
  }

  // Download Italian voice
  const voicePath = path.join(VOICES_DIR, `${VOICE_NAME}.onnx`);
  const voiceConfigPath = path.join(VOICES_DIR, `${VOICE_NAME}.onnx.json`);

  if (fs.existsSync(voicePath) && fs.existsSync(voiceConfigPath)) {
    console.log('Italian voice already installed, skipping.');
  } else {
    console.log('\nDownloading Italian voice (Paola - medium quality)...');
    try {
      await downloadFile(VOICE_URL, voicePath);
      await downloadFile(VOICE_CONFIG_URL, voiceConfigPath);
      console.log('Italian voice installed!');
    } catch (err) {
      console.error('Failed to download voice:', err.message);
    }
  }

  // Create config file
  const configPath = path.join(PIPER_DIR, 'config.json');
  const config = {
    piper_path: path.join(PIPER_DIR, 'piper', piperBinary),
    voice_path: voicePath,
    voice_config: voiceConfigPath,
    voice_name: VOICE_NAME,
    sample_rate: 22050,
  };
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

  console.log('\n' + '='.repeat(50));
  console.log('Setup complete!');
  console.log('='.repeat(50));
  console.log(`Piper binary: ${piperPath}`);
  console.log(`Voice model: ${voicePath}`);
  console.log(`Config: ${configPath}`);
}

main().catch(console.error);
