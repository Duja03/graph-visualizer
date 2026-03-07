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

function cliPrintPre(text) {
    const line = document.createElement('pre');
    line.className = 'cli-line';
    line.textContent = text;
    cliOutput.appendChild(line);
    cliOutput.scrollTop = cliOutput.scrollHeight;
}

async function runCommand(command) {
    if (!command.trim()) return;
    cliPrint(`> ${command}`);

    if (command.trim() === 'clear') {
        cliOutput.innerHTML = '';
        return;
    }

    if (command.trim() === 'help') {
        cliHelp();
        return;
    }

    if (!State.currentWorkspaceId) {
        cliPrint('No workspace loaded. Load a graph first.', true);
        return;
    }

    let result;
    try {
        result = await API.runCli(State.currentWorkspaceId, command);
    } catch (e) {
        cliPrint(`Network error: ${e.message}`, true);
        return;
    }

    if (result.error) {
        cliPrint(result.error, true);
        return;
    }

    cliPrint('OK');

    if (['create', 'edit', 'delete', 'filter', 'search'].some(cmd => command.trim().startsWith(cmd))) {
        try {
            await renderGraph(State.currentWorkspaceId);
        } catch (e) {
            console.warn('Re-render failed after CLI command:', e);
        }
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

function cliHelp() {
    cliPrintPre(`
NODE
  create node --id=<id> [--attribute <name>=<value> ...]
  edit node --id=<id> --attribute <name>=<value> [...]
  delete node --id=<id>

EDGE
  create edge --id=<id> --source=<id> --target=<id> [--attribute <name>=<value> ...]
  edit edge --id=<id> --attribute <name>=<value> [...]
  delete edge --id=<id>

GRAPH
  delete graph

FILTER
  filter <attribute><operator><value>   (operators: == != > >= < <=)

SEARCH
  search <query>

OTHER
  help
  clear
    `.trim());
}