const byId = (id) => document.getElementById(id);

const queryInput = byId("queryInput");
const runBtn = byId("runBtn");
const clearBtn = byId("clearBtn");
const errorPanel = byId("errorPanel");

function setText(id, value) {
  byId(id).textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

function renderTokens(tokens = []) {
  const container = byId("tokens");
  container.innerHTML = "";
  tokens.forEach((token) => {
    const span = document.createElement("span");
    span.className = `token ${token.type}`;
    span.textContent = `${token.type}(${token.value})`;
    container.appendChild(span);
  });
}

function clearOutputs() {
  setText("output", "");
  byId("tokens").innerHTML = "";
  setText("symbolTable", "");
  setText("semantic", "");
  setText("intermediate", "");
  setText("optimized", "");
  setText("codeGen", "");
}

function showError(message) {
  errorPanel.classList.remove("hidden");
  errorPanel.textContent = message;
}

function hideError() {
  errorPanel.classList.add("hidden");
  errorPanel.textContent = "";
}

runBtn.addEventListener("click", async () => {
  hideError();
  const query = queryInput.value.trim();
  if (!query) {
    showError("Please enter a query");
    return;
  }

  runBtn.disabled = true;
  runBtn.textContent = "Running...";

  try {
    const response = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to process query");
    }

    setText("output", data.output);
    renderTokens(data.tokens);
    setText("symbolTable", data.symbol_table);
    setText("semantic", data.semantic);
    setText("intermediate", data.intermediate_code);
    setText("optimized", data.optimized_code);
    setText("codeGen", data.code_generation);
  } catch (err) {
    showError(err.message);
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = "▶ Run";
  }
});

clearBtn.addEventListener("click", () => {
  queryInput.value = "";
  hideError();
  clearOutputs();
});

queryInput.value = "SELECT name FROM students WHERE age > 20;";
