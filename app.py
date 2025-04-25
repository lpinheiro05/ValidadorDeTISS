from dotenv import load_dotenv
import os
from flask import Flask, request, render_template, jsonify
from scripts.agente_ocr import (
    extrair_regras,
    extrair_texto_imagem,
    resumir_texto,
    analisar_preenchimento,
)

load_dotenv()
print("Iniciando o script app.py...")

app = Flask(__name__)
print("Flask app criada.")

UPLOAD_FOLDER = "Uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
print("Pasta de uploads configurada.")


@app.route("/")
def index():
    print("Acessando a rota /")
    return render_template("index.html")


@app.route("/processar", methods=["POST"])
def processar():
    print("Acessando a rota /processar")
    try:
        if "pdf" not in request.files or "imagem" not in request.files:
            print("Erro: Arquivos PDF ou imagem não enviados")
            return jsonify(
                {"error": "Por favor, envie ambos os arquivos (PDF e imagem)."}
            ), 400

        pdf_file = request.files["pdf"]
        imagem_file = request.files["imagem"]
        print(
            f"Arquivos recebidos: PDF={pdf_file.filename}, Imagem={imagem_file.filename}"
        )

        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file.filename)
        imagem_path = os.path.join(app.config["UPLOAD_FOLDER"], imagem_file.filename)
        print(f"Salvando arquivos: PDF={pdf_path}, Imagem={imagem_path}")
        pdf_file.save(pdf_path)
        imagem_file.save(imagem_path)

        print("Extraindo regras do PDF...")
        regras = extrair_regras(pdf_path)
        print(f"Regras extraídas: {regras[:100] if regras else 'Vazio'}...")

        print("Extraindo texto da imagem...")
        texto_documento = extrair_texto_imagem(imagem_path)
        print(
            f"Texto da imagem extraído: {texto_documento[:100] if texto_documento else 'Vazio'}..."
        )

        print("Resumindo regras...")
        regras_resumidas = resumir_texto(regras)
        print(f"Regras resumidas: {regras_resumidas}")

        print("Resumindo texto da imagem...")
        texto_documento_resumido = resumir_texto(texto_documento)
        print(f"Texto da imagem resumido: {texto_documento_resumido}")

        print("Analisando preenchimento...")
        resultado = analisar_preenchimento(regras_resumidas, texto_documento_resumido)
        print(f"Resultado da análise: {resultado}")

        print("Removendo arquivos temporários...")
        os.remove(pdf_path)
        os.remove(imagem_path)

        print("Enviando resposta ao frontend...")
        return jsonify({"resultado": resultado})

    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
        return jsonify({"error": f"Erro ao processar: {str(e)}"}), 500


if __name__ == "__main__":
    print("Iniciando o servidor Flask...")
    app.run(debug=True, port=5002)
