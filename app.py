from dotenv import load_dotenv
import os
from flask import Flask, request, render_template, jsonify
from scripts.agente_ocr import (
    extrair_regras,
    analisar_imagem,
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

# Caminho do PDF estático
PDF_REGRAS_PATH = os.path.join("static", "regras.pdf")
print(f"PDF estático configurado: {PDF_REGRAS_PATH}")


@app.route("/")
def index():
    print("Acessando a rota /")
    return render_template("index.html")


@app.route("/processar", methods=["POST"])
def processar():
    print("Acessando a rota /processar")
    try:
        if "imagem" not in request.files:
            print("Erro: Arquivo de imagem não enviado")
            return jsonify({"error": "Por favor, envie o arquivo de imagem."}), 400

        imagem_file = request.files["imagem"]
        print(f"Arquivo recebido: Imagem={imagem_file.filename}")

        imagem_path = os.path.join(app.config["UPLOAD_FOLDER"], imagem_file.filename)
        print(f"Salvando arquivo: Imagem={imagem_path}")
        imagem_file.save(imagem_path)

        print("Extraindo regras do PDF estático...")
        regras = extrair_regras(PDF_REGRAS_PATH)
        print(f"Regras extraídas: {regras[:100] if regras else 'Vazio'}...")

        print("Analisando imagem...")
        texto_documento_resumido = analisar_imagem(imagem_path)
        print(
            f"Texto da imagem resumido: {texto_documento_resumido[:100] if texto_documento_resumido else 'Vazio'}..."
        )

        print("Resumindo regras...")
        regras_resumidas = resumir_texto(regras)
        print(f"Regras resumidas: {regras_resumidas}")

        print("Analisando preenchimento...")
        resultado = analisar_preenchimento(regras_resumidas, texto_documento_resumido)
        print(f"Resultado da análise: {resultado}")

        print("Removendo arquivo temporário...")
        os.remove(imagem_path)

        print("Enviando resposta ao frontend...")
        return jsonify({"resultado": resultado})

    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
        return jsonify({"error": f"Erro ao processar: {str(e)}"}), 500


if __name__ == "__main__":
    print("Iniciando o servidor Flask...")
    app.run(debug=True, host="0.0.0.0", port=5002)
