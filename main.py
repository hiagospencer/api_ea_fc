from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import os

app = FastAPI()

# Local onde o arquivo Excel será salvo temporariamente
UPLOAD_DIRECTORY = "uploaded_files"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    # Verifica se o arquivo é um Excel
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Somente arquivos Excel são permitidos.")

    # Define o caminho onde o arquivo será salvo
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

    # Salva o arquivo no servidor
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Carrega o arquivo Excel com o Pandas
    df = pd.read_excel(file_location)

    return {
        "filename": file.filename,
        "columns": df.columns.tolist(),
        "data": df.to_dict(orient='records')  # Mostra as primeiras linhas para verificação
    }

@app.get("/data/")
def read_excel():
    # Verifica se há algum arquivo Excel na pasta
    files = [f for f in os.listdir(UPLOAD_DIRECTORY) if f.endswith('.xlsx')]
    if not files:
        raise HTTPException(status_code=404, detail="Nenhum arquivo foi carregado ainda.")

    # Lê o arquivo Excel mais recente (pode modificar para ler um específico)
    file_path = os.path.join(UPLOAD_DIRECTORY, files[0])
    df = pd.read_excel(file_path)

    return df.to_dict(orient='records')

@app.get("/data/columns/{column_name}")
def get_column_data(column_name: str):
    # Verifica se há algum arquivo Excel na pasta
    files = [f for f in os.listdir(UPLOAD_DIRECTORY) if f.endswith('.xlsx')]
    if not files:
        raise HTTPException(status_code=404, detail="Nenhum arquivo foi carregado ainda.")

    # Lê o arquivo Excel mais recente (pode modificar para ler um específico)
    file_path = os.path.join(UPLOAD_DIRECTORY, files[0])
    df = pd.read_excel(file_path)

    if column_name not in df.columns:
        raise HTTPException(status_code=404, detail=f"A coluna {column_name} não foi encontrada.")

    return df[column_name].to_list()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
