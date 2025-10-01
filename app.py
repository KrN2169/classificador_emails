import os
import pdfplumber
import google.generativeai as genai
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import re
import logging
from datetime import datetime

# Configuração
load_dotenv()

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Google Gemini
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    try:
        genai.configure(api_key=google_api_key)
        logger.info("✅ Google Gemini configurado!")
        GEMINI_AVAILABLE = True
    except Exception as e:
        logger.error(f"❌ Erro ao configurar Gemini: {e}")
        GEMINI_AVAILABLE = False
else:
    logger.warning("⚠️ GOOGLE_API_KEY não encontrada - usando modo local")
    GEMINI_AVAILABLE = False

def preprocessar_texto(texto):
    """Pré-processamento do texto para análise"""
    # Limpeza básica
    texto = re.sub(r'\s+', ' ', texto)  # Remove espaços múltiplos
    texto = re.sub(r'[^\w\s@.,!?;-]', '', texto)  # Mantém caracteres comuns em emails
    return texto.strip()

def classificar_email_gemini(texto):
    """Classifica email usando Google Gemini"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        ANALISE ESTE EMAIL E CLASSIFIQUE EM APENAS UMA DESTAS CATEGORIAS:

        CATEGORIAS:
        - PRODUTIVO: Emails que requerem ação ou resposta específica (solicitações de suporte, dúvidas sobre sistema, atualizações de casos)
        - IMPRODUTIVO: Emails que não necessitam ação imediata (mensagens sociais, felicitações, agradecimentos genéricos)

        REGRAS:
        - Se o email pede informação, solicita ação ou relata problema → PRODUTIVO
        - Se é apenas mensagem social sem solicitação → IMPRODUTIVO
        - Responda APENAS com "PRODUTIVO" ou "IMPRODUTIVO"

        TEXTO DO EMAIL:
        {texto[:3000]}

        CLASSIFICAÇÃO:
        """
        
        response = model.generate_content(prompt)
        classificacao = response.text.strip().upper()
        
        # Garantir que a resposta esteja no formato correto
        if "PRODUTIVO" in classificacao:
            return "PRODUTIVO"
        elif "IMPRODUTIVO" in classificacao:
            return "IMPRODUTIVO"
        else:
            return classificar_email_local(texto)  # Fallback
            
    except Exception as e:
        logger.error(f"Erro Gemini na classificação: {e}")
        return classificar_email_local(texto)

def gerar_resposta_gemini(texto, categoria):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if categoria == "PRODUTIVO":
            prompt = f"""
            Gere uma resposta profissional e útil para este email PRODUTIVO.
            A resposta deve ser em português, direta e oferecer ajuda concreta.
            
            EMAIL ORIGINAL:
            {texto[:2000]}
            
            RESPOSTA SUGERIDA (máximo 100 palavras):
            """
        else:  # IMPRODUTIVO
            prompt = f"""
            Gere uma resposta educada e breve para este email IMPRODUTIVO.
            A resposta deve ser agradável mas não incentivar continuidade desnecessária.
            
            EMAIL ORIGINAL:
            {texto[:2000]}
            
            RESPOSTA SUGERIDA (máximo 50 palavras):
            """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Erro Gemini na geração de resposta: {e}")
        return gerar_resposta_local(categoria)

def classificar_email_local(texto):
    """Classificação local baseada em palavras-chave"""
    texto_lower = texto.lower()
    
    # Palavras-chave para emails produtivos
    palavras_produtivas = [
        'problema', 'erro', 'ajuda', 'suporte', 'solicitação', 'pedido',
        'urgente', 'importante', 'dúvida', 'questão', 'assunto', 'caso',
        'cliente', 'contrato', 'fatura', 'pagamento', 'suporte técnico',
        'não funciona', 'como fazer', 'preciso de ajuda', 'resolver'
    ]
    
    # Palavras-chave para emails improdutivos  
    palavras_improdutivas = [
        'obrigado', 'obrigada', 'grato', 'gratidão', 'parabéns', 'feliz',
        'natal', 'ano novo', 'feriado', 'final de semana', 'cumprimentos',
        'saudações', 'olá', 'oi', 'tudo bem', 'como vai', 'espero que'
    ]
    
    contagem_produtivo = sum(1 for palavra in palavras_produtivas if palavra in texto_lower)
    contagem_improdutivo = sum(1 for palavra in palavras_improdutivas if palavra in texto_lower)
    
    # Lógica de classificação
    if contagem_produtivo > contagem_improdutivo:
        return "PRODUTIVO"
    elif contagem_improdutivo > contagem_produtivo:
        return "IMPRODUTIVO"
    else:
        # Empate - analisa estrutura
        if any(indicador in texto_lower for indicador in ['?', 'problema', 'ajuda', 'suporte']):
            return "PRODUTIVO"
        else:
            return "IMPRODUTIVO"

def gerar_resposta_local(categoria):
    """Gera resposta local baseada na categoria"""
    if categoria == "PRODUTIVO":
        return """Agradecemos seu contato. Nossa equipe analisará sua solicitação e retornará em breve. 
        
Caso necessário, você pode acompanhar o status através do nosso sistema ou entrar em contato pelo telefone (XX) XXXX-XXXX."""
    else:
        return """Agradecemos sua mensagem! Estamos sempre à disposição para ajudar quando necessário."""

def extrair_texto_arquivo(arquivo):
    """Extrai texto de arquivos PDF ou TXT"""
    if arquivo.filename.lower().endswith('.pdf'):
        with pdfplumber.open(arquivo) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() or ""
        return texto
    elif arquivo.filename.lower().endswith('.txt'):
        return arquivo.read().decode('utf-8')
    else:
        raise ValueError("Formato não suportado")

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_email():
    try:
        # Obter o texto do email
        texto_email = ""
        
        if 'arquivo' in request.files and request.files['arquivo'].filename:
            arquivo = request.files['arquivo']
            texto_email = extrair_texto_arquivo(arquivo)
        elif 'texto_direto' in request.form and request.form['texto_direto'].strip():
            texto_email = request.form['texto_direto']
        else:
            return render_template('index.html', erro="Por favor, insira um texto ou selecione um arquivo.")
        
        if not texto_email.strip():
            return render_template('index.html', erro="Não foi possível extrair texto do arquivo.")
        
        # Pré-processamento
        texto_processado = preprocessar_texto(texto_email)
        
        # Classificação
        if GEMINI_AVAILABLE:
            categoria = classificar_email_gemini(texto_processado)
            resposta = gerar_resposta_gemini(texto_processado, categoria)
        else:
            categoria = classificar_email_local(texto_processado)
            resposta = gerar_resposta_local(categoria)
        
        # Log da análise
        logger.info(f"Email processado - Categoria: {categoria}, Tamanho: {len(texto_processado)}")
        
        return render_template('resultado.html', 
                             categoria=categoria,
                             resposta=resposta,
                             texto_original=texto_processado[:500] + "..." if len(texto_processado) > 500 else texto_processado,
                             usando_ia=GEMINI_AVAILABLE)
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return render_template('index.html', erro=f"Erro ao processar: {str(e)}")

@app.route('/api/classificar', methods=['POST'])
def api_classificar():
    """API para integração"""
    data = request.json
    texto = data.get('texto', '')
    
    if GEMINI_AVAILABLE:
        categoria = classificar_email_gemini(texto)
        resposta = gerar_resposta_gemini(texto, categoria)
    else:
        categoria = classificar_email_local(texto)
        resposta = gerar_resposta_local(categoria)
    
    return jsonify({
        'categoria': categoria,
        'resposta_sugerida': resposta,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
