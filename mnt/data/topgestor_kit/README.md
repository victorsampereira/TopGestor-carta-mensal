# Kit de Gráficos e Tabelas – Carta Mensal (Top Gestor)

Este kit cria **tabelas e gráficos** no estilo da carta mensal da Safra Asset (tabela de performance, atribuição de performance e evolução da rentabilidade).
Você só precisa **preencher os CSVs da pasta `inputs/`** e rodar o script `gera_graficos_tabelas.py` (ou executar o notebook que preferir com o mesmo código).

> Observação: os gráficos são gerados com **matplotlib** (sem seaborn), **um gráfico por figura** e **sem definir cores específicas**, conforme solicitado.

## Passo a passo

1. **Preencha os arquivos de entrada (CSVs) na pasta `inputs/`:**

   - `nav_diario.csv` — série diária do fundo e do CDI:
     ```csv
     date,nav_fundo,cdi_diario
     2025-07-01,1000.00,0.00055
     2025-07-02,1001.50,0.00055
     ...
     ```
     - `date`: formato `AAAA-MM-DD`
     - `nav_fundo`: valor da cota do fundo
     - `cdi_diario`: taxa do CDI do dia (por exemplo, 0,00055 = 0,055%)

   - `pnl_atribuicao_diario.csv` — P&L diário por **bucket** (em % do PL, pode usar bps/10000 ou diretamente em % do PL):
     ```csv
     date,renda_variavel,renda_fixa,moedas,commodities,outros,despesas,caixa
     2025-08-01,0.03,0.12,-0.01,0.00,0.00,-0.02,0.00
     ...
     ```

   - `acoes_rentab_mensal.csv` — rentabilidade **mensal (%)** de fundos de ações “ativos” (linhas no gráfico):
     ```csv
     data,EquityPortfolioSpecial,AcoesLivre,EquityPortfolio,Selection,SmallCap,Bancos
     2025-01,2.10,1.9,2.0,1.2,3.0,1.5
     ...
     ```

   - `setoriais_rentab_mensal.csv` — rentabilidade **mensal (%)** de fundos de ações “setoriais”:
     ```csv
     data,Exportacao,Infraestrutura,Consumo,BDR_Nivel_I,Consumo_Americano,Arquimedes
     2025-01,1.0,2.3,1.1,-0.5,-0.7,0.9
     ...
     ```

   - `indices_rentab_mensal.csv` — índices de referência:
     ```csv
     data,Ibovespa,IPCA
     2025-01,6.08,0.63
     ...
     ```

2. **Edite o arquivo `config.json`:**
   ```json
   {
     "fund_name": "Engenheiras da Bolsa MM",
     "start_date": "2024-08-01",
     "pl_medio": 150000000
   }
   ```

3. **Rode o script:**
   ```bash
   python gera_graficos_tabelas.py
   ```

4. **Saídas na pasta `outputs/`:**
   - `tabela_performance.xlsx` — tabela com **Fundo, CDI, %CDI e Vol*** para: Mês, Ano (YTD), 12m, 24m, 36m e Início.
   - `atribuicao_mes.png` — gráfico de barras com **Atribuição de Performance** do mês (Renda Variável, Renda Fixa, Moedas, Commodities, Outros, Despesas, Caixa).
   - `evolucao_acoes_ativos.png` — linhas com **evolução de fundos de ações ativos**.
   - `evolucao_acoes_setoriais.png` — linhas com **evolução de fundos setoriais**.
   - `indices_evolucao.png` — linhas com **Índices – Evolução (%)** (ex.: Ibovespa e IPCA).

## Definições e fórmulas (sugestão)

- **Retorno do fundo no período**: retorno geométrico a partir das cotas diárias.
- **Retorno do CDI no período**: acumular as taxas diárias (1 + cdi_diario) do período e subtrair 1.
- **%CDI**: `(retorno_fundo / retorno_cdi) * 100`.
- **Vol***: volatilidade anualizada de retornos diários do fundo no **último ano**: `stdev(ret_diarios) * sqrt(252)`.
- **YTD (Ano)**: do primeiro dia útil do ano até a última data disponível.
- **12m/24m/36m**: janelas móveis (use o histórico disponível).

> Dica: Caso você prefira **Excel/Sheets**:
> - Retorno diário: `=COTA_HOJE/COTA_ONTEM - 1`
> - Vol anualizada: `=DESVPAD.S(retornos_diarios)*RAIZ(252)`
> - Acúmulo no período (mensal, YTD): `=PRODUTO(1+faixa_de_retornos) - 1`
> - %CDI: `=retorno_fundo / retorno_CDI * 100`

---

## Observação sobre estilo dos gráficos
- Um gráfico por figura.
- Sem definir cores específicas (usar padrão do matplotlib).
- Títulos e rótulos objetivos, eixos com percentuais quando pertinente.

Bom trabalho e bons resultados no Top Gestor! ⚑
