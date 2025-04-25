import os
import PyPDF2
import pytesseract
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API da OpenAI não está configurada.")
client = OpenAI(api_key=api_key)


def extrair_regras(pdf_path):
    print(f"Extraindo regras de {pdf_path}...")
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            texto = ""
            for page_num in range(5, min(8, len(reader.pages))):
                texto += reader.pages[page_num].extract_text() or ""
        print(f"Texto extraído do PDF: {texto[:100] if texto else 'Vazio'}...")
        return texto.strip()
    except Exception as e:
        print(f"Erro ao extrair regras: {str(e)}")
        raise Exception(f"Erro ao extrair regras do PDF: {str(e)}")


def extrair_texto_imagem(imagem_path):
    print(f"Extraindo texto de {imagem_path}...")
    try:
        imagem = Image.open(imagem_path)
        texto = pytesseract.image_to_string(imagem, lang="por")
        print(f"Texto extraído da imagem: {texto[:100] if texto else 'Vazio'}...")
        return texto.strip()
    except Exception as e:
        print(f"Erro ao extrair texto da imagem: {str(e)}")
        raise Exception(f"Erro ao extrair texto da imagem: {str(e)}")


def resumir_texto(texto):
    print(f"Enviando texto para resumo na OpenAI: {texto[:100]}...")
    try:
        prompt = f"Resuma o seguinte texto em até 100 palavras, mantendo as informações principais:\n\n{texto}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que resume textos de forma clara e concisa.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.5,
        )
        resumo = response.choices[0].message.content.strip()
        print(f"Resumo recebido: {resumo}")
        return resumo
    except requests.exceptions.ConnectionError as e:
        print(f"Erro de conexão com a OpenAI: {str(e)}")
        raise Exception(f"Erro de conexão com a OpenAI: {str(e)}")
    except Exception as e:
        print(f"Erro ao resumir texto: {str(e)}")
        raise Exception(f"Erro ao resumir texto: {str(e)}")


def analisar_preenchimento(regras_resumidas, texto_documento_resumido):
    print(f"Analisando preenchimento com OpenAI...")
    print(f"Regras: {regras_resumidas[:100]}...")
    print(f"Texto da guia: {texto_documento_resumido[:100]}...")
    try:
        prompt = (
            f"Compare as seguintes regras com o texto da guia preenchida e identifique pontos de conformidade e não conformidade. "
            f"Retorne apenas uma lista de pontos de não conformidade e uma lista de pontos de conformidade, no formato:\n"
            f"Pontos de não conformidade:\n- [Ponto 1]\n- [Ponto 2]\n...\n"
            f"Pontos de conformidade:\n- [Ponto 1]\n- [Ponto 2]\n...\n"
            f"Se não houver pontos, escreva 'Nenhum ponto de não conformidade identificado' ou 'Nenhum ponto de conformidade identificado'.\n\n"
            f"Regras:\n{regras_resumidas}\n\n"
            f"Texto da guia:\n{texto_documento_resumido}"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que analisa conformidade de documentos e retorna respostas no formato especificado.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.5,
        )
        resultado = response.choices[0].message.content.strip()
        print(f"Resultado da análise: {resultado}")
        return resultado
    except requests.exceptions.ConnectionError as e:
        print(f"Erro de conexão com a OpenAI: {str(e)}")
        raise Exception(f"Erro de conexão com a OpenAI: {str(e)}")
    except Exception as e:
        print(f"Erro ao analisar preenchimento: {str(e)}")
        raise Exception(f"Erro ao analisar preenchimento: {str(e)}")
