/**
 * cli.js
 * Handles the in-page CLI terminal for graph manipulation commands.
 */

const cliInput = document.getElementById('cli-input');
const cliOutput = document.getElementById('cli-output');
const cliRunBtn = document.getElementById('btn-cli-run');

function cliPrint(text, isError = false) {
    const line = document.createElement('div');
    line.className = isError ? 'cli-line cli-error' : 'cli-line';
    line.textContent = text;
    cliOutput.appendChild(line);
    cliOutput.scrollTop = cliOutput.scrollHeight;
}

async function runCommand(command) {
    if (!command.trim()) return;
    cliPrint(`> ${command}`);

    if (!currentWorkspaceId) {
        cliPrint('No workspace loaded. Load a graph first.', true);
        return;
    }

    try {
        const result = await API.runCli(currentWorkspaceId, command);
        if (result.error) {
            cliPrint(result.error, true);
        } else {
            cliPrint(result.message || 'OK');
            // Re-render graph after mutation commands
            if (['create', 'edit', 'delete'].some(cmd => command.startsWith(cmd))) {
                await renderGraph(currentWorkspaceId);
            }
        }
    } catch (e) {
        cliPrint(`Error: ${e.message}`, true);
    }
}

cliRunBtn?.addEventListener('click', () => {
    runCommand(cliInput.value);
    cliInput.value = '';
});

cliInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        runCommand(cliInput.value);
        cliInput.value = '';
    }
});