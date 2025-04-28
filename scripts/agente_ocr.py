import PyPDF2
from PIL import Image
import pytesseract
import re
import nltk
from nltk.corpus import stopwords

# Baixar stopwords do NLTK (execute uma vez)
nltk.download("stopwords")
stop_words = set(stopwords.words("portuguese"))


def extrair_regras(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() or ""
        print(f"Texto extraído do PDF: {texto[:200]}...")  # Log para depuração
        return texto
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")


def analisar_imagem(imagem_path):
    try:
        imagem = Image.open(imagem_path)
        texto = pytesseract.image_to_string(imagem, lang="por")
        print(f"Texto extraído da imagem: {texto[:200]}...")  # Log para depuração
        return texto
    except Exception as e:
        raise Exception(f"Erro ao analisar imagem: {str(e)}")


def resumir_texto(texto):
    try:
        # Resumo simples: manter até 500 caracteres
        return texto[:500] + "..." if len(texto) > 500 else texto
    except Exception as e:
        raise Exception(f"Erro ao resumir texto: {str(e)}")


def analisar_preenchimento(regras, texto_documento):
    try:
        # Converter textos para minúsculas
        regras = regras.lower()
        texto_documento = texto_documento.lower()

        # Definir palavras-chave relevantes (exemplo baseado no domínio TISS/Unimed)
        palavras_chave_relevantes = [
            "tiss",
            "unimed",
            "ans",
            "guia",
            "preenchimento",
            "padrão",
            "data",
            "nome",
            "código",
            "autorização",
            "procedimento",
        ]

        # Extrair palavras do PDF, filtrando stopwords
        palavras_pdf = [
            word
            for word in re.findall(r"\w+", regras)
            if word in palavras_chave_relevantes and word not in stop_words
        ]

        # Definir regras específicas para validação (exemplo)
        regras_validacao = {
            "tiss": {
                "descricao": "Código TISS deve estar presente",
                "regex": r"\b\d{4}-\d{2}-\d{2}\b",  # Exemplo: código TISS no formato 1234-56-78
                "obrigatório": True,
            },
            "data": {
                "descricao": "Data no formato DD/MM/AAAA",
                "regex": r"\b\d{2}/\d{2}/\d{4}\b",
                "obrigatório": True,
            },
            "nome": {
                "descricao": "Nome do paciente deve estar presente",
                "regex": r"\b[a-zA-Z\s]+?\b",  # Simplificado, pode ser ajustado
                "obrigatório": True,
            },
            "unimed": {
                "descricao": "Referência à Unimed deve estar presente",
                "regex": r"\bunimed\b",
                "obrigatório": False,
            },
        }

        conformidades = []
        nao_conformidades = []

        # Validar cada regra
        for campo, info in regras_validacao.items():
            match = re.search(info["regex"], texto_documento)
            if match:
                conformidades.append(
                    f"Conformidade: {info['descricao']} ({match.group()})"
                )
            elif info["obrigatório"]:
                nao_conformidades.append(f"Não conformidade: {info['descricao']}")

        # Verificar palavras-chave adicionais
        for palavra in palavras_pdf:
            if palavra not in regras_validacao and palavra in texto_documento:
                conformidades.append(
                    f"Conformidade: '{palavra}' encontrada no documento"
                )
            elif palavra not in regras_validacao:
                nao_conformidades.append(
                    f"Não conformidade: '{palavra}' não encontrada no documento"
                )

        # Montar resultado
        resultado = "Pontos de não conformidade:\n"
        resultado += (
            "\n".join([f"- {item}" for item in nao_conformidades])
            if nao_conformidades
            else "Nenhum ponto de não conformidade identificado"
        )
        resultado += "\n\nPontos de conformidade:\n"
        resultado += (
            "\n".join([f"- {item}" for item in conformidades])
            if conformidades
            else "Nenhum ponto de conformidade identificado"
        )

        print(f"Resultado da análise: {resultado}")  # Log para depuração
        return resultado

    except Exception as e:
        raise Exception(f"Erro ao analisar preenchimento: {str(e)}")
