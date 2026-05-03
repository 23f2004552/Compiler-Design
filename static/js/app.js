window.addEventListener("load", function () {

    // ─── Sample Programs ───────────────────────────────────────────────
    const samples = {
        sample1: "let x = 5 + 3;\nlet y = x * 2;\nprint(y);",
        sample2: "let a = 10;\nif (a > 5) {\n    let b = a + 1;\n    print(b);\n} else {\n    print(a);\n} end",
        sample3: "let x@ = 5;       // '@' is illegal",
        sample4: "let x = 5\nprint(x);"
    };

    // ─── CodeMirror Setup ──────────────────────────────────────────────
    let editor = null;
    const textarea = document.getElementById("code-editor");

    if (typeof CodeMirror !== "undefined") {
        if (CodeMirror.defineSimpleMode) {
            CodeMirror.defineSimpleMode("minilang", {
                start: [
                    { regex: /(?:let|if|else|print|end)\b/, token: "keyword" },
                    { regex: /(?:\.\d+|\d+\.?\d*)(?:e[-+]?\d+)?/i, token: "number" },
                    { regex: /\/\/.*/, token: "comment" },
                    { regex: /[-+\/*=<>!]+/, token: "operator" },
                    { regex: /[a-z$][\w$]*/i, token: "variable" },
                    { regex: /[(){};]/, token: "bracket" }
                ]
            });
        }
        editor = CodeMirror.fromTextArea(textarea, {
            mode: "minilang",
            theme: "default",
            lineNumbers: true,
            matchBrackets: true,
            indentUnit: 4,
            tabSize: 4
        });
        editor.setValue(samples.sample1);
    } else {
        textarea.value = samples.sample1;
        textarea.style.cssText = "display:block;width:100%;height:100%;border:none;outline:none;font-family:'JetBrains Mono',monospace;font-size:15px;padding:16px;resize:none;background:transparent;color:inherit;";
    }

    function getSource() {
        return editor ? editor.getValue() : textarea.value;
    }

    // ─── Sample Loader ─────────────────────────────────────────────────
    document.getElementById("sample-select").addEventListener("change", function (e) {
        var code = samples[e.target.value];
        if (!code) return;
        if (editor) editor.setValue(code);
        else textarea.value = code;
    });

    // ─── Tab Switcher ──────────────────────────────────────────────────
    document.querySelectorAll(".tab-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
            document.querySelectorAll(".tab-pane").forEach(function (p) { p.classList.remove("active"); });
            btn.classList.add("active");
            document.getElementById(btn.dataset.tab + "-tab").classList.add("active");
        });
    });

    // ─── Run Compiler ──────────────────────────────────────────────────
    document.getElementById("run-btn").addEventListener("click", compileCode);

    async function compileCode() {
        var source = getSource().trim();
        if (!source) return;

        var runBtn = document.getElementById("run-btn");
        var statusMsg = document.getElementById("status-message");
        var loader = document.getElementById("spinner");

        runBtn.disabled = true;
        loader.classList.remove("hidden");
        statusMsg.textContent = "Compiling...";
        statusMsg.className = "status-text";

        try {
            var response = await fetch("/api/compile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ source: source })
            });

            if (!response.ok) throw new Error("Server error " + response.status);
            var data = await response.json();

            // ── Clear all outputs ──────────────────────────────────────
            document.querySelector("#tokens-table tbody").innerHTML = "";
            document.querySelector("#symtable-table tbody").innerHTML = "";
            document.getElementById("ast-output").textContent = "";
            document.getElementById("tac-output").innerHTML = "";
            document.getElementById("errors-output").innerHTML = "";
            document.getElementById("error-badge").classList.add("hidden");
            document.getElementById("token-stream-banner").classList.add("hidden");

            // ── Phase 1: Token Stream ──────────────────────────────────
            if (data.token_stream) {
                document.getElementById("token-stream-text").textContent = data.token_stream;
                document.getElementById("token-stream-banner").classList.remove("hidden");
            }

            if (data.tokens && data.tokens.length > 0) {
                var tbody = document.querySelector("#tokens-table tbody");
                data.tokens.forEach(function (t) {
                    var tr = document.createElement("tr");
                    tr.innerHTML =
                        "<td><code class=\"notation\">" + t.notation + "</code></td>" +
                        "<td>" + t.raw + "</td>" +
                        "<td><span class=\"type-" + t.type.toLowerCase() + "\">" + t.type + "</span></td>" +
                        "<td>" + t.line + "</td>" +
                        "<td>" + t.col + "</td>";
                    tbody.appendChild(tr);
                });
            }

            // ── Symbol Table ───────────────────────────────────────────
            if (data.symbol_table && data.symbol_table.length > 0) {
                var symTbody = document.querySelector("#symtable-table tbody");
                data.symbol_table.forEach(function (entry) {
                    var tr = document.createElement("tr");
                    tr.innerHTML =
                        "<td>" + entry.index + "</td>" +
                        "<td><strong>" + entry.name + "</strong></td>" +
                        "<td>" + entry.type + "</td>" +
                        "<td>" + entry.line + "</td>";
                    symTbody.appendChild(tr);
                });
            }

            // ── Phase 2: AST Tree ──────────────────────────────────────
            if (data.ast_tree && data.ast_tree.length > 0) {
                document.getElementById("ast-output").textContent = data.ast_tree.join("\n");
            }

            // ── Phase 3: TAC ───────────────────────────────────────────
            if (data.tac && data.tac.length > 0) {
                var tacList = document.getElementById("tac-output");
                data.tac.forEach(function (line) {
                    var li = document.createElement("li");
                    // Highlight label lines differently
                    if (line.match(/^L\d+:/)) {
                        li.className = "tac-label";
                        li.textContent = line;
                    } else {
                        li.textContent = line;
                    }
                    tacList.appendChild(li);
                });
            }

            // ── Errors ─────────────────────────────────────────────────
            if (!data.success && data.errors && data.errors.length > 0) {
                var errorList = document.getElementById("errors-output");
                data.errors.forEach(function (e) {
                    var div = document.createElement("div");
                    div.className = "error-item";
                    div.innerHTML =
                        "<div class=\"error-title\">" + e.phase + " Error</div>" +
                        "<div>" + e.message + "</div>" +
                        "<div class=\"error-location\">Line " + e.line + " : Col " + e.col + "</div>";
                    errorList.appendChild(div);
                });

                var badge = document.getElementById("error-badge");
                badge.textContent = data.errors.length;
                badge.classList.remove("hidden");
                document.querySelector("[data-tab='errors']").click();

                statusMsg.textContent = data.errors.length + " error(s) found";
                statusMsg.classList.add("error-text");
            } else {
                statusMsg.textContent = "Compiled successfully";
                statusMsg.classList.add("success-text");
                document.querySelector("[data-tab='tokens']").click();
                setTimeout(function () { statusMsg.classList.add("hidden"); }, 3000);
            }

        } catch (err) {
            statusMsg.textContent = "Error: " + err.message;
            statusMsg.classList.add("error-text");
        } finally {
            runBtn.disabled = false;
            loader.classList.add("hidden");
        }
    }
});
