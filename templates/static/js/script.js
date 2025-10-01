// Funcionalidades JavaScript para melhor UX
document.addEventListener('DOMContentLoaded', function() {
    
    // Exemplos rápidos
    const botoesExemplo = document.querySelectorAll('.usar-exemplo');
    botoesExemplo.forEach(botao => {
        botao.addEventListener('click', function() {
            const texto = this.getAttribute('data-texto');
            document.getElementById('texto_direto').value = texto;
            
            // Ativa a aba de texto
            const textoTab = new bootstrap.Tab(document.getElementById('text-tab'));
            textoTab.show();
            
            // Scroll suave para o textarea
            document.getElementById('texto_direto').scrollIntoView({ 
                behavior: 'smooth' 
            });
        });
    });

    // Validação de arquivo
    const inputArquivo = document.getElementById('arquivo');
    if (inputArquivo) {
        inputArquivo.addEventListener('change', function(e) {
            const arquivo = e.target.files[0];
            if (arquivo) {
                const tamanhoMaximo = 5 * 1024 * 1024; // 5MB
                if (arquivo.size > tamanhoMaximo) {
                    alert('Arquivo muito grande! Por favor, selecione um arquivo menor que 5MB.');
                    e.target.value = '';
                }
                
                // Mostra o nome do arquivo
                const label = this.nextElementSibling;
                if (label && label.classList.contains('form-text')) {
                    label.textContent = `Arquivo selecionado: ${arquivo.name} (${(arquivo.size / 1024 / 1024).toFixed(2)} MB)`;
                    label.classList.add('text-success', 'fw-bold');
                }
            }
        });
    }

    // Efeitos visuais
    const botoes = document.querySelectorAll('.btn');
    botoes.forEach(botao => {
        botao.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        botao.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Auto-focus no textarea quando a aba é ativada
    const textTab = document.getElementById('text-tab');
    if (textTab) {
        textTab.addEventListener('shown.bs.tab', function() {
            document.getElementById('texto_direto').focus();
        });
    }
});

// Função para copiar resposta (usada no resultado.html)
function copiarResposta() {
    const resposta = document.querySelector('.bg-light p').textContent;
    navigator.clipboard.writeText(resposta).then(function() {
        // Feedback visual
        const btn = event.target;
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check me-2"></i>Copiado!';
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-success');
        
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-primary');
        }, 2000);
    }).catch(function(err) {
        alert('Erro ao copiar: ' + err);
    });
}

// Loading state no formulário
function mostrarLoading() {
    const btn = document.querySelector('button[type="submit"]');
    if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';
        btn.disabled = true;
    }
}

// Adiciona loading ao formulário
const form = document.querySelector('form');
if (form) {
    form.addEventListener('submit', mostrarLoading);
}