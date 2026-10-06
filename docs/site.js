// SPDX-License-Identifier: MIT
'use strict';
const command = document.getElementById('download-command');
const copyStatus = document.getElementById('copy-status');
const commands = {
  windows: 'git clone https://github.com/zubSero/StremioBox.git\ncd StremioBox\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/download.ps1 -OutputDirectory downloads',
  linux: 'git clone https://github.com/zubSero/StremioBox.git\ncd StremioBox\nbash tools/download.sh --output downloads'
};
document.querySelectorAll('[data-platform]').forEach(button => {
  button.addEventListener('click', () => {
    command.textContent = commands[button.dataset.platform];
    copyStatus.textContent = '';
    document.querySelectorAll('[data-platform]').forEach(tab => {
      const selected = tab === button;
      tab.classList.toggle('active', selected);
      tab.setAttribute('aria-pressed', String(selected));
    });
  });
});
document.getElementById('copy-command').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(command.textContent);
    copyStatus.textContent = 'Commands copied.';
  } catch {
    copyStatus.textContent = 'Select the commands above and copy them manually.';
  }
});
