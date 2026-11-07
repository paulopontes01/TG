# export_model.py
import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

# Identifica a raiz do projeto (uma pasta acima de 'api/')
DIR_ATUAL = Path(__file__).resolve().parent
RAIZ_PROJETO = DIR_ATUAL.parent

# 1. Carregar dados limpos
# Procura imoveis.csv na raiz do projeto ou na pasta local
arquivo_csv = RAIZ_PROJETO / "imoveis.csv"
if not arquivo_csv.exists():
    arquivo_csv = DIR_ATUAL / "imoveis.csv"
    if not arquivo_csv.exists():
        arquivo_csv = RAIZ_PROJETO / "data/raw/imoveis.csv"

if not arquivo_csv.exists():
    raise FileNotFoundError(f"Arquivo de dados não encontrado em {arquivo_csv}")

base = pd.read_csv(arquivo_csv, sep=";", encoding="cp1252", dtype=str)
for col in ["Referência", "Finalidade", "Disponibilidade"]:
    base[col] = base[col].str.strip().replace("", np.nan)

# Filtra locação e referências válidas
dados = base.loc[base.Finalidade.eq("Locação") & base["Referência"].notna()].copy()
dados = dados.drop_duplicates(subset=["Referência"])
dados["sucesso"] = dados.Disponibilidade.isin(["Alugado", "Vendido"]).astype(int)

# Tratamento das features numéricas e categóricas
preco = dados.Valor.str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.strip()
dados["valor_anuncio"] = pd.to_numeric(preco, errors="coerce")
dados["dormitorios"] = pd.to_numeric(dados["Características"].str.extract(r"(\d+)\s+dormitório", expand=False), errors="coerce")
dados["banheiros"] = pd.to_numeric(dados["Características"].str.extract(r"(\d+)\s+banheiro", expand=False), errors="coerce")
dados["garagens"] = pd.to_numeric(dados["Características"].str.extract(r"(\d+)\s+garage", expand=False), errors="coerce")
dados["tipo"] = dados["Tipo"].fillna("Outro").str.strip()
dados["bairro"] = dados["Bairro"].fillna("Outro").str.strip()

features = ["valor_anuncio", "dormitorios", "banheiros", "garagens", "tipo", "bairro"]
X = dados[features]
y = dados["sucesso"]

# 2. Pipeline completo de pré-processamento e classificação
preparacao = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), ["valor_anuncio", "dormitorios", "banheiros", "garagens"]),
    ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=2), ["tipo", "bairro"])
])

pipeline = Pipeline([
    ("preparacao", preparacao),
    ("classificador", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
])

# 3. Treinar e salvar o modelo na pasta models/ da raiz
pipeline.fit(X, y)
pasta_models = RAIZ_PROJETO / "models"
pasta_models.mkdir(exist_ok=True)

caminho_modelo = pasta_models / "modelo_liquidez.joblib"
joblib.dump(pipeline, caminho_modelo)
print(f"Modelo serializado com sucesso em: {caminho_modelo}")