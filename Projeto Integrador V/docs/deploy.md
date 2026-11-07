# Lima Imóveis no Render

## Arquivos válidos e diferenças

A implementação deste repositório PIV é a fonte válida, conforme orientação do usuário. Usa `api/app.py`, `api/index.html` e `models/modelo_liquidez.joblib`. O artefato é um Pipeline direto, com imputação, padronização, OneHotEncoder e regressão logística. Não é o dicionário com `pipeline` e `feature_config` do projeto anterior. Não houve retreinamento nem substituição do modelo.

Os seis campos são `valor_anuncio`, `dormitorios`, `banheiros`, `garagens`, `tipo` e `bairro`. O artefato registra scikit-learn 1.9.1, fixado em requirements.txt. Os demais pins de pandas, NumPy e joblib foram aproveitados do projeto anterior; este repositório não informa suas versões originais de treino. Validar scores verifica o transporte HTTP, não substitui uma avaliação estatística.

O HTML original foi mantido, com fetch na mesma origem, aviso de uso exploratório e validação do valor positivo. Métricas no HTML são as informadas originalmente: não há relatório de avaliação associado no deploy. A única rota de previsão é `/api/predict`. Nenhuma base, credencial ou arquivo .env foi importado. O exportador histórico `api/export_model.py` fica fora do container.

## Executar

Python 3.13:

```bash
python -m pip install -r requirements-api.txt
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Docker:

```bash
docker build -t lima-imoveis .
docker run --rm -p 8000:8000 -e PORT=8000 lima-imoveis
```

Abra http://localhost:8000. O container usa usuário sem privilégios, carrega o modelo sem retreino e inclui apenas API, HTML, dependências e JOBLIB. O processo escuta em 0.0.0.0 na porta definida por PORT.

- `GET /`: front HTML com CSS/JS embutidos.
- `GET /health`: prontidão, após carregamento e inferência inicial do modelo.
- `GET /api/model`: campos e categorias do pipeline; métricas indisponíveis retornam null.
- `POST /api/predict`: probabilidade, classe, categoria, recomendação e aviso.
- `GET /docs`: documentação interativa.

```bash
curl http://localhost:8000/api/predict -H 'Content-Type: application/json' -d '{"valor_anuncio":2200,"dormitorios":2,"banheiros":1,"garagens":1,"tipo":"Apartamento","bairro":"Centro"}'
```

Prioridades originais: alta ≥ 65%, média ≥ 40%, baixa < 40%; classe positiva ≥ 50%. O score serve para priorização exploratória, sem garantir fechamento. Nenhum cadastro é persistido.

## Testar

```bash
python -m pip install httpx==0.28.1
python -m unittest discover -s tests -v
```

Testes usam exemplos sintéticos: comparam scores HTTP com o pipeline carregado independentemente, validam entradas, front, metadados e prontidão. Não requerem bases locais.

## Publicar pelo Blueprint

1. Faça commit e push dos arquivos para `paulopontes01/PIV`, incluindo o JOBLIB já existente. Escolha a branch que contém `render.yaml`.
2. No [painel Render](https://dashboard.render.com), clique **New > Blueprint**.
3. Conecte o GitHub e autorize acesso ao repositório privado `paulopontes01/PIV`. A autenticação do gh local não conecta a conta GitHub ao Render automaticamente.
4. Selecione o repositório, a branch e o caminho `render.yaml` na raiz.
5. Revise um único Web Service chamado `lima-imoveis`, runtime Docker, plano **Free**, health check `/health`. Não são necessários segredos, banco de dados ou disco.
6. Clique **Deploy Blueprint**. O Render constrói a imagem e inicia o serviço. O deploy automático de código está desativado (`autoDeployTrigger: off`); a criação inicial faz o primeiro deploy.
7. Quando estiver Live, abra a URL HTTPS gerada. Confira `/health`, `/docs`, `/api/model` e faça uma simulação pelo formulário.
8. Para atualizar código, faça push e use **Manual Deploy > Deploy latest commit** no serviço. Mudanças no Blueprint também têm o fluxo próprio de sincronização do Render.

O serviço Free hiberna após 15 minutos sem tráfego; a próxima requisição pode levar cerca de um minuto para ativá-lo. Há 750 horas gratuitas por workspace/mês compartilhadas entre serviços. Consulte os limites atuais da conta. Esta aplicação pública é destinada a demonstração e uso exploratório.

Fontes oficiais: [Blueprints](https://render.com/docs/infrastructure-as-code), [campos do YAML](https://render.com/docs/blueprint-spec), [plano gratuito](https://render.com/docs/free).
