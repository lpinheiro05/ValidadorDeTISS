document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    console.log("Formulário enviado");

    const form = event.target;
    const formData = new FormData(form);
    const resultadoDiv = document.getElementById("resultado");

    // Exibir mensagem de carregamento com spinner
    resultadoDiv.innerHTML = `
        <div class="card shadow-sm result-card">
            <div class="card-body text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Processando...</span>
                </div>
                <p class="mt-2 mb-0">Processando...</p>
            </div>
        </div>
    `;

    try {
        console.log("Enviando requisição para /processar...");
        const response = await fetch("/processar", {
            method: "POST",
            body: formData
        });

        console.log("Resposta recebida:", response.status, response.statusText);
        const data = await response.json();
        console.log("Dados recebidos:", data);

        resultadoDiv.innerHTML = "";

        if (response.ok) {
            console.log("Sucesso! Exibindo resultado...");
            resultadoDiv.innerHTML = `
                <div class="card shadow-sm result-card">
                    <div class="card-header bg-success text-white">
                        <h4 class="mb-0"><i class="bi bi-check-circle-fill me-2"></i>Resultado da Análise</h4>
                    </div>
                    <div class="card-body">
                        <h5>Pontos de não conformidade</h5>
                        <ul class="list-unstyled non-conformity">
                            ${
                                data.resultado.includes("Nenhum ponto de não conformidade identificado")
                                    ? "<li>Nenhum ponto de não conformidade identificado</li>"
                                    : data.resultado
                                        .match(/Pontos de não conformidade:([\s\S]*?)Pontos de conformidade:/)[1]
                                        .trim()
                                        .split("\n")
                                        .map(item => `<li>${item.replace(/^- /, '')}</li>`)
                                        .join("")
                            }
                        </ul>
                        <h5 class="mt-4">Pontos de conformidade</h5>
                        <ul class="list-unstyled conformity">
                            ${
                                data.resultado.includes("Nenhum ponto de conformidade identificado")
                                    ? "<li>Nenhum ponto de conformidade identificado</li>"
                                    : data.resultado
                                        .match(/Pontos de conformidade:([\s\S]*)/)[1]
                                        .trim()
                                        .split("\n")
                                        .map(item => `<li>${item.replace(/^- /, '')}</li>`)
                                        .join("")
                            }
                        </ul>
                    </div>
                </div>
            `;
        } else {
            console.log("Erro na resposta:", data.error);
            resultadoDiv.innerHTML = `
                <div class="card shadow-sm result-card">
                    <div class="card-header bg-danger text-white">
                        <h4 class="mb-0"><i class="bi bi-x-circle-fill me-2"></i>Erro</h4>
                    </div>
                    <div class="card-body">
                        <p class="card-text">${data.error || "Erro desconhecido"}</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error("Erro ao processar a requisição:", error);
        resultadoDiv.innerHTML = `
            <div class="card shadow-sm result-card">
                <div class="card-header bg-danger text-white">
                    <h4 class="mb-0"><i class="bi bi-x-circle-fill me-2"></i>Erro</h4>
                </div>
                <div class="card-body">
                    <p class="card-text">Erro ao processar os arquivos: ${error.message}</p>
                </div>
            </div>
        `;
    }
});