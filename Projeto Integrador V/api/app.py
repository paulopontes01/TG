# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from pathlib import Path

# 1. Inicialização da aplicação FastAPI
app = FastAPI(
    title="API de Predição de Sucesso Comercial - Inteligência Imobiliária",
    description="API do PI5 (Fatec Votorantim) para avaliação de probabilidade de fechamento/liquidez de imóveis.",
    version="1.1"
)

# 2. Configuração de Middleware CORS (Resolve o erro 404 em requisições OPTIONS/POST)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Localização e carregamento do modelo serializado
DIR_ATUAL = Path(__file__).resolve().parent
RAIZ_PROJETO = DIR_ATUAL.parent

MODEL_PATH = RAIZ_PROJETO / "models" / "modelo_liquidez.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = DIR_ATUAL / "models" / "modelo_liquidez.joblib"

if not MODEL_PATH.exists():
    raise RuntimeError(f"Ficheiro do modelo não encontrado em {MODEL_PATH}. Execute export_model.py primeiro.")

model = joblib.load(MODEL_PATH)

# 4. Schema/Contrato de dados de entrada
class ImovelEntrada(BaseModel):
    valor_anuncio: float = Field(..., description="Valor do anúncio em R$", json_schema_extra={"example": 2200.0})
    dormitorios: int = Field(default=2, description="Quantidade de dormitórios", json_schema_extra={"example": 2})
    banheiros: int = Field(default=1, description="Quantidade de banheiros", json_schema_extra={"example": 1})
    garagens: int = Field(default=1, description="Vagas de garagem", json_schema_extra={"example": 1})
    tipo: str = Field(..., description="Tipo de imóvel", json_schema_extra={"example": "Apartamento"})
    bairro: str = Field(..., description="Bairro de localização", json_schema_extra={"example": "Jardim Vera Cruz"})

@app.get("/")
def home():
    return {
        "status": "online",
        "projeto": "PI 5 - Inteligência de Liquidez para Imobiliárias",
        "docs": "Consulte a rota /docs para a especificação OpenAPI/Swagger"
    }

# 5. Rota oficial de inferência
@app.post("/predict")
def predizer_sucesso(dados: ImovelEntrada):
    try:
        input_dict = dados.model_dump() if hasattr(dados, 'model_dump') else dados.dict()
        df_input = pd.DataFrame([input_dict])

        # Probabilidade calculada pela regressão logística
        probabilidade = float(model.predict_proba(df_input)[0, 1])
        previsao_binaria = int(probabilidade >= 0.5)

        # Regras de recomendação operacional baseadas no score
        if probabilidade >= 0.65:
            categoria = "Alta Liquidez"
            recomendacao = "Priorizar atendimento no WhatsApp, destacar no portal e agendar visitas com rapidez."
        elif probabilidade >= 0.40:
            categoria = "Média Liquidez"
            recomendacao = "Monitorar volume de contatos nos primeiros 15 dias e manter captação ativa."
        else:
            categoria = "Baixa Liquidez"
            recomendacao = "Revisar precificação com o proprietário ou reavaliar o pacote de custos (condomínio/IPTU)."

        return {
            "sucesso_estimado": bool(previsao_binaria),
            "probabilidade_sucesso": round(probabilidade, 4),
            "categoria_liquidez": categoria,
            "recomendacao_operacional": recomendacao
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)