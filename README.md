# 🚀 Classificador Inteligente de Emails

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**Solução de IA para classificação automática de emails em Produtivo ou Improdutivo**

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![Deploy on Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

</div>

## 📋 Sobre o Projeto

Sistema desenvolvido para **automatizar a leitura e classificação de emails** utilizando Inteligência Artificial. A solução categoriza emails automaticamente e sugere respostas adequadas, otimizando o tempo da equipe.

### 🎯 Funcionalidades Principais

- ✅ **Classificação Automática**: Identifica se emails são **Produtivos** ou **Improdutivos**
- 🤖 **IA Avançada**: Utiliza Google Gemini para análise contextual precisa
- 📧 **Respostas Sugeridas**: Gera respostas automáticas baseadas na categoria
- 📁 **Multi-formatos**: Suporte a texto direto, PDF, TXT, DOC e DOCX
- 🌐 **Web Interface**: Interface moderna e responsiva
- 🚀 **API REST**: Endpoint para integração com outros sistemas

## 🏗️ Arquitetura do Sistema

```mermaid
graph TB
    A[Interface Web] --> B[Flask Backend]
    B --> C[Processamento de Texto]
    C --> D[Google Gemini AI]
    D --> E[Classificação]
    E --> F[Geração de Resposta]
    F --> G[Resultado]