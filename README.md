# Brasileiro | Consultare

Aplicativo Streamlit independente do Colab e do Google Drive.

## Publicação no GitHub e Streamlit

1. Extraia o ZIP no computador. Crie no GitHub um repositório **privado**, por exemplo `brasileiro-consultare`.
2. Envie o CONTEÚDO da pasta extraída para a raiz do repositório, preservando `dados`, `Fotos` e `.streamlit`. O arquivo `app.py` deve ficar na raiz. Não envie apenas o ZIP.
3. Confira no GitHub os arquivos `app.py`, `rede.py`, `requirements.txt`, `dados/Atletas_Tabelas_Atualizadas.xlsx` e as 11 fotos em `Fotos`.
4. Entre em https://share.streamlit.io/ e use **Create app**, escolhendo seu repositório privado, a branch utilizada (normalmente `main`) e `app.py` como arquivo principal. Nas opções avançadas, selecione Python 3.12.
5. Configure/confirme a privacidade do aplicativo como **privado**, antes de compartilhar o endereço, e cadastre apenas os espectadores autorizados. A privacidade do repositório e a do aplicativo são configurações distintas.
6. Use **Deploy**. Alterações posteriores no código e nos arquivos devem ser enviadas ao mesmo repositório.

O pacote contém nomes, fotos e planos das atletas. Seu conteúdo é destinado ao repositório privado. Não há autenticação própria dentro do código: a restrição de acesso deve ser feita no Streamlit Community Cloud. Não publique este pacote como aplicativo público.

Documentação: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy e https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app

## Dados já incluídos

- `dados/Atletas_Tabelas_Atualizadas.xlsx`: 11 atletas; aba `atletas_planos` lida preferencialmente.
- `Fotos`: 11 retratos e logotipo recebido. A associação segue os nomes de arquivo do cadastro, sem reconhecimento facial.
- Nomes e campos NI preservados como na fonte. NI aparece como Não informado na interface.

## Rede de hospitais

A base de hospitais não foi fornecida e nenhum hospital foi inventado. A consulta permanece com mensagem de base ausente até sua inclusão.

Adicione `dados/hospitais_goiania_planos.xlsx`, de preferência com aba `Hospitais_Planos`, ou `dados/hospitais_goiania_planos.csv`. Também é possível enviar a base pela barra lateral para teste.

Colunas obrigatórias: `hospital`, `operadora`, `plano`, `endereco`. Opcionais: `telefone`, `latitude`, `longitude`. Há um modelo vazio em `dados/modelo_hospitais.csv`; preencha e salve com o nome acima. Telefones devem ser texto, preservando DDD e zeros.

Operadora e plano precisam corresponder exatamente aos do cadastro após remover diferenças de maiúsculas, acentos e espaços. O sistema não infere equivalências como AMS e AMS - Assistência Multidisciplinar de Saúde. Padronize apenas após confirmar a equivalência na fonte.

Os uploads da barra lateral valem somente para a sessão, não gravam nem atualizam o GitHub. Atualizações permanentes exigem substituir o arquivo no repositório.

## Teste local

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Validação realizada

Sintaxe Python, conteúdo do XLSX, existência das 11 fotos e regras de associação de operadora/plano verificadas. A publicação na conta do usuário e o teste visual completo no Streamlit Cloud ainda precisam ser feitos.
